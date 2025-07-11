"""Event entity and related functions."""

from dataclasses import dataclass
from enum import Enum
from findpatientzero.gamedata.load import load_conditions, load_event_types, load_events


class EventCategory(Enum):
    """The category (wheel) of event."""

    TRAV_HEALTHY = "Healthy"
    """Events related to healthy or asymptomatic travelers."""

    TRAV_INFECTED = "Infected"
    """Events related to symptomatic travelers."""

    CITY_SUSPICIOUS = "Suspicious"
    """Events related to unalerted cities."""

    CITY_EPIDEMIC = "Epidemic"
    """Events related to infected cities."""

    NONE = "None"
    """No event."""

    @property
    def key(self) -> str:
        """Return the corresponding filename for the event category."""

        if self == EventCategory.TRAV_HEALTHY:
            return "traveler_healthy"
        elif self == EventCategory.TRAV_INFECTED:
            return "traveler_infected"
        elif self == EventCategory.CITY_SUSPICIOUS:
            return "city_suspicious"
        elif self == EventCategory.CITY_EPIDEMIC:
            return "city_epidemic"
        return "none"


@dataclass
class Event:
    """An event that players can encounter in a game round."""

    category: EventCategory = EventCategory.NONE
    """The category (wheel) of event."""

    description: str = "No event"
    """The description (flavor text) of the event."""

    action: str = "none"
    """The action that the traveler or city must take."""

    amount: int = 0
    """The quantity (such as duration for lockdown events or distance for
    movement events) associated with the event (if any)."""

    condition: str | None = None
    """The condition associated with the event (if any)."""

    def __post_init__(self) -> None:
        if self.category != EventCategory.NONE:
            assert self.description != "No event", "Event description is missing"
            assert self.action != "none", "Event action is missing"

    def __str__(self) -> str:
        output = f"{self.category.value} event - \"{self.description}\""
        output += f" [action: {self.action}"
        if self.amount != 0:
            output += f" {self.amount}"
        if self.condition is not None:
            output += f", condition: {self.condition}"
        output += "]"

        return output

def _get_events() -> dict[EventCategory, list[Event]]:
    """Load all events from the data files.

    Returns:
        dict[EventCategory, list[Event]]: A dictionary of event categories and their respective event lists, including repeats based on frequency."""

    # Load event types and conditions
    evt_types = {
        'city': load_event_types('city'),
        'traveler': load_event_types('traveler'),
    }
    conditions = {
        'city': load_conditions('city'),
        'traveler': load_conditions('traveler'),
    }

    # Load events by category
    events: dict[EventCategory, list[Event]] = dict()
    for cat in EventCategory:

        # Skip the NONE category
        if cat == EventCategory.NONE:
            continue

        # Initialize the event list for the category
        events[cat] = list()

        # Get the player type for the event category
        plyr_type = 'city' if 'city' in cat.key else 'traveler'

        # Load the events for the category
        for event in load_events(cat.key):

            # Get the action text for the event/amount combination
            action_text = next(iter(
                e['description'] for e in evt_types[plyr_type]
                if e['action'] == event['action']
                and e.get('amount') == event.get('amount')
            ), None)

            # If there is no associated action text, raise an error
            if action_text is None:
                raise ValueError(f"Unrecognized event type: {event['action']}")

            # Get the condition text for the event
            if event.get('condition') is not None:
                cond_text = next(iter(
                    c['description'] for c in conditions[plyr_type]
                    if c['name'] == event.get('condition')
                ), None)
                if cond_text is None:
                    raise ValueError(
                        f"Unrecognized condition: {event.get('condition')}"
                    )

            # Assemble the event description and create the event object
            desc = (event['description']) + " " + action_text
            new_event = Event(
                category=cat,
                description=desc,
                action=event['action'],
                amount=event.get('amount', 0),
                condition=event.get('condition'),
            )

            # Add the event to the list, repeating based on frequency
            events[cat].extend([new_event] * event['frequency'])

    return events


EVENTS = _get_events()
"""A dictionary of event categories and their respective event lists, including repeats based on frequency."""

NULL_EVENT = Event(
    category=EventCategory.NONE,
    description="You take a long bath, nothing happens.",
    action="none",
)
