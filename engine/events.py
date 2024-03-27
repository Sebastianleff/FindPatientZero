from engine.util import load_data


class Event:
    action: str
    """The action that the traveler or city must take."""

    frequency: int
    """The amount of times the event appears in the pool."""

    flavor: str
    """The flavor text of the event."""

    def __init__(self, action: str, frequency: int, flavor: str) -> None:
        self.action = action
        self.frequency = frequency
        self.flavor = flavor

    def __str__(self) -> str:
        return f"[{self.frequency}x] {self.flavor}"


class TravelerEvent(Event):
    pass


class CityEvent(Event):
    pass


def load_events() -> dict[str, list[Event]]:
    city_event_types = load_data('gamedata/event_types_city.txt')
    traveler_event_types = load_data('gamedata/event_types_traveler.txt')

    event_types = dict(city_event_types + traveler_event_types)

    events: dict[str, list[Event]] = {
        'traveler_healthy': [],
        'traveler_infected': [],
        'city_suspicious': [],
        'city_epidemic': []
    }
    for category in events.keys():
        for event in load_data(f'gamedata/events_{category}.txt'):
            action = event[0]
            frequency = int(event[1])
            flavor = f"{event[2]} {event_types[event[0]]}"
            events[category].append(Event(action, frequency, flavor))

    return events
