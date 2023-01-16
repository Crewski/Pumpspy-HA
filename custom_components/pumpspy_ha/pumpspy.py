from homeassistant.const import (
    CONF_ACCESS_TOKEN,
    CONF_PASSWORD,
    CONF_USERNAME,
    CONTENT_TYPE_JSON,
)
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client
from .const import (
    AUTHORIZATION_HEADER,
    BASE_URL,
    CONF_DEVICE_NAME,
    CONF_DEVICEID,
    CONF_REFRESH_TOKEN,
    CURRENT_URL,
    DEVICES_URL,
    LOCATIONS_URL,
    TOKEN_URL,
    UID_URL,
)


class Pumpspy:
    """Placeholder class to make tests pass.

    TODO Remove this placeholder class and replace with things from your PyPI package.
    """

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize."""
        self.hass = hass
        self.username = None
        self.password = None
        self.access_token = None
        self.refresh_token = None
        self.deviceid = None
        self.device_name = None

    async def get_token(self) -> None:
        """Get bearer token"""

        # GET TOKEN
        headers = {
            "Authorization": AUTHORIZATION_HEADER,
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": CONF_PASSWORD,
            CONF_USERNAME: self.username,
            CONF_PASSWORD: self.password,
        }
        session = aiohttp_client.async_get_clientsession(self.hass)
        async with session.post(
            f"{BASE_URL}{TOKEN_URL}", headers=headers, data=data
        ) as resp:
            if resp.status == 200:
                response = await resp.json()
                self.access_token = response[CONF_ACCESS_TOKEN]
                self.refresh_token = response[CONF_REFRESH_TOKEN]
            else:
                print(await resp.json())
                raise InvalidAuth
        return

    async def get_uid(self) -> None:  # GET UID
        """Get the uid of the user"""

        session = aiohttp_client.async_get_clientsession(self.hass)
        async with session.get(
            f"{BASE_URL}{UID_URL}{self.username}", headers=self.authed_headers()
        ) as resp:
            if resp.status == 200:
                response = await resp.json()
                return response[0]["uid"]
            else:
                print(await resp.json())
                raise InvalidAuth

    async def get_locations(self, username: str, password: str):
        """Get the available locations"""
        self.username = username
        self.password = password
        await self.get_token()
        uid = await self.get_uid()
        session = aiohttp_client.async_get_clientsession(self.hass)
        async with session.get(
            f"{BASE_URL}{LOCATIONS_URL}{uid}", headers=self.authed_headers()
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                raise InvalidAuth

    async def get_devices(self, lid):
        """Get the available devices"""
        session = aiohttp_client.async_get_clientsession(self.hass)
        async with session.get(
            f"{BASE_URL}{DEVICES_URL}{lid}", headers=self.authed_headers()
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            else:
                raise InvalidAuth

    async def fetch_current_data(self):
        """Get the current data"""
        session = aiohttp_client.async_get_clientsession(self.hass)
        async with session.get(
            f"{BASE_URL}{CURRENT_URL}{self.deviceid}", headers=self.authed_headers()
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 401:
                await self.get_token()
                self.fetch_current_data()
            else:
                raise CannotConnect

    async def fetch_interval_data(self, type: str, interval: str):
        """Get the current data"""
        updated_url = (
            f"/bbs_cycles/deviceid/{self.deviceid}/motor/{type}/interval/{interval}"
        )
        session = aiohttp_client.async_get_clientsession(self.hass)
        async with session.get(
            f"{BASE_URL}{updated_url}",
            headers=self.authed_headers(),
        ) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 401:
                await self.get_token()
                self.fetch_current_data()
            else:
                raise CannotConnect

    def set_device_info(self, deviceid, device_name):
        """Setter for device id"""
        self.deviceid = deviceid
        self.device_name = device_name

    def get_device_info(self):
        """Getter for device id"""
        return {CONF_DEVICEID: self.deviceid, CONF_DEVICE_NAME: self.device_name}

    def authed_headers(self):
        "Return headers with bearer token"
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": CONTENT_TYPE_JSON,
        }

    def get_variables(self):
        """Pass variables back to config"""
        return {
            CONF_ACCESS_TOKEN: self.access_token,
            CONF_REFRESH_TOKEN: self.refresh_token,
            CONF_DEVICEID: self.deviceid,
            CONF_USERNAME: self.username,
            CONF_DEVICE_NAME: self.device_name,
            CONF_PASSWORD: self.password,
        }

    def set_variables(
        self,
        access_token: str,
        refresh_token: str,
        deviceid,
        username: str,
        device_name: str,
        password: str,
    ):
        """Set all the variables for a new instance"""
        self.username = username
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.deviceid = deviceid
        self.device_name = device_name
        self.password = password


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
