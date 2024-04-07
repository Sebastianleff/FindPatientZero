from enum import Enum
import random

from engine.entities.city import City
from engine.entities.event import EVENTS, Event, EventCategory
from engine.util import load_data


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


class PlayerState:
    health: InfectionState
    """The health state of the traveler."""

    infection_timer: int
    """The timer for the traveler's infection."""

    role: PlayerRole
    """The role of the player."""

    city: City
    """The city the player is currently in."""

    def __init__(
        self,
        health: InfectionState = InfectionState.HEALTHY,
        infection_timer: int = 0,
        role: PlayerRole = PlayerRole.TRAVELER,
    ) -> None:
        self.health = health
        self.infection_timer = infection_timer
        self.role = role


class Player:
    _name: str
    """The name of the player."""

    _history: list[PlayerState]
    """The history of the player's states."""

    _pending_sus_prompt: bool
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
    def city(self) -> City:
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

        self._pending_sus_prompt = False
        self._sus_prompt_response = None

    def respond_suspicious(self, response: bool) -> None:
        """Set the player's response to the Suspicious event prompt."""

        self._sus_prompt_response = response
        self._pending_sus_prompt = False

    @property
    def pending_sus_prompt(self) -> bool:
        """Whether the player has a pending Suspicious event prompt."""
        return self._pending_sus_prompt

    @property
    def sus_prompt_response(self) -> bool | None:
        """The player's response to the Suspicious event prompt."""
        return self._sus_prompt_response

    @property
    def next_event_category(self) -> EventCategory | None:
        category = None

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
            if self.city.alerted:
                category = EventCategory.CITY_EPIDEMIC
            elif self.get_sus_prompt_response():
                category = EventCategory.CITY_SUSPICIOUS

        return category

    @property
    def next_event(self) -> Event | None:
        """The next event that the player must resolve."""

        # If the player has no next event category, return None
        if self.next_event_category is None:
            return None

        # If an event has not been chosen yet, choose one at random
        if self._next_event is None:
            self._next_event = random.choice(EVENTS[self.next_event_category])

        return self._next_event
    
    @property
    def city_options(self, cities: list[City]) -> list[City]:
        """The cities that the player can choose from."""
        if self.role != PlayerRole.TRAVELER:
            raise ValueError("Only travelers can choose cities.")

        if self.next_event.action == "CHOOSE":
            options = [city for city in cities if not city.alerted]
            if len(options) == 0:
                options = None #TODO
    
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
    names: list[str] = load_data("gamedata/cpu_names.txt")

    def __init__(self) -> None:
        index = random.randint(0, len(CPUPlayer.names) - 1)
        super().__init__(CPUPlayer.names.pop(index))

    def __str__(self) -> str:
        return f"{self._name} (CPU)"
