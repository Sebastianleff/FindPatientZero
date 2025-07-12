"""Tests for classes in the City module."""

import unittest
from unittest.mock import patch

from findpatientzero.engine.entities.city import City, CityState


class TestCity(unittest.TestCase):
    def setUp(self):
        self.city = City()
        self.city.add_state(CityState())

    def test_city_name(self):
        self.assertIsInstance(self.city.name, str)
        self.assertNotIn(self.city.name, self.city.names)

    def test_city_state(self):
        self.assertIsInstance(self.city.state, CityState)

    def test_city_alerted(self):
        self.assertIsInstance(self.city.alerted, bool)
        self.assertFalse(self.city.alerted)

    def test_city_infection_stage(self):
        self.assertIsInstance(self.city.infection_stage, int)
        self.assertEqual(self.city.infection_stage, 0)

    def test_city_conditions(self):
        self.assertIsInstance(self.city.conditions, list)
        self.assertEqual(len(self.city.conditions), 0)

    def test_city_in_lockdown(self):
        self.assertIsInstance(self.city.in_lockdown, bool)
        self.assertFalse(self.city.in_lockdown)

    def test_city_can_roll_suspicious(self):
        round = 5
        suspicious_cooldown = 2
        self.city.state.last_sus_roll = 4
        self.assertEqual(self.city.state.last_sus_roll, 4)
        self.assertIsInstance(self.city.can_roll_suspicious(round, suspicious_cooldown), bool)
        self.assertFalse(self.city.can_roll_suspicious(round, suspicious_cooldown))
        self.city.state.last_sus_roll = 2
        self.assertTrue(self.city.can_roll_suspicious(round, suspicious_cooldown))
        self.city.state.alerted = True
        self.assertFalse(self.city.can_roll_suspicious(round, suspicious_cooldown))

    def test_city_survey(self):
        current_state = CityState(infection_stage=0)
        advantage = True
        self.assertIsInstance(self.city.survey(current_state, advantage), bool)
        self.assertFalse(self.city.survey(current_state, advantage))

        current_state = CityState(infection_stage=9)
        with patch("findpatientzero.engine.entities.city.randint", return_value=56):
            self.assertFalse(self.city.survey(current_state, False))

        with patch("findpatientzero.engine.entities.city.randint", return_value=54):
            self.assertTrue(self.city.survey(current_state, False))

        current_state = CityState(infection_stage=11)
        self.assertTrue(self.city.survey(current_state, advantage))

    def test_city_add_state(self):
        state = CityState(infection_stage=2)
        self.city.add_state(state)
        self.assertEqual(len(self.city._history), 2)
        self.assertEqual(self.city.state, state)

if __name__ == "__main__":
    unittest.main()
