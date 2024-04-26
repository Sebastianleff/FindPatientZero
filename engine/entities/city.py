import random
from engine.game import GameConfig
from engine.entities.player import Player
from gamedata.load import load_city_names


class CityState:
    infection_stage: int
    """The level of infection in the city."""

    last_sus_roll: int
    """The last time a Suspicious event was rolled for this city."""

    governor: Player | None
    """The player who is currently the governor of the city."""

    alerted: bool
    """Whether the city has been alerted to an epidemic."""

    def __init__(
        self,
        infection_stage: int = 0,
        last_sus_roll: int = None,
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

    def __init__(self) -> None:
        index = random.randint(0, len(City.NAMES) - 1)
        self.name = City.NAMES.pop(index)
        self.state = CityState()
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
            return (
                round - self.state.last_sus_roll >= config.suspicious_cooldown
            )
        return True
