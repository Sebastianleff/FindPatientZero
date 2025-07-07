"""Player entity and related classes."""

from dataclasses import dataclass, field
import random
from enum import Enum

from findpatientzero.engine.entities.city import City
from findpatientzero.engine.entities.event import EVENTS, Event, EventCategory
from findpatientzero.gamedata.load import load_cpu_names


class InfectionState(Enum):
    """The state of a traveler's infection."""

    HEALTHY = "Healthy"
    """The traveler is healthy and uninfected."""

    ASYMPTOMATIC = "Asymptomatic"
    """The traveler is infected but appears healthy."""

    SYMPTOMATIC = "Symptomatic"
    """The traveler is infected and showing symptoms."""

    IMMUNE = "Immune"
    """The traveler has recovered and is immune to reinfection."""

    DEAD = "Dead"
    """The traveler has died."""


class PlayerRole(Enum):
    """The role of a player."""

    TRAVELER = "Traveler"
    """A traveler who moves between cities based on event outcomes."""

    GOVERNOR = "Governor"
    """A governor who manages a city, generating events and making decisions."""

    OBSERVER = "Observer"
    """A player who died and could not be assigned to a city as governor, but can still vote for the suspected Patient Zero."""


@dataclass
class PlayerState:
    """The state of a player in a game round."""

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
    """A player in the game."""

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
        """Initialize a player.

        Args:
            name (str): The name of the player.
        """

        self._name = name
        self._history = []
        self._sus_prompt_pending = False
        self._sus_prompt_response = None
        self._next_event = None
        self._pending_city_prompt = False
        self._city_prompt_response = None

    def __str__(self) -> str:
        return self._name

    @property
    def name(self) -> str:
        """The name of the player."""
        return self._name

    @property
    def state(self) -> PlayerState:
        """The current state of the player."""
        return self._history[-1]

    @property
    def city(self) -> City | None:
        """The city the player is currently in."""
        return self.state.city

    @property
    def role(self) -> PlayerRole:
        """The role of the player."""
        return self.state.role

    @property
    def health(self) -> InfectionState:
        """The health state of the player."""
        return self.state.health

    @property
    def last_event(self) -> Event:
        """The last event that the player resolved."""
        return self.state.event

    @property
    def pending_city_prompt(self) -> bool:
        """Whether the player has a pending city choice prompt."""
        return self._pending_city_prompt

    @property
    def city_prompt_response(self) -> City | None:
        """The player's response to the city choice prompt."""
        return self._city_prompt_response

    @property
    def sus_prompt_pending(self) -> bool:
        """Whether the player has a pending Suspicious event prompt."""
        return self._sus_prompt_pending

    @property
    def sus_prompt_response(self) -> bool | None:
        """The player's response to the Suspicious event prompt."""
        return self._sus_prompt_response

    @property
    def next_event_choice(self) -> bool:
        """If the next event is of the choice type"""
        return self._next_event.action == "choose"

    @property
    def next_event_move(self) -> bool:
        """If the next event is of the choice type"""
        return self._next_event.action == "move"

    @property
    def next_event(self) -> Event:
        """The next event that the player must resolve."""
        # If the player has no next event category, return a "no event" event
        if self.next_event_category is EventCategory.NONE:
            return Event()
        return self._next_event

    @property
    def next_event_category(self) -> EventCategory:
        """The category of the next event that the player must resolve."""

        # If the player is dead, there is no next event
        category = EventCategory.NONE

        if self.role == PlayerRole.TRAVELER:
            # Travelers not currently displaying symptoms can roll healthy events
            if self.health in [
                InfectionState.HEALTHY,
                InfectionState.ASYMPTOMATIC,
                InfectionState.IMMUNE,
            ]:
                category = EventCategory.TRAV_HEALTHY

            # Travelers displaying symptoms can only roll infected events
            elif self.health == InfectionState.SYMPTOMATIC:
                category = EventCategory.TRAV_INFECTED

        elif self.role == PlayerRole.GOVERNOR:
            assert self.city is not None
            assert self.sus_prompt_pending is False

            # Governors of alerted cities can only roll epidemic events
            if self.city.alerted:
                category = EventCategory.CITY_EPIDEMIC

            # Governors of unalerted cities can roll a suspicious event if they chose to
            elif self.sus_prompt_response is not None:
                category = EventCategory.CITY_SUSPICIOUS

        return category

    def roll_next_event(self) -> None:
        """Roll the next event.""" #TODO add player input choices
        # If an event has not been chosen yet, choose one at random
        pool = EVENTS[self.next_event_category].copy()

        # Remove the last event from the pool to avoid repeats
        try:
            pool.remove(self.last_event)
        # If the last event is not in the pool, ignore the error
        except ValueError:
            pass

        self._next_event = random.choice(pool)

    def can_move(self, dest: City) -> bool:
        """Whether the player can move to a given city.

        Args:
            dest (City): The city the player wants to move to.

        Returns:
            bool: Whether the player can move to the city."""

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
        elif self.next_event.condition is not None:
            return self.next_event.condition not in (
                self.city.conditions + dest.conditions
            )

        return True

    def city_options(self, cities: list[City]) -> list[City]:
        """The cities that the player can choose from.
        
        Args:
            cities (list[City]): The list of cities to choose from.
            
        Returns:
            list[City]: The cities that the player can actually try to move to."""
        
        # Verify that the event is valid
        if self.role != PlayerRole.TRAVELER:
            raise ValueError("Only travelers can choose cities.")
        assert self.city is not None

        # If the player is in a locked down city, they can only stay there
        if self.city.in_lockdown:
            return [self.city]
        
        # If the player has a choose event, they can only move to uninfected cities
        elif self.next_event_choice:
            options = [city for city in cities if self.can_move(city)]
            if len(options) > 0:
                return options

        # Default to the current city
        return [self.city]

    def city_move_destination(self, cities: list[City]) -> City:
        """The next city a player will move to with current event

        Args:
            cities (list[City]): The list of cities to choose from.

        Returns:
            City: The next city a player will move to."""

        # Verify that the event is valid
        if self.role != PlayerRole.TRAVELER:
            raise ValueError("Only travelers can choose cities.")
        assert self.city is not None

        # If the player is in a locked down city, they can only stay there
        if self.city.in_lockdown:
            return self.city

        # If current event is choice, return chosen city
        elif self.next_event_choice:
            return self.city_prompt_response

        # If the player has a move event, they can only move to the target city
        elif self.next_event_move:
            curr_index = cities.index(self.city)
            target_city = cities[
                (curr_index + self.next_event.amount) % len(cities)
            ]
            if self.can_move(target_city):
                return target_city

        # Default to the current city for stay events
        return self.city

    def infect_patient_zero(self) -> None:
        """Infect patient zero. Should only be called for patient zero on game start."""
        self.state.health = InfectionState.ASYMPTOMATIC
        self.state.infected_round = 0

    def add_state(self, state: PlayerState) -> None:
        """Add a state to the player's history.

        Args:
            state (PlayerState): The state to add.
        """
        self._history.append(state)

    def reset_next_event(self) -> None:
        """Reset the next event."""
        self._next_event = None

    def prompt_suspicious(self) -> None:
        """Update flags indicating that the player has a pending Suspicious
        event prompt."""

        self._sus_prompt_pending = True
        self._sus_prompt_response = None

    def respond_suspicious(self, response: bool) -> None:
        """Set the player's response to the Suspicious event prompt.

        Args:
            response (bool): The player's response to the prompt."""

        self._sus_prompt_response = response
        self._sus_prompt_pending = False

    def prompt_city_choice(self) -> None:
        """Update flags indicating that the player has a pending city choice
        prompt."""

        self._pending_city_prompt = True
        self._city_prompt_response = None

    def respond_city_choice(self, city: City) -> None:
        """Set the player's response to the city choice prompt.

        Args:
            city (City): The city the player chose.

        """

        self._pending_city_prompt = False
        self._city_prompt_response = city


class CPUPlayer(Player): #TODO add proper AI and AI control
    """A player that is controlled by the game engine."""

    names: list[str] = load_cpu_names()
    """The list of available CPU player names."""

    def __init__(self) -> None:
        """Initialize a CPU player with a random name."""

        index = random.randint(0, len(CPUPlayer.names) - 1)
        super().__init__(CPUPlayer.names.pop(index))

    def __str__(self) -> str:
        return f"{self._name} (CPU)"
