"""The Pumpspy-HA integration."""
from __future__ import annotations
from datetime import timedelta
import logging
from homeassistant.helpers import entity_registry

from homeassistant.helpers.device_registry import DeviceEntry

from .pypumpspy import InvalidAccessToken, Pumpspy

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)


from .const import (
    CONF_DEVICEID,
    CONF_MONTHLY,
    CONF_WEEKLY,
    DOMAIN,
)


PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.BINARY_SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pumpspy-HA from a config entry."""
    api: Pumpspy = Pumpspy(
        username=entry.data[CONF_USERNAME],
        password=entry.data[CONF_PASSWORD],
        device_id=entry.data[CONF_DEVICEID],
    )

    if not entry.options:
        await async_update_options(hass, entry)

    await api.setup()
    coordinator = PumpspyCoordinator(
        hass=hass,
        api=api,
        weekly=entry.options.get(CONF_WEEKLY),
        monthly=entry.options.get(CONF_MONTHLY),
    )
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(update_listener))

    return True


async def update_listener(hass: HomeAssistant, config_entry: ConfigEntry):
    """Handle options update."""

    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_update_options(hass: HomeAssistant, config_entry: ConfigEntry):
    """Configure optional sensors"""
    options = {
        CONF_WEEKLY: config_entry.data.get(CONF_WEEKLY, False),
        CONF_MONTHLY: config_entry.data.get(CONF_MONTHLY, False),
    }
    hass.config_entries.async_update_entry(config_entry, options=options)


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    unload_ok = await hass.config_entries.async_unload_platforms(
        config_entry, PLATFORMS
    )

    ent_reg = entity_registry.async_get(hass)
    entity_ids_to_be_removed = []
    if config_entry.options.get(CONF_WEEKLY) is False:
        entity_ids_to_be_removed.extend(
            [
                entry.entity_id
                for entry in ent_reg.entities.values()
                if entry.config_entry_id == config_entry.entry_id
                and CONF_WEEKLY in entry.unique_id
            ]
        )

    if config_entry.options.get(CONF_MONTHLY) is False:
        entity_ids_to_be_removed.extend(
            [
                entry.entity_id
                for entry in ent_reg.entities.values()
                if entry.config_entry_id == config_entry.entry_id
                and CONF_MONTHLY in entry.unique_id
            ]
        )

    _LOGGER.debug("Entities to be removed: %s", entity_ids_to_be_removed)

    for entity_id in entity_ids_to_be_removed:
        if ent_reg.async_is_registered(entity_id):
            ent_reg.async_remove(entity_id)

    if unload_ok:
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    return True


class PumpspyCoordinator(DataUpdateCoordinator):
    """Pumpspy coordinator."""

    def __init__(
        self, hass: HomeAssistant, api: Pumpspy, weekly: bool, monthly: bool
    ) -> None:
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
        self.weekly = weekly
        self.monthly = monthly

        self.intervals = ["day"]
        if weekly:
            self.intervals.append("week")
        if monthly:
            self.intervals.append("month")

    async def _async_update_data(self):
        """Fetch data from API endpoint."""
        # intervals = ["day"]
        # if self.weekly:
        #     intervals.append("week")
        # if self.monthly:
        #     intervals.append("month")
        try:
            return await self.api.fetch_data(intervals=self.intervals)
        except InvalidAccessToken:
            _LOGGER.info("Access token expired, will try again")
        except ConnectionError as err:
            _LOGGER.error(err)
