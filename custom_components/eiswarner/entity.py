import logging
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)


class EiswarnerEntity(Entity):
    def __init__(self):
        self._state = None
        self._code = None
        self._left = None
        self._city = None
        self._date = None

    @property
    def name(self):
        return "Eiswarner"

    @property
    def state(self):
        return self._state

    @property
    def status_code(self):
        return self._code

    @property
    def calls_left(self):
        return self._left

    @property
    def forecast_city(self):
        return self._city

    @property
    def forecast_date(self):
        return self._date
