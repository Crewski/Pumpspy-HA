# Pumpspy-HA
Pumpspy-HA is a custom integration for [Home Assistant](https://www.home-assistant.io/) to pull in data from Pumpspy and Pitboss+ sump pump monitoring devices.



# Installation

## HACS (preferred)
Add the respository URL as a custom [repository integration](https://hacs.xyz/docs/faq/custom_repositories).

## Manual
Copy the pumpspy_ha folder from this repo to config/custom_components (create custom_components folder if it doesn't exist already)

## Setup
Once Pumpspy-HA is installed, you can set it up by adding it as an integration.  You'll need your username (email) and password.  Depending on how many locations and devices you have, you may be prompted to select them.


# Data
Pumspy-HA polls the Pumpspy server every 5 minutes.  The data should not be considered real time, especially for alerts.

## Supported
- Alerts
- Main/Backup pump cycles and gallons
    - Daily
    - Weekly
    - Monthly
- Battery data
- Connectivity data
- Last cycle data

*many sensors have data in their attributes



# Home Assistant
![Home Assistant](/images/main_lovelace.png)