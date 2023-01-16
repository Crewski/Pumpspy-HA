"""Base Entity for Pumpspy."""
from __future__ import annotations

from homeassistant.helpers.entity import DeviceInfo
from . import PumpspyCoordinator
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .const import DOMAIN, MANUFACTURER


class PumpspyEntity(CoordinatorEntity[PumpspyCoordinator]):
    """Defines a base Pumpspy entity."""

    def __init__(self, *, coordinator: PumpspyCoordinator) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)

    @property
    def device_info(self) -> DeviceInfo | None:
        try:
            return DeviceInfo(
                identifiers={(DOMAIN, self.coordinator.data["current"][0]["deviceid"])},
                name=self.coordinator.data["current"][0]["user_nickname"],
                manufacturer=MANUFACTURER,
                model=self.coordinator.data["current"][0]["device_types_name"],
                hw_version=self.coordinator.data["current"][0]["hardware_rev"],
                sw_version=self.coordinator.data["current"][0]["firmware_rev"],
            )
        except TypeError:
            return None
