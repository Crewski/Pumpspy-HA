"""The Pumpspy-HA integration."""
from __future__ import annotations
from datetime import timedelta
import logging
import async_timeout

from homeassistant.helpers.device_registry import DeviceEntry

from .pumpspy import Pumpspy

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_PASSWORD,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

# from homeassistant.exceptions import ConfigEntryAuthFailed


from .const import (
    CONF_DEVICE_NAME,
    CONF_DEVICEID,
    CONF_REFRESH_TOKEN,
    DOMAIN,
    MANUFACTURER,
)

# TODO List the platforms that you want to support.
# For your initial PR, limit it to 1 platform.
PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pumpspy-HA from a config entry."""
    api = Pumpspy(hass)
    api.set_variables(
        entry.data[CONF_ACCESS_TOKEN],
        entry.data[CONF_REFRESH_TOKEN],
        entry.data[CONF_DEVICEID],
        entry.data[CONF_USERNAME],
        entry.data[CONF_DEVICE_NAME],
        entry.data[CONF_PASSWORD],
    )
    coordinator = PumpspyCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    return True


class PumpspyCoordinator(DataUpdateCoordinator):
    """Pumpspy coordinator."""

    def __init__(self, hass, api):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name="Pumpspy",
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=300),
        )
        self.api = api

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        try:
            # Note: asyncio.TimeoutError and aiohttp.ClientError are already
            # handled by the data update coordinator.
            data = {}
            async with async_timeout.timeout(30):
                data["current"] = await self.api.fetch_current_data()
            async with async_timeout.timeout(30):
                data["main_daily"] = await self.api.fetch_interval_data("ac", "day")
            async with async_timeout.timeout(30):
                data["backup_daily"] = await self.api.fetch_interval_data("dc", "day")
            async with async_timeout.timeout(30):
                data["main_monthly"] = await self.api.fetch_interval_data("ac", "month")
            async with async_timeout.timeout(30):
                data["backup_monthly"] = await self.api.fetch_interval_data(
                    "dc", "month"
                )
            async with async_timeout.timeout(30):
                data["main_weekly"] = await self.api.fetch_interval_data("ac", "week")
            async with async_timeout.timeout(30):
                data["backup_weekly"] = await self.api.fetch_interval_data("dc", "week")
            return data
        except Exception as err:
            self.logger.error(err)
