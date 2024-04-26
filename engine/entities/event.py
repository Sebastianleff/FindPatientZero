from enum import Enum
from gamedata.load import load_conditions, load_event_types, load_events


class EventCategory(Enum):
    """The category (wheel) of event."""
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
    """The category (wheel) of event."""

    description: str
    """The description (flavor text) of the event."""

    action: str
    """The action that the traveler or city must take."""

    amount: int
    """The quantity (such as duration for lockdown events or distance for
    movement events) associated with the event (if any)."""

    condition: str
    """The condition associated with the event (if any)."""

    def __init__(
        self,
        category: EventCategory,
        description: str,
        action: str,
        amount: int = None,
        condition: str = None,
    ) -> None:
        self.category = category
        self.description = description
        self.action = action
        self.amount = amount
        self.condition = condition

    def __str__(self) -> str:
        output = f"{self.category.value} event - \"{self.description}\""
        output += f" [action: {self.action}"
        if self.amount is not None:
            output += f" {self.amount}"
        if self.condition is not None:
            output += f", condition: {self.condition}"
        output += "]"

        return output

    # def formatted(self, player: Player) -> str:
    #     """Return the event flavor text with player-specific information."""

    #     output = self.description
    #     if "$CITY$" in output:
    #         output = output.replace("$CITY$", player.city.name)
    #     if "$PLAYER$" in output:
    #         output = output.replace("$PLAYER$", player.name)
    #     if "$GOVERNOR$" in output:
    #         output = output.replace("$GOVERNOR$", player.city.governor.name)

    #     return output


def _get_events() -> dict[EventCategory, list[Event]]:

    evt_types = {
        'city': load_event_types('city'),
        'traveler': load_event_types('traveler'),
    }
    conditions = {
        'city': load_conditions('city'),
        'traveler': load_conditions('traveler'),
    }

    events = dict()
    for cat in EventCategory:
        events[cat] = list()
        plyr_type = 'city' if 'city' in cat.key else 'traveler'
        for event in load_events(cat.key):

            action_text = next(iter(
                e['description'] for e in evt_types[plyr_type]
                if e['action'] == event['action']
                and e.get('amount') == event.get('amount')
            ), None)
            if action_text is None:
                raise ValueError(f"Unrecognized event type: {event['action']}")

            if event.get('condition') is not None:
                cond_text = next(iter(
                    c['description'] for c in conditions[plyr_type]
                    if c['name'] == event['condition']
                ), None)
                if cond_text is None:
                    raise ValueError(
                        f"Unrecognized condition: {event['condition']}"
                    )

            desc = event['description'] + " " + action_text
            new_event = Event(
                category=cat,
                description=desc,
                action=event['action'],
                amount=event.get('amount'),
                condition=event.get('condition'),
            )
            events[cat].extend([new_event] * event['frequency'])

    return events


EVENTS = _get_events()
