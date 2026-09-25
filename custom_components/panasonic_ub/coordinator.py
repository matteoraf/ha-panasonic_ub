"""DataUpdateCoordinator for the Panasonic UB Blu-ray integration."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, STATUS_MAPPING
from .panasonic_api import PanasonicSecureAPI

_LOGGER = logging.getLogger(__name__)


class PanasonicUBCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(
        self, hass: HomeAssistant, api: PanasonicSecureAPI, poll_interval: int
    ) -> None:
        """Initialize."""
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_interval),
        )

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        # 1. Get Status
        status_code, duration = await self.api.get_status_details()

        # If unavailable, return None state (handled by entity)
        if status_code is None:
            return {"status_code": None, "position": None, "duration": None}

        data = {
            "status_code": status_code,
            "position": None,
            "duration": duration,
        }

        # 2. Get Time (if playing)
        mapped_status = STATUS_MAPPING.get(status_code)

        # Check time if we are in a playback state
        if mapped_status in [
            "PLAYBACK",
            "PAUSED",
            "CUE_PLAYBACK",
            "REV_PLAYBACK",
            "SLOW_FORWARD",
            "SLOW_BACKWARD",
        ]:
            data["position"] = await self.api.get_play_position()

        return data
