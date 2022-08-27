"""The sma_speedwire component."""
from datetime import timedelta
import logging

from .sma_speedwire import SMA_SPEEDWIRE, smaError

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

PLATFORMS = [Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up sma_speedwire from a config entry."""
    api = SMA_SPEEDWIRE(entry.data[CONF_HOST],entry.data[CONF_PASSWORD],_LOGGER)

    try:
        await hass.async_add_executor_job(api.init)
    except (smaError) as exception:
        raise ConfigEntryNotReady from exception

    async def async_update_data():
        """Fetch data from the API."""
        try:
            await hass.async_add_executor_job(api.update)
            return api
        except (smaError) as exception:
            pass

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sma_speedwire",
        update_method=async_update_data,
        update_interval=timedelta(seconds=300),
    )

    # await coordinator.async_config_entry_first_refresh()
    await coordinator.async_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    #hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    # hass version 2022.8+
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
