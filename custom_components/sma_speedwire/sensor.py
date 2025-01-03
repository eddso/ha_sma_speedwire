"""The sensor entity for the iec6205621 integration."""
from __future__ import annotations
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    UnitOfEnergy.KILO_WATT_HOUR,
    UnitOfPower.WATT,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
# from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from . import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Initialize the integration."""
    coordinator = hass.data[DOMAIN][entry.entry_id]
    device = entry.data[CONF_HOST]
    if (device := entry.data[CONF_HOST]) is None:
        device = entry.entry_id

    entities = []
    for sensor in coordinator.data.sensors:
        _LOGGER.debug("add sensor %s, %s", device, sensor)
        entities.append(SMASensor(coordinator, device, sensor))
    async_add_entities(entities)


class SMASensor(CoordinatorEntity, SensorEntity): 
    """Class for a sensor."""
    def __init__(self, coordinator, device, sensor):
        """Initialize an sensor."""
        super().__init__(coordinator)
        self._sensor = sensor
        self._device = device
        self._attr_unique_id = f"{DOMAIN}_{device}_{sensor}"
        self._attr_name = coordinator.data.sensors[sensor]['name']
        # self._attr_icon = "mdi:flash"
        if coordinator.data.sensors[sensor]['unit'] == 'kWh':
            self._attr_state_class = SensorStateClass.TOTAL_INCREASING
            self._attr_device_class = SensorDeviceClass.ENERGY
            self._attr_native_unit_of_measurement = UnitOfEnergy.KILO_WATT_HOUR
        elif coordinator.data.sensors[sensor]['unit'] == 'W':
            self._attr_state_class = SensorStateClass.MEASUREMENT
            self._attr_device_class = SensorDeviceClass.POWER
            self._attr_native_unit_of_measurement = UnitOfPower.WATT
    
        # https://developers.home-assistant.io/docs/device_registry_index/
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, f"{device}")},
            manufacturer="SMA",
            model=coordinator.data.inv_type,
            name=coordinator.data.inv_type,
            hw_version=coordinator.data.serial,
        )

    @property
    def available(self):
        """Return if entity is available."""
        return self.coordinator.last_update_success

    @property
    def native_value(self):
        """Return the state of the sensor."""
        value = self.coordinator.data.sensors[self._sensor]['value']
        _LOGGER.debug("%s %f", self._sensor, value)

        return value
