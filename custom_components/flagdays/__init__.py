import asyncio
import logging

import async_timeout
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.helpers.event import async_call_later
from homeassistant.util import dt as dt_util
from homeassistant.util import slugify

_LOGGER = logging.getLogger(__name__)

CONF_NAME = 'name'
CONF_DATE_OF_FLAG = 'date_of_flag'
CONF_ICON = 'icon'
DOMAIN = 'flagdays'

FLAGDAY_CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Required(CONF_DATE_OF_FLAG): cv.date,
    vol.Optional(CONF_ICON, default='mdi:flag-outline'): cv.string,
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.All(cv.ensure_list, [FLAGDAY_CONFIG_SCHEMA])
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):

    devices = []

    for flagday_data in config[DOMAIN]:
        name = flagday_data[CONF_NAME]
        date_of_flag = flagday_data[CONF_DATE_OF_FLAG]
        icon = flagday_data[CONF_ICON]
        devices.append(FlagdayEntity(name, date_of_flag, icon, hass))

    component = EntityComponent(_LOGGER, DOMAIN, hass)
    await component.async_add_entities(devices)


    tasks = [asyncio.create_task(device.update_data()) for device in devices]
    await asyncio.wait(tasks)

    return True


class FlagdayEntity(Entity):

    def __init__(self, name, date_of_flag, icon, hass):
        self._name = name
        self._date_of_flag = date_of_flag
        self._icon = icon
        self._age_at_next_flagday = 0
        self._state = None
        name_in_entity_id = slugify(name)
        self.entity_id = 'flagday.{}'.format(name_in_entity_id)
        self.hass = hass

    @property
    def name(self):
        return self._name

    @property
    def unique_id(self):
        return '{}.{}'.format(self.entity_id, slugify(self._date_of_flag.strftime("%m%d")))

    @property
    def state(self):
        return self._state

    @property
    def should_poll(self):
        # Do not poll, instead we trigger an asynchronous update every day at midnight
        return False

    @property
    def icon(self):
        return self._icon

    @property
    def extra_state_attributes(self):
        return {
            CONF_DATE_OF_FLAG: str(self._date_of_flag),
            'age_at_next_flagday': self._age_at_next_flagday,
        }

    @property
    def unit_of_measurement(self):
        return 'days'

    @property
    def hidden(self):
        return self._state is None

    def _get_seconds_until_midnight(self):
        one_day_in_seconds = 24 * 60 * 60

        now = dt_util.now()
        total_seconds_passed_today = (now.hour*60*60) + (now.minute*60) + now.second

        return one_day_in_seconds - total_seconds_passed_today

    async def update_data(self, *_):
        from datetime import date, timedelta

        today = dt_util.start_of_local_day().date()
        next_flagday = date(today.year, self._date_of_flag.month, self._date_of_flag.day)

        if next_flagday < today:
            next_flagday = next_flagday.replace(year=today.year + 1)

        days_until_next_flagday = (next_flagday-today).days

        self._age_at_next_flagday = next_flagday.year - self._date_of_flag.year
        self._state = days_until_next_flagday

        if days_until_next_flagday == 0:
            # Fire event if flagday is today
            self.hass.bus.async_fire(event_type='flagday', event_data={'name': self._name, 'age': self._age_at_next_flagday})

        self.async_write_ha_state()
        async_call_later(self.hass, self._get_seconds_until_midnight(), self.update_data)
