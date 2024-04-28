import random
from engine.entities.event import Event, EventCategory
from engine.game import GameConfig
from engine.entities.player import Player
from gamedata.load import load_city_names


class CityState:
    infection_stage: int
    """The level of infection in the city."""

    last_sus_roll: int | None
    """The last time a Suspicious event was rolled for this city."""

    governor: Player | None
    """The player who is currently the governor of the city."""

    alerted: bool
    """Whether the city has been alerted to an epidemic."""

    lockdown: int
    """The number of rounds of lockdown remaining."""

    infection_pause: int
    """The number of rounds of infection pause remaining."""

    conditions: list[str]
    """The conditions currently affecting the city."""

    def __init__(
        self,
        infection_stage: int = 0,
        last_sus_roll: int | None = None,
        governor: Player | None = None,
        alerted: bool = False,
    ) -> None:
        self.infection_stage = infection_stage
        self.last_sus_roll = last_sus_roll
        self.governor = governor
        self.alerted = alerted


class City:
    names: list[str] = load_city_names()
    """The list of available city names."""

    _name: str
    """The name of the city."""

    _history: list[CityState]
    """The history of the city's states."""

    governor: Player | None
    """The player who is currently the governor of the city."""

    @property
    def in_lockdown(self) -> bool:
        return self.state.lockdown > 0

    def __init__(self) -> None:
        index = random.randint(0, len(City.names) - 1)
        self._name = City.names.pop(index)
        self._history = [CityState()]
        self.governor = None

    def __str__(self) -> str:
        if self.governor is not None:
            return f"{self.name} (Governor: {self.governor})"
        return self.name

    @property
    def name(self) -> str:
        return self._name

    @property
    def state(self) -> CityState:
        return self._history[-1]

    @property
    def alerted(self) -> bool:
        return self.state.alerted

    def can_roll_suspicious(self, round: int, config: GameConfig) -> bool:
        """Determine if the city can roll a Suspicious event."""

        if self.alerted:
            return False
        if self.governor is None:
            return False
        if self.state.last_sus_roll is not None:
            return round - self.state.last_sus_roll >= \
                config.suspicious_cooldown
        return True

    def can_move(self, event: Event) -> bool:
        """Determine if a Traveler carrying out an event can move to the
        city."""
        # Verify that the event is valid
        if event.category not in [
                EventCategory.TRAV_HEALTHY, EventCategory.TRAV_INFECTED]:
            raise ValueError("Only travelers can move.")
        # For choose events, players can only move to uninfected cities
        elif event._action == "choose" and self.alerted:
            return False
        # For any movement, the event condition must not conflict
        elif event.condition is not None:
            return event.condition not in self.state.conditions
        return True
