"""Tests for classes in the City module."""

import unittest
from findpatientzero.engine.entities.city import City, CityState


class TestCity(unittest.TestCase):
    def setUp(self):
        self.city = City()

    def test_city_name(self):
        self.assertIsInstance(self.city.name, str)
        self.assertNotIn(self.city.name, self.city.names)

    def test_city_state(self):
        self.assertIsInstance(self.city.state, CityState)

    def test_city_alerted(self):
        self.assertIsInstance(self.city.alerted, bool)

    def test_city_infection_stage(self):
        self.assertIsInstance(self.city.infection_stage, int)

    def test_city_conditions(self):
        self.assertIsInstance(self.city.conditions, list)

    def test_city_in_lockdown(self):
        self.assertIsInstance(self.city.in_lockdown, bool)

    def test_city_can_roll_suspicious(self):
        round = 5
        suspicious_cooldown = 2
        self.assertIsInstance(self.city.can_roll_suspicious(round, suspicious_cooldown), bool)

    def test_city_survey(self):
        current_state = CityState(infection_stage=3)
        advantage = True
        self.assertIsInstance(City.survey(current_state, advantage), bool)

    def test_city_add_state(self):
        state = CityState(infection_stage=2)
        self.city.add_state(state)
        self.assertEqual(len(self.city._history), 2)
        self.assertEqual(self.city.state, state)

if __name__ == "__main__":
    unittest.main()
