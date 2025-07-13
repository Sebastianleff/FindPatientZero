"""Tests for classes in the Player module."""

import unittest
from unittest.mock import patch, PropertyMock

from findpatientzero.engine.entities.city import CityState
from findpatientzero.engine.entities.player import *


class TestPlayer(unittest.TestCase):

    def setUp(self):
        self.player = Player("MacTester")
        self.cities = [City(), City(), City(), City()]
        for city in self.cities:
            city.add_state(CityState())
        self.player_city =  self.cities[0]
        self.dest_city = self.cities[1]
        self.player.add_state(PlayerState(city=self.player_city))

    def test_player_initialization(self):
        """Test that the Player class can be instantiated correctly with the default state."""
        init_state = PlayerState(city=self.player_city)
        self.assertIsInstance(self.player, Player)
        self.assertEqual(self.player.name, "MacTester")
        self.assertIsInstance(self.player.state, PlayerState)
        self.assertEqual(self.player.state, init_state)

    def test_add_state(self):
        """Test that the player can add states"""
        mactester_state = PlayerState(
            health = InfectionState.IMMUNE,
            infected_round=2,
        )
        self.player.add_state(mactester_state)
        self.assertEqual(mactester_state, self.player.state)

    def test_sus(self):
        """Test that the player can prompt for a suspicious event."""
        self.player.prompt_suspicious()
        self.assertTrue(self.player._sus_prompt_pending)
        self.assertIsNone(self.player._sus_prompt_response)

        self.player.respond_suspicious(True)
        self.assertFalse(self.player._sus_prompt_pending)
        self.assertTrue(self.player._sus_prompt_response)

    def test_choice(self):
        self.player.prompt_city_choice()
        self.assertTrue(self.player.pending_city_prompt)
        self.assertIsNone(self.player._city_prompt_response)

        self.player.respond_city_choice(self.dest_city)
        self.assertFalse(self.player.pending_city_prompt)
        self.assertEqual(self.player._city_prompt_response, self.dest_city)

    def test_next_event_category(self):
        """Test that the player can get the next event category."""
        self.assertIsInstance(self.player.next_event_category, EventCategory)
        self.assertEqual(self.player.next_event_category, EventCategory.TRAV_HEALTHY)

        self.player.add_state(PlayerState(health=InfectionState.SYMPTOMATIC))
        self.assertIsInstance(self.player.next_event_category, EventCategory)
        self.assertEqual(self.player.next_event_category, EventCategory.TRAV_INFECTED)

    def test_next_event(self):
        """Test that the player can generate and get the next event."""
        self.player.roll_next_event()
        self.assertIsInstance(self.player.next_event, Event)
        self.assertEqual(self.player.next_event.category, EventCategory.TRAV_HEALTHY)

        self.player.add_state(PlayerState(health=InfectionState.SYMPTOMATIC))
        self.player.roll_next_event()
        self.assertIsInstance(self.player.next_event, Event)
        self.assertEqual(self.player.next_event.category, EventCategory.TRAV_INFECTED)

    def test_can_move_healthy(self):
        """Test that the player can move cities when healthy or infected."""
        self.player.roll_next_event()
        self.assertTrue(self.player.can_move(self.dest_city))
        self.player.state.health = InfectionState.SYMPTOMATIC
        self.assertTrue(self.player.can_move(self.dest_city))

    def test_can_move_choose(self):
        """Player cannot move to an alerted city when event action is 'choose'."""
        self.dest_city.state.alerted = True

        mock_event = Event(
            category=EventCategory.TRAV_HEALTHY,
            description="none",
            action="choose",
            condition=None,
        )

        with patch.object(Player, "next_event", new_callable=PropertyMock) as mocked:
            mocked.return_value = mock_event
            can_move = self.player.can_move(self.dest_city)
        self.assertFalse(can_move)

    def test_blocked_on_condition_conflict(self):
        """Player cannot move if the event condition matches a condition in either city."""
        self.dest_city.state.conditions.append("Harbor")

        mock_event = Event(
            category=EventCategory.TRAV_HEALTHY,
            description="none",
            action="move",
            condition="Harbor",
        )

        with patch.object(Player, "next_event", new_callable=PropertyMock) as mocked:
            mocked.return_value = mock_event
            can_move = self.player.can_move(self.dest_city)
        self.assertFalse(can_move)

    def test_city_lockdown(self):
        """Player cannot move if city is in lockdown."""
        self.player_city.state.lockdown = True
        self.assertEqual(self.player.city_options(self.cities), [self.player_city])

    def test_next_cities_choose_event(self):
        """Test next cities player can choose to move to"""
        self.cities[3].state.alerted = True

        self.player._next_event = Event(
            category=EventCategory.TRAV_HEALTHY,
            description="none",
            action="choose",
        )

        options = self.player.city_options(self.cities)

        self.assertEqual(options, [self.cities[0],self.cities[1],self.cities[2]])

    def test_next_cities_move_event(self):
        """Test next cities player can move to"""

        self.player._next_event  = Event(
            category=EventCategory.TRAV_HEALTHY,
            description="none",
            action="move",
            amount= 1,
        )

        options = self.player.city_move_destination(self.cities)

        self.assertEqual(options, self.cities[1])

if __name__ == "__main__":
    unittest.main()