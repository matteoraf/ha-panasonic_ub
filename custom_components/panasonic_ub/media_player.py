"""Media Player entity for Panasonic UB Blu-ray players."""

from datetime import datetime
import logging

import voluptuous as vol

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_NAME,
    STATE_IDLE,
    STATE_OFF,
    STATE_ON,
    STATE_PAUSED,
    STATE_PLAYING,
    STATE_UNAVAILABLE,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import (
    AddEntitiesCallback,
    async_get_current_platform,
)
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util.dt import utcnow

from .const import COMMAND_MAPPING, DOMAIN, STATUS_MAPPING
from .coordinator import PanasonicUBCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the platform from a ConfigEntry."""
    name = config_entry.data[CONF_NAME]

    # Retrieve the coordinator created in __init__.py
    coordinator: PanasonicUBCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entity = PanasonicBlurayEntity(name, coordinator, config_entry.entry_id)
    async_add_entities([entity], True)

    # Register custom service
    platform = async_get_current_platform()
    platform.async_register_entity_service(
        "remote_command",
        {vol.Required("command"): vol.In(list(COMMAND_MAPPING.keys()))},
        "async_send_custom_command",
    )


class PanasonicBlurayEntity(CoordinatorEntity, MediaPlayerEntity):
    """Representation of a Panasonic Blu-ray Player."""

    def __init__(
        self, name: str, coordinator: PanasonicUBCoordinator, entry_id: str
    ) -> None:
        """Initialize the entity."""
        self._media_position_updated_at: datetime | None = None
        super().__init__(coordinator)
        self._name = name
        self._entry_id = entry_id
        self._attr_unique_id = entry_id

    def _handle_coordinator_update(self) -> None:
        """Record when the reported playback position was refreshed."""
        if self.coordinator.data and self.coordinator.data.get("position") is not None:
            self._media_position_updated_at = utcnow()
        super()._handle_coordinator_update()

    @property
    def name(self) -> str:
        """Return the name of the device."""
        return self._name

    @property
    def state(self) -> str:
        """Return the state of the device based on coordinator data."""
        data = self.coordinator.data
        if not data:
            return STATE_UNAVAILABLE

        status_code = data.get("status_code")

        # Connection failure handling
        if status_code is None:
            return STATE_UNAVAILABLE

        mapped_status = STATUS_MAPPING.get(status_code)

        if mapped_status == "PLAYBACK":
            return STATE_PLAYING
        if mapped_status == "PAUSED":
            return STATE_PAUSED
        if mapped_status in ["STOPPED", "TRAY_OPEN"]:
            return STATE_IDLE
        if mapped_status == "POWER_OFF":
            return STATE_OFF
        if mapped_status in [
            "CUE_PLAYBACK",
            "REV_PLAYBACK",
            "SLOW_FORWARD",
            "SLOW_BACKWARD",
        ]:
            return STATE_PLAYING

        # Fallback for menus
        return STATE_ON

    @property
    def available(self) -> bool:
        """Return if the device is available."""
        # Coordinator data will be None or status_code None if unreachable
        data = self.coordinator.data
        if not data or data.get("status_code") is None:
            return False
        return self.coordinator.last_update_success

    @property
    def media_position(self) -> int | None:
        """Return the current playback position."""
        if self.coordinator.data:
            return self.coordinator.data.get("position")
        return None

    @property
    def media_duration(self) -> int | None:
        """Return the current title duration."""
        if self.coordinator.data:
            return self.coordinator.data.get("duration")
        return None

    @property
    def media_position_updated_at(self) -> datetime | None:
        """Return when the current playback position was refreshed."""
        return self._media_position_updated_at

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Return the supported features."""
        return (
            MediaPlayerEntityFeature.PLAY
            | MediaPlayerEntityFeature.PAUSE
            | MediaPlayerEntityFeature.STOP
            | MediaPlayerEntityFeature.TURN_OFF
            | MediaPlayerEntityFeature.TURN_ON
            | MediaPlayerEntityFeature.PREVIOUS_TRACK
            | MediaPlayerEntityFeature.NEXT_TRACK
            | MediaPlayerEntityFeature.SEEK
        )

    @property
    def extra_state_attributes(self):
        """Return entity specific state attributes."""
        if not self.coordinator.data:
            return {}

        status_code = self.coordinator.data.get("status_code")
        # Get the human readable status from your const.py mapping
        raw_status = STATUS_MAPPING.get(status_code, "Unknown")

        return {
            "status_code": status_code,
            "detailed_status": raw_status,  # e.g., "TRAY_OPEN", "PLAYBACK"
        }

    async def async_turn_on(self) -> None:
        """Turn the device on."""
        # Access the API via the coordinator
        if await self.coordinator.api.turn_on():
            # Optimistic update while waiting for next poll
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self) -> None:
        """Turn the device off."""
        if await self.coordinator.api.send_key("POWER_OFF"):
            # Optimistic update: Set status to Power Off code "07"
            if self.coordinator.data:
                self.coordinator.data["status_code"] = "07"
                self.async_write_ha_state()
            await self.coordinator.async_request_refresh()

    async def async_media_play(self) -> None:
        """Send play command."""
        if not await self.coordinator.api.send_key("PLAY"):
            return

        # Optimistic update: Set status to Playback code "08"
        if self.coordinator.data:
            self.coordinator.data["status_code"] = "08"
            self.async_write_ha_state()

        await self.coordinator.async_request_refresh()

    async def async_media_pause(self) -> None:
        """Send pause command."""
        if not await self.coordinator.api.send_key("PAUSE"):
            return

        # Optimistic update: Set status to Paused code "09"
        if self.coordinator.data:
            self.coordinator.data["status_code"] = "09"
            self.async_write_ha_state()

        await self.coordinator.async_request_refresh()

    async def async_media_stop(self) -> None:
        """Send stop command."""
        if not await self.coordinator.api.send_key("STOP"):
            return

        # Optimistic update: Set status to Stopped code "00"
        if self.coordinator.data:
            self.coordinator.data["status_code"] = "00"
            self.async_write_ha_state()

        await self.coordinator.async_request_refresh()

    async def async_media_previous_track(self) -> None:
        """Send previous track command."""
        await self.coordinator.api.send_key("SKIP_REV")

    async def async_media_next_track(self) -> None:
        """Send next track command."""
        await self.coordinator.api.send_key("SKIP_FWD")

    async def async_send_custom_command(self, command: str) -> None:
        """Send any command via the abstracted API method."""
        await self.coordinator.api.send_key(command)
