"""Tests for classes in the Event module."""

import unittest
from findpatientzero.engine.entities.event import Event


class TestEvent(unittest.TestCase):
    def setUp(self):
        self.event = Event()


if __name__ == "__main__":
    unittest.main()
