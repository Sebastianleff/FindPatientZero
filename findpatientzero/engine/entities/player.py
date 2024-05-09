from dataclasses import dataclass, field
import random
from enum import Enum

from findpatientzero.engine.entities.city import City
from findpatientzero.engine.entities.event import EVENTS, Event, EventCategory
from findpatientzero.gamedata.load import load_cpu_names


class InfectionState(Enum):
    """The state of a traveler's infection."""

    HEALTHY = "Healthy"
    ASYMPTOMATIC = "Asymptomatic"
    SYMPTOMATIC = "Symptomatic"
    IMMUNE = "Immune"
    DEAD = "Dead"


class PlayerRole(Enum):
    """The role of a player."""

    TRAVELER = "Traveler"
    GOVERNOR = "Governor"
    OBSERVER = "Observer"


@dataclass
class PlayerState:
    health: InfectionState = InfectionState.HEALTHY
    """The health state of the traveler."""

    infected_round: int | None = None
    """The round in which the traveler was infected."""

    role: PlayerRole = PlayerRole.TRAVELER
    """The role of the player."""

    city: City | None = None
    """The city the player is currently in."""

    event: Event = field(default_factory=Event)
    """The event that the player resolved this round."""


class Player:
    _name: str
    """The name of the player."""

    _history: list[PlayerState]
    """The history of the player's states."""

    _sus_prompt_pending: bool
    """Whether the player has a pending Suspicious event prompt."""

    _sus_prompt_response: bool | None
    """The player's response to the Suspicious event prompt."""

    _next_event: Event | None
    """The next event that the player must resolve."""

    _pending_city_prompt: bool
    """Whether the player has a pending city choice prompt."""

    _city_prompt_response: City | None
    """The player's response to the city choice prompt."""

    def __init__(self, name: str) -> None:
        self._name = name

    def __str__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> PlayerState:
        return self._history[-1]

    @property
    def city(self) -> City | None:
        return self.state.city

    @property
    def role(self) -> PlayerRole:
        return self.state.role

    @property
    def health(self) -> InfectionState:
        return self.state.health

    def prompt_suspicious(self) -> None:
        """Update flags indicating that the player has a pending Suspicious
        event prompt."""

        self._sus_prompt_pending = False
        self._sus_prompt_response = None

    def respond_suspicious(self, response: bool) -> None:
        """Set the player's response to the Suspicious event prompt."""

        self._sus_prompt_response = response
        self._sus_prompt_pending = False

    @property
    def sus_prompt_pending(self) -> bool:
        """Whether the player has a pending Suspicious event prompt."""
        return self._sus_prompt_pending

    @property
    def sus_prompt_response(self) -> bool | None:
        """The player's response to the Suspicious event prompt."""
        return self._sus_prompt_response

    @property
    def last_event(self) -> Event:
        """The last event that the player resolved."""
        return self.state.event

    @property
    def next_event_category(self) -> EventCategory:
        category = EventCategory.NONE

        if self.role == PlayerRole.TRAVELER:
            if self.health in [
                InfectionState.HEALTHY,
                InfectionState.ASYMPTOMATIC,
                InfectionState.IMMUNE,
            ]:
                category = EventCategory.TRAV_HEALTHY
            elif self.health == InfectionState.SYMPTOMATIC:
                category = EventCategory.TRAV_INFECTED

        elif self.role == PlayerRole.GOVERNOR:
            assert self.city is not None
            assert self.sus_prompt_pending is False
            if self.city.alerted:
                category = EventCategory.CITY_EPIDEMIC
            elif self.sus_prompt_response is not None:
                category = EventCategory.CITY_SUSPICIOUS

        return category

    @property
    def next_event(self) -> Event:
        """The next event that the player must resolve."""

        # If the player has no next event category, return a "no event" event
        if self.next_event_category is EventCategory.NONE:
            return Event()

        # If an event has not been chosen yet, choose one at random
        if self._next_event is None:
            pool = EVENTS[self.next_event_category].copy()

            # Remove the last event from the pool to avoid repeats
            try:
                pool.remove(self.last_event)
            # If the last event is not in the pool, ignore the error
            except ValueError:
                pass

            self._next_event = random.choice(pool)

        return self._next_event

    def can_move(self, dest: City) -> bool:
        """Whether the player can move to a given city."""

        # Verify that the event is valid
        if self.next_event.category not in [
            EventCategory.TRAV_HEALTHY,
            EventCategory.TRAV_INFECTED,
        ]:
            raise ValueError("Only travelers can move.")
        assert self.city is not None
        # For choose events, players can only move to uninfected cities
        if self.next_event.action == "choose" and dest.alerted:
            return False
        # For any movement, the event condition must not conflict
        # TODO: Conditions should be checked in the event resolution
        elif self.next_event.condition is not None:
            return self.next_event.condition not in (
                self.city.conditions + dest.conditions
            )
        return True

    def city_options(self, cities: list[City]) -> list[City]:
        """The cities that the player can choose from."""
        if self.role != PlayerRole.TRAVELER:
            raise ValueError("Only travelers can choose cities.")
        assert self.city is not None
        if self.city.in_lockdown:
            return [self.city]
        elif self.next_event.action == "choose":
            options = [city for city in cities if not self.can_move(city)]
            if len(options) > 0:
                return options
        elif self.next_event.action == "move":
            curr_index = cities.index(self.city)
            target_city = cities[
                (curr_index + self.next_event.amount) % len(cities)
            ]
            if self.can_move(target_city):
                return [target_city]
        return [self.city]

    def prompt_city_choice(self) -> None:
        """Update flags indicating that the player has a pending city choice
        prompt."""

        self._pending_city_prompt = True
        self._city_prompt_response = None

    def respond_city_choice(self, city: City) -> None:
        """Set the player's response to the city choice prompt."""

        self._city_prompt_response = city
        self._pending_city_prompt = False

    @property
    def pending_city_prompt(self) -> bool:
        """Whether the player has a pending city choice prompt."""
        return self._pending_city_prompt

    @property
    def city_prompt_response(self) -> City | None:
        """The player's response to the city choice prompt."""
        return self._city_prompt_response

    def add_state(self, state: PlayerState) -> None:
        self._history.append(state)


class CPUPlayer(Player):
    names: list[str] = load_cpu_names()
    """The list of available CPU player names."""

    def __init__(self) -> None:
        index = random.randint(0, len(CPUPlayer.names) - 1)
        super().__init__(CPUPlayer.names.pop(index))

    def __str__(self) -> str:
        return f"{self._name} (CPU)"
