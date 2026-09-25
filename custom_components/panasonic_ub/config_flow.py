"""Config flow for Panasonic UB Blu-ray integration."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_MAC, CONF_NAME
from homeassistant.core import callback

from .const import (
    CONF_AUTH_ENABLE,
    CONF_KEY,
    CONF_POLL_INTERVAL,
    DEFAULT_NAME,
    DEFAULT_POLL_INTERVAL,
    DEFAULT_SECRET_KEY,
    DOMAIN,
)


class PanasonicUBConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Panasonic UB."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return PanasonicUBOptionsFlowHandler()

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        errors = {}

        if user_input is not None:
            auth_enabled = user_input.get(CONF_AUTH_ENABLE, True)
            raw_key = (user_input.get(CONF_KEY) or "").strip()
            invalid_key = len(raw_key) not in (0, 32) or (
                auth_enabled and (len(raw_key) != 32 or raw_key == DEFAULT_SECRET_KEY)
            )
            if invalid_key:
                errors["base"] = "invalid_key"
            else:
                data = {**user_input, CONF_KEY: raw_key or DEFAULT_SECRET_KEY}
                return self.async_create_entry(
                    title=data.get(CONF_NAME, DEFAULT_NAME), data=data
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_MAC): str,
                vol.Optional(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Optional(CONF_KEY): str,
                vol.Optional(CONF_AUTH_ENABLE, default=True): bool,
                vol.Optional(CONF_POLL_INTERVAL, default=DEFAULT_POLL_INTERVAL): int,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"device_name": "Panasonic Player"},
        )


class PanasonicUBOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for the integration."""

    # FIX: __init__ removed.
    # self.config_entry is automatically populated by Home Assistant before async_step_init is called.

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        errors = {}

        if user_input is not None:
            auth_enabled = user_input.get(CONF_AUTH_ENABLE, True)
            raw_key = (user_input.get(CONF_KEY) or "").strip()
            invalid_key = len(raw_key) not in (0, 32) or (
                auth_enabled and (len(raw_key) != 32 or raw_key == DEFAULT_SECRET_KEY)
            )
            if invalid_key:
                errors["base"] = "invalid_key"
            else:
                # When options are saved, update the main config entry data.
                data = {**user_input, CONF_KEY: raw_key or DEFAULT_SECRET_KEY}
                self.hass.config_entries.async_update_entry(
                    self.config_entry,
                    data=data,
                )
                return self.async_create_entry(title="", data={})

        # Load current values from the config entry
        current_data = self.config_entry.data

        # Build schema with current values as defaults
        options_schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=current_data.get(CONF_HOST)): str,
                vol.Optional(CONF_MAC, default=current_data.get(CONF_MAC)): str,
                vol.Optional(
                    CONF_NAME, default=current_data.get(CONF_NAME, DEFAULT_NAME)
                ): str,
                vol.Optional(
                    CONF_KEY, default=current_data.get(CONF_KEY, "")
                ): str,
                vol.Optional(
                    CONF_AUTH_ENABLE, default=current_data.get(CONF_AUTH_ENABLE, True)
                ): bool,
                vol.Optional(
                    CONF_POLL_INTERVAL,
                    default=current_data.get(CONF_POLL_INTERVAL, DEFAULT_POLL_INTERVAL),
                ): int,
            }
        )

        return self.async_show_form(
            step_id="init", data_schema=options_schema, errors=errors
        )
