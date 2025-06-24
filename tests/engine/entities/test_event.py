"""Tests for classes in the Event module."""

import unittest
from findpatientzero.engine.entities.event import Event, EVENTS, EventCategory


class TestEvent(unittest.TestCase):
    def setUp(self):
        self.event = Event()

    def test_event(self):
        """Test that the Event class can be instantiated."""
        self.assertIsInstance(self.event, Event)

    def test_event_category(self):
        """Test that the event category is set correctly."""
        self.assertEqual(self.event.category, EventCategory.NONE)

    def test_events_keys(self):
        """Test that the events dictionary has the correct keys."""
        for category in EventCategory:
            if category == EventCategory.NONE:
                continue
            self.assertIn(category, EVENTS)

    def test_events_values(self):
        """Test that the events dictionary has non-empty lists for each category."""
        for category, event_list in EVENTS.items():
            if category == EventCategory.NONE:
                continue
            self.assertIsInstance(event_list, list)
            self.assertGreater(len(event_list), 0)


if __name__ == "__main__":
    unittest.main()
