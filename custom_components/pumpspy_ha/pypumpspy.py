"""Python package to talk to Pumpspy API"""

import asyncio
import logging
import aiohttp
from datetime import date

AUTH_USERNAME = "IOS"
AUTH_PASSWORD = "secret"

# LIST OF ENDPOINTS
BASE_URL = "http://www.pumpspy.com:8081"
TOKEN_URL = "/oauth/token"
UID_URL = "/users/email/"
LOCATIONS_URL = "/locations/uid/"
DEVICES_URL = "/devices/lid/"
CURRENT_URL = "/bbs/deviceid/"
DEVICEINFO_URL = "devices/deviceid"
DAILY_URL = "/bbs_cycles/deviceid/<DEVICEID>/motor/ac/interval/day"

LOG = logging.getLogger(__name__)

device_types = {
    2: {
        "endpoint": "pump_outlets",
        "interval_endpoint": "pump_outlet",
        "has_backup": False,
    },
    3: {"endpoint": "bbs", "interval_endpoint": "bbs", "has_backup": True},
    4: {
        "endpoint": "rht_outlets",
        "interval_endpoint": "rht_outlet",
        "has_backup": False,
    },
    5: {
        "endpoint": "rht_outlets",
        "interval_endpoint": "rht_outlet",
        "has_backup": False,
    },
    6: {
        "endpoint": "rht_outlets",
        "interval_endpoint": "rht_outlet",
        "has_backup": False,
    },
}


class Pumpspy:
    """Python class to talk to Pumpspy API"""

    def __init__(self, username, password, device_id=None, iddevice_type=None) -> None:
        """Initialize."""
        self.username = username
        self.password = password
        self.device_name = None
        self.device_id = device_id
        self.iddevice_type = iddevice_type
        self.access_token = None
        self.uid = None
        self.lid = None

    async def setup(self) -> None:
        """Setup the class with access token and user id"""
        await self.get_token()
        async with aiohttp.ClientSession(headers=self.authed_headers()) as session:
            await self.get_uid(session=session)
            if self.device_id is not None:

                # need to get the device type info so we know which endpoint to query
                device_info = await self.get_device_info_from_id(session=session)
                self.iddevice_type = device_info[0]["iddevice_types"]
                self.device_name = device_info[0]["device_types_name"]

                # init_data = await self.fetch_current_data(session=session)
                # LOG.debug("Got device nickname of %s", init_data[0]["user_nickname"])
                # self.device_name = init_data[0]["user_nickname"]

    async def get_token(self) -> None:
        """Get bearer token"""

        # GET TOKEN
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
        }

        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.post(
                        f"{BASE_URL}{TOKEN_URL}",
                        auth=aiohttp.BasicAuth(AUTH_USERNAME, AUTH_PASSWORD),
                        headers=headers,
                        data=data,
                    ) as resp:
                        if resp.status == 200:
                            response = await resp.json()
                            access_token = response["access_token"]
                            LOG.debug("Got an access token of %s", access_token)
                            self.access_token = access_token
                        else:
                            LOG.error(
                                "Error getting authorization: %s", await resp.text()
                            )
                            return None
                        break
                except (
                    aiohttp.ServerDisconnectedError,
                    aiohttp.ClientResponseError,
                    aiohttp.ClientConnectorError,
                ) as err:
                    LOG.debug("Oops, the server connection was dropped: %s", err)
                    await asyncio.sleep(1)  # don't hammer the server

    async def get_uid(self, session: aiohttp.ClientSession) -> None:  # GET UID
        """Get the uid of the user"""

        # async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(
                    f"{BASE_URL}{UID_URL}{self.username}", headers=self.authed_headers()
                ) as resp:
                    response = await resp.json()
                    if resp.status == 200:
                        uid = response[0]["uid"]
                        LOG.debug("Got uid: %s", uid)
                        self.uid = uid
                        return
                    elif resp.status == 401 and response["error"] == "invalid_token":
                        raise InvalidAccessToken
                    else:
                        LOG.error("Error getting user id: %s", await resp.text())
                        return None

            except (
                aiohttp.ServerDisconnectedError,
                aiohttp.ClientResponseError,
                aiohttp.ClientConnectorError,
            ) as err:
                LOG.debug("Oops, the server connection was dropped: %s", err)
                await asyncio.sleep(1)  # don't hammer the server

    async def get_locations(self):
        """Get the available locations"""
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.get(
                        f"{BASE_URL}{LOCATIONS_URL}{self.uid}",
                        headers=self.authed_headers(),
                    ) as resp:
                        response = await resp.json()
                        if resp.status == 200:
                            LOG.debug("Got locations: %s", await resp.text())
                            return response
                        elif (
                            resp.status == 401 and response["error"] == "invalid_token"
                        ):
                            raise InvalidAccessToken
                        else:
                            LOG.error("Error getting locations: %s", await resp.text())
                            return None

                except (
                    aiohttp.ServerDisconnectedError,
                    aiohttp.ClientResponseError,
                    aiohttp.ClientConnectorError,
                ) as err:
                    LOG.debug("Oops, the server connection was dropped: %s", err)
                    await asyncio.sleep(1)  # don't hammer the server

    async def get_devices(self):
        """Get the available devices"""
        async with aiohttp.ClientSession() as session:
            while True:
                try:
                    async with session.get(
                        f"{BASE_URL}{DEVICES_URL}{self.lid}",
                        headers=self.authed_headers(),
                    ) as resp:
                        response = await resp.json()
                        if resp.status == 200:
                            LOG.debug("Got devices: %s", await resp.text())
                            return response
                        elif (
                            resp.status == 401 and response["error"] == "invalid_token"
                        ):
                            raise InvalidAccessToken
                        else:
                            LOG.error("Error getting devices: %s", await resp.text())
                            return None
                except (
                    aiohttp.ServerDisconnectedError,
                    aiohttp.ClientResponseError,
                    aiohttp.ClientConnectorError,
                ) as err:
                    LOG.debug("Oops, the server connection was dropped: %s", err)
                    await asyncio.sleep(1)  # don't hammer the server

    async def get_device_info_from_id(self, session: aiohttp.ClientSession):
        """Get the device info"""
        # async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(
                    f"{BASE_URL}/{DEVICEINFO_URL}/{self.device_id}",
                    headers=self.authed_headers(),
                ) as resp:
                    response = await resp.json()
                    if resp.status == 200:
                        LOG.debug("Got device info: %s", await resp.text())
                        return response
                    elif resp.status == 401 and response["error"] == "invalid_token":
                        raise InvalidAccessToken
                    else:
                        LOG.error("Error getting device info: %s", await resp.text())
                        return None
            except (
                aiohttp.ServerDisconnectedError,
                aiohttp.ClientResponseError,
                aiohttp.ClientConnectorError,
            ) as err:
                LOG.debug("Oops, the server connection was dropped: %s", err)
                await asyncio.sleep(1)  # don't hammer the server

    def set_location(self, lid):
        """Setter for location id"""
        self.lid = lid

    def get_device_info(self):
        """Getter for device id"""
        return {"deviceid": self.device_id, "device_name": self.device_name}

    def has_backup(self):
        """Check if the device has a backup pump"""
        if self.iddevice_type is None:
            return False
        return device_types[self.iddevice_type]["has_backup"]

    async def fetch_data(self, intervals):
        """Get all the data from the API"""
        async with aiohttp.ClientSession(headers=self.authed_headers()) as session:
            data = {"current": None, "ac": {}, "dc": {}}
            while True:
                try:
                    data["current"] = await self.fetch_current_data(session=session)

                    for interval in intervals:
                        data["ac"][interval] = await self.fetch_interval_data(
                            session=session, motor="ac", interval=interval
                        )
                        if self.has_backup() is True:
                            data["dc"][interval] = await self.fetch_interval_data(
                                session=session, motor="dc", interval=interval
                            )
                    LOG.debug(data)
                    return data
                except InvalidAccessToken:
                    await self.get_token()
                    await asyncio.sleep(1)  # don't hammer the server
                    break

                except (
                    aiohttp.ServerDisconnectedError,
                    aiohttp.ClientResponseError,
                    aiohttp.ClientConnectorError,
                ) as err:
                    LOG.debug("Oops, the server connection was dropped: %s", err)
                    await asyncio.sleep(1)  # don't hammer the server

    async def fetch_current_data(self, session: aiohttp.ClientSession):
        """Get the current data"""
        updated_url = f"{BASE_URL}/{device_types[self.iddevice_type]['endpoint']}/deviceid/{self.device_id}"
        LOG.debug("Querying api: %s", updated_url)
        async with session.get(updated_url) as resp:
            response = await resp.json()
            if resp.status == 200:
                return response
            elif resp.status == 401 and response["error"] == "invalid_token":
                raise InvalidAccessToken
            else:
                LOG.error("Error fetching current data: %s", await resp.text())
                return None

    async def fetch_interval_data(
        self, session: aiohttp.ClientSession, motor: str, interval: str
    ):
        """
        Get the interval data.
        motor = "ac" for main, "dc" for backup
        interval = "day", "month", "week"
        """
        updated_url = f"{BASE_URL}/{device_types[self.iddevice_type]['interval_endpoint']}_cycles/deviceid/{self.device_id}"
        if self.has_backup() is True:
            updated_url = f"{updated_url}/motor/{motor}"
        updated_url = f"{updated_url}/interval/{interval}"
        LOG.debug("Querying api: %s", updated_url)
        async with session.get(updated_url) as resp:
            response = await resp.json()
            if resp.status == 200:
                return response
            elif resp.status == 401 and response["error"] == "invalid_token":
                raise InvalidAccessToken
            else:
                LOG.error("Error fetching current data: %s", await resp.text())
                return None

    def authed_headers(self):
        "Return headers with bearer token"
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }


class InvalidAccessToken(Exception):
    """Class excpetion for expired"""

    LOG.debug("Expired access token found on %s", date.today())
