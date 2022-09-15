"""Config flow for Pumpspy-HA integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from .pumpspy import Pumpspy
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector

from homeassistant.const import (
    CONF_USERNAME,
    CONF_PASSWORD,
)

from .const import (
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pumpspy-HA."""

    VERSION = 1

    pumpspy: Pumpspy
    locations = None
    devices = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""

        errors = {}
        if user_input is not None:
            self.pumpspy = Pumpspy(self.hass)
            self.locations = await self.pumpspy.get_locations(
                user_input[CONF_USERNAME], user_input[CONF_PASSWORD]
            )
            if self.locations:
                return await self.async_step_location()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )

    async def async_step_location(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Form to select location"""
        errors = {}

        # skip this step if there is only 1 location
        if len(self.locations) == 1:
            self.devices = await self.pumpspy.get_devices(self.locations[0]["lid"])
            if self.devices:
                return await self.async_step_device()

        if user_input is not None:
            self.devices = await self.pumpspy.get_devices(user_input["location"])
            if self.devices:
                return await self.async_step_device()

        options = []
        for location in self.locations:
            options.append(
                selector.SelectOptionDict(
                    value=str(location["lid"]), label=location["nickname"]
                )
            )
        data_schema = vol.Schema(
            {
                vol.Required("location"): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=options)
                )
            }
        )

        return self.async_show_form(
            step_id="location", data_schema=data_schema, errors=errors
        )

    async def async_step_device(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Form to select device"""
        errors = {}

        # skip this step if there is only 1 device
        if len(self.devices) == 1:
            self.pumpspy.set_device_info(
                self.devices[0]["deviceid"], self.devices[0]["device_types_name"]
            )
            await self.async_set_unique_id(self.devices[0]["deviceid"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=f'Pumpspy ({self.devices[0]["device_types_name"]})',
                data=self.pumpspy.get_variables(),
            )

        if user_input is not None:
            await self.async_set_unique_id(user_input["device"])
            self._abort_if_unique_id_configured()
            device_name = next(
                (x for x in self.devices if x.deviceid == user_input["device"]), None
            )
            self.pumpspy.set_device_info(user_input["device"], device_name)
            return self.async_create_entry(
                title=f"Pumpspy ({device_name})", data=self.pumpspy.get_variables()
            )

        options = []
        for device in self.devices:
            options.append(
                selector.SelectOptionDict(
                    value=str(device["deviceid"]), label=device["device_types_name"]
                )
            )
        data_schema = vol.Schema(
            {
                vol.Required("device"): selector.SelectSelector(
                    selector.SelectSelectorConfig(options=options)
                )
            }
        )

        return self.async_show_form(
            step_id="device", data_schema=data_schema, errors=errors
        )
