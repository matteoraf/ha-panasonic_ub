"""API for controlling Panasonic UB Blu-ray players."""

import asyncio
import hashlib
import logging
import socket

import aiohttp

from .const import COMMAND_MAPPING

_LOGGER = logging.getLogger(__name__)


class PanasonicSecureAPI:
    """Interface to communicate with the Panasonic Player."""

    def __init__(
        self,
        host: str,
        secret_key: str,
        session: aiohttp.ClientSession,
        mac_address: str | None = None,
        auth_enabled: bool = True,
    ) -> None:
        """Initialize the API.

        Args:
            host (str): IP address of the player.
            secret_key (str): Secret key for authentication (Must be 32 chars).
            session (aiohttp.ClientSession): The aiohttp session.
            mac_address (str, optional): MAC address for WOL.
            auth_enabled (bool): Whether to use authentication. Defaults to True.

        Raises:
            ValueError: If the secret key is not the correct length (32 characters).

        """
        self._host = host
        self._session = session
        self._mac = mac_address
        self._auth_enabled = auth_enabled

        # Validate Key Length (Strict Check)
        if not secret_key or len(secret_key) != 32:
            raise ValueError(
                f"Invalid Secret Key: Must be 32 characters long. Got {len(secret_key) if secret_key else 0}."
            )

        self._key = secret_key
        # cAUTH_FORM is the first 2 characters of the secret key
        self._auth_form = self._key[:2]

        self._headers = {
            "User-Agent": "MEI-LAN-REMOTE-CALL",
            "Connection": "keep-alive",
        }

    async def _get_nonce(self) -> str | None:
        """Request a random nonce (challenge string) from the device.

        Returns:
            str: The nonce string, or None if connection failed.

        """
        url = f"http://{self._host}/cgi-bin/get_nonce.cgi"
        try:
            async with asyncio.timeout(3):
                resp = await self._session.post(
                    url, data={"SID": "HASS_CTRL"}, headers=self._headers
                )
                resp.raise_for_status()
                nonce = await resp.text()
                return nonce.strip()
        except (TimeoutError, aiohttp.ClientError):
            return None

    def _calculate_auth(self, nonce: str) -> str | None:
        """Generate the SHA-256 signature required for commands.

        Args:
            nonce (str): The challenge string from the device.

        Returns:
            str: The uppercase hex hash signature.

        """
        if not nonce:
            return None
        input_str = self._key + nonce
        return hashlib.sha256(input_str.encode("utf-8")).hexdigest().upper()

    def wake_on_lan(self) -> bool:
        """Send a Magic Packet to wake the device from Eco Standby.

        Returns:
            bool: True if sent, False if MAC is missing or invalid.

        """
        if not self._mac:
            return False

        mac_clean = self._mac.replace(":", "").replace("-", "")
        if len(mac_clean) != 12:
            return False

        try:
            # Magic Packet: 6 bytes of FF followed by 16 repetitions of the MAC
            data = bytes.fromhex("FF" * 6 + mac_clean * 16)

            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.sendto(data, ("255.255.255.255", 9))
        except ValueError:
            _LOGGER.error("Invalid MAC address format: %s", self._mac)
            return False
        except OSError as err:
            _LOGGER.error("Failed to send WOL: %s", err)
            return False
        else:
            return True

    async def send_command(
        self, command_code: str, enable_auth: bool = True
    ) -> str | None:
        """Send a raw command to the player. Handles authentication if enabled.

        Args:
            command_code (str): The internal protocol code (e.g. 'RC_PLAYBACK', 'REVIEW', 'PST').
            enable_auth (bool): Override to disable auth for specific commands (e.g. PST).

        Returns:
            str: The raw response text from the device.
            None: If the connection failed or authentication failed.

        """
        cmd_param = f"cCMD_{command_code}"
        data = {f"{cmd_param}.x": "100", f"{cmd_param}.y": "100"}

        should_auth = self._auth_enabled and enable_auth

        if should_auth:
            nonce = await self._get_nonce()
            if not nonce:
                return None

            auth_key = self._calculate_auth(nonce)
            if auth_key:
                data["cAUTH_FORM"] = self._auth_form
                data["cAUTH_VALUE"] = auth_key

        url = f"http://{self._host}/WAN/dvdr/dvdr_ctrl.cgi"

        try:
            async with asyncio.timeout(4):
                resp = await self._session.post(url, data=data, headers=self._headers)
                if resp.status == 200:
                    response_text = await resp.text()
                    response_lines = [
                        line.strip()
                        for line in response_text.splitlines()
                        if line.strip()
                    ]
                    response_code = (
                        response_lines[0].split(",", 1)[0].strip()
                        if response_lines
                        else None
                    )
                    if response_code != "00":
                        _LOGGER.debug(
                            "Player rejected %s with protocol status %s",
                            command_code,
                            response_code,
                        )
                        return None
                    return response_text
                return None
        except (TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.debug("Error sending command %s: %s", command_code, err)
            return None

    async def send_key(self, key_alias: str) -> bool:
        """Send a command by its convenient alias (e.g., 'PLAY', 'NETFLIX').

        Args:
            key_alias (str): The alias key from COMMAND_MAPPING.

        Returns:
            bool: True if successful, False otherwise.

        """
        code = COMMAND_MAPPING.get(key_alias)
        if not code:
            _LOGGER.error("Unknown key alias: %s", key_alias)
            return False

        result = await self.send_command(code)
        return result is not None

    async def get_status_details(self) -> tuple[str | None, int | None]:
        """Poll the UB status using REVIEW.

        The unauthenticated UB REVIEW response exposes the status code, but
        the time-like field in the response is not the current title's total
        duration. Leave duration unset until a reliable title-duration
        command is available.

        Returns:
            A status code and an unavailable duration.

        """
        response_text = await self.send_command(
            COMMAND_MAPPING["STATUS"], enable_auth=True
        )

        if response_text:
            parts = response_text.split(",")
            if len(parts) > 5:
                return parts[5], None

        return None, None

    async def get_status(self) -> str | None:
        """Poll the device status using REVIEW."""
        status_code, _ = await self.get_status_details()
        return status_code

    async def get_play_position(self) -> int | None:
        """Poll the playback time (PST). Skipped Auth for optimization.

        Returns:
            int: Current time in seconds.
            None: If failed or not playing.

        """
        # PST works without Auth, saving 1 HTTP request per poll
        response_text = await self.send_command(
            COMMAND_MAPPING["TIME"], enable_auth=False
        )

        if response_text:
            parts = response_text.split(",")
            # Format: 00,"",1 1,2077,0,...
            # Index 3 is Current Time.
            if len(parts) >= 4:
                try:
                    return int(parts[3])
                except ValueError:
                    pass

        return None

    async def turn_on(self) -> bool:
        """Turn on the device using WOL (with delay) and HTTP command.

        Returns:
            bool: True if command sent successfully.

        """
        if self.wake_on_lan():
            await asyncio.sleep(2)

        return await self.send_key("POWER_ON")
