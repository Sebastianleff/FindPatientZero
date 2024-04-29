from dataclasses import dataclass, field
from random import randint

from engine.entities.player import Player
from engine.game import GameConfig
from gamedata.load import load_city_names


@dataclass
class CityState:
    infection_stage: int = 0
    """The level of infection in the city."""

    last_sus_roll: int | None = None
    """The last time a Suspicious event was rolled for this city."""

    governor: Player | None = None
    """The player who is currently the governor of the city."""

    travelers: list[Player] = field(default_factory=list)
    """The list of travelers currently in the city."""

    alerted: bool = False
    """Whether the city has been alerted to an epidemic."""

    lockdown: int = 0
    """The number of rounds of lockdown remaining."""

    infection_pause: int = 0
    """The number of rounds of infection pause remaining."""

    conditions: list[str] = field(default_factory=list)
    """The conditions currently affecting the city."""


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

    @property
    def conditions(self) -> list[str]:
        return self.state.conditions

    def __init__(self) -> None:
        index = randint(0, len(City.names) - 1)
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

    @property
    def infection_stage(self) -> int:
        return self.state.infection_stage

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

    SURVEY_THRESHOLDS: dict[int, int] = {
        0: 0,
        1: 1,
        2: 2,
        3: 3,
        4: 5,
        5: 8,
        6: 13,
        7: 21,
        8: 34,
        9: 55,
        10: 89,
        11: 100,
    }
    MAX_INFECTION_STAGE: int = max(SURVEY_THRESHOLDS.keys())

    @staticmethod
    def survey(current: CityState, advantage: bool) -> bool:
        """Survey the city for infection."""

        for _ in range(1 + advantage):
            if randint(1, 100) <= City.SURVEY_THRESHOLDS[
                current.infection_stage
            ]:
                return True
        return False

    def add_state(self, state: CityState) -> None:
        self._history.append(state)
