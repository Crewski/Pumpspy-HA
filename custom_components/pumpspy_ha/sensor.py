"""Platform for sensor integration."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from collections.abc import Mapping
import pytz

from homeassistant.helpers.typing import StateType
from .entity import PumpspyEntity

# from .pumpspy_ha import PumpspyEntity, pumpspy
from homeassistant.const import (
    PERCENTAGE,
    UnitOfVolume,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.util import dt
from .const import (
    CONF_BACKUP_PUMP,
    CONF_CYCLES,
    CONF_DAILY,
    CONF_DEVICE_NAME,
    CONF_DEVICEID,
    CONF_GALLONS,
    CONF_MAIN_PUMP,
    CONF_MONTHLY,
    CONF_WEEKLY,
    DOMAIN,
)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = [
        SignalStrengthSensor(coordinator=coordinator),
        BatterySensor(coordinator=coordinator),
        TotalingSensor(
            coordinator=coordinator,
            pump=CONF_MAIN_PUMP,
            sensor_type=CONF_CYCLES,
            interval=CONF_DAILY,
        ),
        TotalingSensor(
            coordinator=coordinator,
            pump=CONF_MAIN_PUMP,
            sensor_type=CONF_GALLONS,
            interval=CONF_DAILY,
        ),
        TotalingSensor(
            coordinator=coordinator,
            pump=CONF_BACKUP_PUMP,
            sensor_type=CONF_CYCLES,
            interval=CONF_DAILY,
        ),
        TotalingSensor(
            coordinator=coordinator,
            pump=CONF_BACKUP_PUMP,
            sensor_type=CONF_GALLONS,
            interval=CONF_DAILY,
        ),
        TotalingSensor(
            coordinator=coordinator,
            pump=CONF_MAIN_PUMP,
            sensor_type=CONF_CYCLES,
            interval=CONF_MONTHLY,
        ),
        TotalingSensor(
            coordinator=coordinator,
            pump=CONF_MAIN_PUMP,
            sensor_type=CONF_GALLONS,
            interval=CONF_MONTHLY,
        ),
        TotalingSensor(
            coordinator=coordinator,
            pump=CONF_BACKUP_PUMP,
            sensor_type=CONF_CYCLES,
            interval=CONF_MONTHLY,
        ),
        TotalingSensor(
            coordinator=coordinator,
            pump=CONF_BACKUP_PUMP,
            sensor_type=CONF_GALLONS,
            interval=CONF_MONTHLY,
        ),
        TotalingSensor(
            coordinator=coordinator,
            pump=CONF_MAIN_PUMP,
            sensor_type=CONF_CYCLES,
            interval=CONF_WEEKLY,
        ),
        TotalingSensor(
            coordinator=coordinator,
            pump=CONF_MAIN_PUMP,
            sensor_type=CONF_GALLONS,
            interval=CONF_WEEKLY,
        ),
        TotalingSensor(
            coordinator=coordinator,
            pump=CONF_BACKUP_PUMP,
            sensor_type=CONF_CYCLES,
            interval=CONF_WEEKLY,
        ),
        TotalingSensor(
            coordinator=coordinator,
            pump=CONF_BACKUP_PUMP,
            sensor_type=CONF_GALLONS,
            interval=CONF_WEEKLY,
        ),
        LastCycleSensor(coordinator=coordinator, pump=CONF_MAIN_PUMP),
        LastCycleSensor(coordinator=coordinator, pump=CONF_BACKUP_PUMP),
    ]
    if new_devices:
        async_add_entities(new_devices)


class SignalStrengthSensor(PumpspyEntity, SensorEntity):
    """Signal Strength Sensor"""

    def __init__(self, coordinator) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator)
        self._available = True
        self._attr_native_unit_of_measurement = "dBm"
        self._attr_device_class = SensorDeviceClass.SIGNAL_STRENGTH

        device_info = self.coordinator.api.get_device_info()

        self._attr_unique_id = f"{device_info[CONF_DEVICEID]}_rssi"
        self._attr_name = f"{device_info[CONF_DEVICE_NAME]} RSSI"

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Get value"""
        return self.coordinator.data["current"][0]["last_rssi"]

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return {
            "last_rssi_time": dt.as_utc(
                datetime.fromtimestamp(
                    self.coordinator.data["current"][0]["last_rssi_time"] / 1000,
                    pytz.UTC,
                )
            )
        }


class BatterySensor(PumpspyEntity, SensorEntity):
    """Battery Sensor"""

    def __init__(self, coordinator):
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator)
        self._available = True
        self._attr_native_unit_of_measurement = PERCENTAGE
        self._attr_device_class = SensorDeviceClass.BATTERY

        device_info = self.coordinator.api.get_device_info()

        self._attr_unique_id = f"{device_info[CONF_DEVICEID]}_battery"
        self._attr_name = f"{device_info[CONF_DEVICE_NAME]} Battery"

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        """Native value"""
        return self.coordinator.data["current"][0]["battery_charge_percentage"]

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        """Attributes"""
        return {
            "voltage": self.coordinator.data["current"][0]["battery_voltage"] / 1000,
            "estimated_life": round(
                self.coordinator.data["current"][0]["battery_estimated_life"], 1
            ),
            "tested_time": dt.as_utc(
                datetime.fromtimestamp(
                    self.coordinator.data["current"][0]["battery_tested_time"] / 1000,
                    pytz.UTC,
                )
            ),
            "updated": dt.as_utc(
                datetime.fromtimestamp(
                    self.coordinator.data["current"][0]["battery_updated"] / 1000,
                    pytz.UTC,
                )
            ),
        }


class TotalingSensor(PumpspyEntity, SensorEntity):
    """Totaling Sensor"""

    def __init__(self, coordinator, pump: str, sensor_type: str, interval: str):
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator)
        self._available = True
        self._attr_state_class = SensorStateClass.TOTAL_INCREASING
        self._pump = pump
        self._type = sensor_type
        self._interval = interval
        self._motor = "ac" if pump == CONF_MAIN_PUMP else "dc"

        self._interval_converted = None
        if interval == CONF_DAILY:
            self._interval_converted = "day"
        elif interval == CONF_WEEKLY:
            self._interval_converted = "week"
        elif interval == CONF_MONTHLY:
            self._interval_converted = "month"

        device_info = self.coordinator.api.get_device_info()
        if sensor_type == "gallons":
            self._attr_native_unit_of_measurement = UnitOfVolume.GALLONS

        self._attr_unique_id = (
            f"{device_info[CONF_DEVICEID]}_{pump}_{interval}_{sensor_type}"
        )
        self._attr_name = (
            f"{device_info[CONF_DEVICE_NAME]} {pump} {interval} {sensor_type}".title()
        )

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        try:
            data = self.coordinator.data[self._motor][self._interval_converted][0]
            data_type = "total_count" if self._type == CONF_CYCLES else self._type
            if data["year_num"] != datetime.now().year:
                return 0
            elif (
                self._interval == CONF_WEEKLY
                and data["week_num"] == datetime.now().isocalendar().week
            ):
                return data[data_type]
            elif data["month_num"] == datetime.now().month:
                if (
                    self._interval == CONF_DAILY
                    and data["day_num"] == datetime.now().day
                ):
                    return data[data_type]
                elif self._interval == CONF_MONTHLY:
                    return data[data_type]
                else:
                    return 0
            else:
                return 0
        except Exception:  # pylint: disable=broad-except
            return 0


class LastCycleSensor(PumpspyEntity, SensorEntity):
    """Daily Gallon Sensor"""

    def __init__(self, coordinator, pump: str):
        """Initialize the sensor."""
        super().__init__(coordinator=coordinator)
        self._available = True
        self._pump = pump
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._pre_key = "" if self._pump == CONF_MAIN_PUMP else "backup_"

        device_info = self.coordinator.api.get_device_info()

        self._attr_unique_id = f"{device_info[CONF_DEVICEID]}_{pump}_last_cycle"
        self._attr_name = f"{device_info[CONF_DEVICE_NAME]} {pump.title()} Last Cycle"

    @property
    def native_value(self) -> StateType | date | datetime | Decimal:
        return dt.as_utc(
            datetime.fromtimestamp(
                self.coordinator.data["current"][0][f"{self._pre_key}lastcycletime"]
                / 1000,
                pytz.UTC,
            )
        )

    @property
    def extra_state_attributes(self) -> Mapping[str, Any] | None:
        return {
            "duration": round(
                self.coordinator.data["current"][0][f"{self._pre_key}cycleduration"]
                / 1000,
                1,
            )
        }
