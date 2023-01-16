"""Platform for binary sensor integration."""
from __future__ import annotations
from typing import Any
from collections.abc import Mapping

from homeassistant.helpers.entity import EntityCategory

from .entity import PumpspyEntity
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from .const import (
    ALERT_AC_POWER_LOSS,
    ALERT_BACKUP_EXCESSIVE_CURRET,
    ALERT_BACKUP_EXCESSIVE_RUN_TIME,
    ALERT_BACKUP_PUMP_FAILURE,
    ALERT_BATTERY_CHARGE_LEVEL,
    ALERT_CONNECTED,
    ALERT_EXCESSIVE_CURRENT,
    ALERT_EXCESSIVE_RUN_TIME,
    ALERT_HIGH_WATER,
    ALERT_PRIMARY_PUMP_FAILURE,
    CONF_DEVICE_NAME,
    CONF_DEVICEID,
    DOMAIN,
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = [
        AlertBinarySensor(coordinator, ALERT_CONNECTED),
        AlertBinarySensor(coordinator, ALERT_HIGH_WATER),
        AlertBinarySensor(coordinator, ALERT_AC_POWER_LOSS),
        AlertBinarySensor(coordinator, ALERT_EXCESSIVE_CURRENT),
        AlertBinarySensor(coordinator, ALERT_EXCESSIVE_RUN_TIME),
        AlertBinarySensor(coordinator, ALERT_BATTERY_CHARGE_LEVEL),
        AlertBinarySensor(coordinator, ALERT_BACKUP_EXCESSIVE_CURRET),
        AlertBinarySensor(coordinator, ALERT_BACKUP_EXCESSIVE_RUN_TIME),
        AlertBinarySensor(coordinator, ALERT_PRIMARY_PUMP_FAILURE),
        AlertBinarySensor(coordinator, ALERT_BACKUP_PUMP_FAILURE),
    ]
    if new_devices:
        async_add_entities(new_devices)


class AlertBinarySensor(PumpspyEntity, BinarySensorEntity):
    """Alert Binary Sensor"""

    def __init__(self, coordinator, alert: str):
        """Initialize the sensor."""
        # super().__init__(coordinator)
        self.coordinator = coordinator
        self.coordinator_context = object()
        self._available = True
        self._alert = alert
        self._attr_device_class = (
            BinarySensorDeviceClass.CONNECTIVITY
            if alert == ALERT_CONNECTED
            else BinarySensorDeviceClass.PROBLEM
        )
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

        device_info = self.coordinator.api.get_device_info()

        self._attr_unique_id = f"{device_info[CONF_DEVICEID]}_{alert}"
        self._attr_name = (
            f'{device_info[CONF_DEVICE_NAME]} {alert.replace("_", " ").title()}'
        )

    # @callback
    # def _handle_coordinator_update(self) -> None:
    #     """Handle updated data from the coordinator."""
    #     if self.coordinator.data is None:
    #         return
    #     val = self.coordinator.data["current"][0][self._alert]["state"]
    #     if self._alert == ALERT_BATTERY_CHARGE_LEVEL:
    #         val = not bool(val)
    #     self._attr_is_on = val
    #     self._attr_extra_state_attributes = {
    #         "message": self.coordinator.data["current"][0][self._alert]["message"]
    #     }
    #     self.async_write_ha_state()

    @property
    def is_on(self) -> bool | None:
        val = self.coordinator.data["current"][0][self._alert]["state"]
        if self._alert == ALERT_BATTERY_CHARGE_LEVEL:
            val = not bool(val)
        return val

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return {"message": self.coordinator.data["current"][0][self._alert]["message"]}
