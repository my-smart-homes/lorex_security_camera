"""The Lorex Security Camera integration."""
from __future__ import annotations

import logging
import aiohttp
import asyncio
from typing import Any
from datetime import timedelta

import voluptuous as vol

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, CONF_HOST, CONF_RTSP_PATH, CONF_USERNAME, CONF_PASSWORD

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Lorex Security Camera from a config entry."""
    config = config_entry.data
    
    # Create coordinator for connection status updates
    coordinator = LorexCoordinator(
        hass,
        host=config[CONF_HOST],
        username=config[CONF_USERNAME],
        password=config[CONF_PASSWORD],
    )
    
    # Start the coordinator
    await coordinator.async_config_entry_first_refresh()
    
    camera = LorexCamera(
        coordinator=coordinator,
        host=config[CONF_HOST],
        rtsp_path=config[CONF_RTSP_PATH],
        username=config[CONF_USERNAME],
        password=config[CONF_PASSWORD],
    )
    async_add_entities([camera])

class LorexCoordinator(DataUpdateCoordinator):
    """Coordinator for Lorex camera connection status."""

    def __init__(
        self,
        hass: HomeAssistant,
        host: str,
        username: str,
        password: str,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Lorex Camera Status",
            update_interval=SCAN_INTERVAL,
        )
        self._host = host
        self._username = username
        self._password = password
        self._is_connected = False

    async def _async_update_data(self) -> bool:
        """Update the connection status."""
        try:
            base_url = f"http://{self._host}"
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    base_url,
                    auth=aiohttp.BasicAuth(self._username, self._password),
                    timeout=10
                ) as response:
                    self._is_connected = response.status == 200
                    return self._is_connected
        except Exception as err:
            _LOGGER.error("Error checking camera connection: %s", err)
            self._is_connected = False
            return False

    @property
    def is_connected(self) -> bool:
        """Return the connection status."""
        return self._is_connected

class LorexCamera(Camera):
    """Representation of a Lorex Security Camera."""

    def __init__(
        self,
        coordinator: LorexCoordinator,
        host: str,
        rtsp_path: str,
        username: str,
        password: str,
    ) -> None:
        """Initialize a Lorex Security Camera."""
        super().__init__()
        self._coordinator = coordinator
        self._host = host
        self._rtsp_path = rtsp_path
        self._username = username
        self._password = password
        self._name = f"Lorex Camera {host}"
        self._stream_source = f"rtsp://rignev:pass2025@03cabcc9-ring-mqtt:8554/649a63ca6a1b_live"

    @property
    def name(self) -> str:
        """Return the name of this camera."""
        return self._name

    @property
    def stream_source(self) -> str:
        """Return the stream source."""
        return self._stream_source

    @property
    def available(self) -> bool:
        """Return True if the camera is available."""
        return self._coordinator.is_connected

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the camera state attributes."""
        return {
            "connection_status": "connected" if self.available else "disconnected",
            "last_update": self._coordinator.last_update_success,
        }

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image response from the camera."""
        # This will be handled by the generic camera platform
        return None
