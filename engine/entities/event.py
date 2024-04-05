from enum import Enum
from engine.entities.player import Player
from engine.util import load_data


class EventCategory(Enum):
    """The type of event."""
    TRAV_HEALTHY = "Healthy"
    TRAV_INFECTED = "Infected"
    CITY_SUSPICIOUS = "Suspicious"
    CITY_EPIDEMIC = "Epidemic"

    @property
    def key(self) -> str:
        if self == EventCategory.TRAV_HEALTHY:
            return "traveler_healthy"
        elif self == EventCategory.TRAV_INFECTED:
            return "traveler_infected"
        elif self == EventCategory.CITY_SUSPICIOUS:
            return "city_suspicious"
        elif self == EventCategory.CITY_EPIDEMIC:
            return "city_epidemic"


class Event:
    category: EventCategory

    action: str
    """The action that the traveler or city must take."""

    frequency: int
    """The amount of times the event appears in the pool."""

    flavor: str
    """The flavor text of the event."""

    def __init__(
        self,
        category: EventCategory,
        action: str,
        frequency: int,
        flavor: str
    ) -> None:
        self.category = category
        self.action = action
        self.frequency = frequency
        self.flavor = flavor

    def __str__(self) -> str:
        return self.flavor

    def formatted(self, player: Player) -> str:
        """Return the event flavor text with player-specific information."""

        output = self.flavor
        if "$CITY$" in output:
            output = output.replace("$CITY$", player.city.name)
        if "$PLAYER$" in output:
            output = output.replace("$PLAYER$", player.name)
        if "$GOVERNOR$" in output:
            output = output.replace("$GOVERNOR$", player.city.governor.name)

        return output


def _load_events() -> dict[EventCategory, set[Event]]:
    city_event_types = load_data('gamedata/event_types_city.txt')
    traveler_event_types = load_data('gamedata/event_types_traveler.txt')

    event_types = dict(city_event_types + traveler_event_types)

    events: dict[EventCategory, set[Event]] = {
        EventCategory.TRAV_HEALTHY: set(),
        EventCategory.TRAV_INFECTED: set(),
        EventCategory.CITY_SUSPICIOUS: set(),
        EventCategory.CITY_EPIDEMIC: set(),
    }
    for category in events.keys():
        for event in load_data(f'gamedata/events_{category.key}.txt'):
            action = event[0]
            frequency = int(event[1])
            flavor = f"{event[2]} {event_types[event[0]]}"
            events[category].add(Event(category, action, frequency, flavor))

    return events


EVENTS = _load_events()
