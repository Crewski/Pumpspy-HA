"""Constants for the Pumpspy-HA integration."""

from homeassistant.const import DEVICE_CLASS_HUMIDITY


DOMAIN = "pumpspy_ha"
MANUFACTURER = "Pumpspy"

BASE_URL = "http://www.pumpspy.com:8081"
TOKEN_URL = "/oauth/token"
UID_URL = "/users/email/"
LOCATIONS_URL = "/locations/uid/"
DEVICES_URL = "/devices/lid/"
CURRENT_URL = "/bbs/deviceid/"
DAILY_URL = "/bbs_cycles/deviceid/<DEVICEID>/motor/ac/interval/day"
AUTHORIZATION_HEADER = "Basic SU9TOnNlY3JldA=="

CONF_REFRESH_TOKEN = "refresh_token"
CONF_DEVICEID = "deviceid"
CONF_DEVICE_NAME = "device_name"

CONF_GALLONS = "gallons"
CONF_CYCLES = "cycles"
CONF_MAIN_PUMP = "main"
CONF_BACKUP_PUMP = "backup"
CONF_DAILY = "daily"
CONF_MONTHLY = "monthly"
CONF_WEEKLY = "weekly"

ALERT_CONNECTED = "connected"
ALERT_HIGH_WATER = "high_water_alert"
ALERT_AC_POWER_LOSS = "ac_power_loss"
ALERT_EXCESSIVE_CURRENT = "excessive_current"
ALERT_EXCESSIVE_RUN_TIME = "excessive_run_time"
ALERT_BATTERY_CHARGE_LEVEL = "battery_charge_level"
ALERT_BACKUP_EXCESSIVE_RUN_TIME = "backup_excessive_run_time"
ALERT_BACKUP_EXCESSIVE_CURRET = "backup_excessive_current"
ALERT_PRIMARY_PUMP_FAILURE = "primary_pump_failure"
ALERT_BACKUP_PUMP_FAILURE = "backup_pump_failure"
