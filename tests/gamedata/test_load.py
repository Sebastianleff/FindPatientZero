"""Unit tests for the gamedata.load module."""

import unittest
from findpatientzero.gamedata.load import (
    load_city_names,
    load_conditions,
    load_cpu_names,
    load_event_types,
    load_events,
)
from findpatientzero.gamedata.schema import (
    ConditionData,
    EventData,
    EventTypeData,
    NameList,
)

class TestLoad(unittest.TestCase):
    def test_load_city_names(self):
        self.assertIsInstance(load_city_names(), list)

    def test_load_conditions(self):
        self.assertIsInstance(load_conditions("city"), list)
        self.assertIsInstance(load_conditions("traveler"), list)

    def test_load_cpu_names(self):
        self.assertIsInstance(load_cpu_names(), list)

    def test_load_event_types(self):
        self.assertIsInstance(load_event_types("city"), list)
        self.assertIsInstance(load_event_types("traveler"), list)

    def test_load_events(self):
        self.assertIsInstance(load_events("city_suspicious"), list)
        self.assertIsInstance(load_events("city_epidemic"), list)
        self.assertIsInstance(load_events("traveler_healthy"), list)
        self.assertIsInstance(load_events("traveler_infected"), list)

    def test_load_event_types_data(self):
        event_types = load_event_types("city")
        for event_type in event_types:
            self.assertIsInstance(event_type, EventTypeData)

    def test_load_conditions_data(self):
        conditions = load_conditions("city")
        for condition in conditions:
            self.assertIsInstance(condition, ConditionData)

    def test_load_events_data(self):
        events = load_events("city_suspicious")
        for event in events:
            self.assertIsInstance(event, EventData)


if __name__ == "__main__":
    unittest.main()
