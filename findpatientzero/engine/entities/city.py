"""Code related to the City entity, which represents a location in the game."""

from dataclasses import dataclass, field
from random import randint

from findpatientzero.engine.entities.event import Event
from findpatientzero.gamedata.load import load_city_names


@dataclass
class CityState:
    """The state of a city in the game."""

    infection_stage: int = 0
    """The level of infection in the city."""

    last_sus_roll: int | None = None
    """The last time a Suspicious event was rolled for this city."""

    alerted: bool = False
    """Whether the city has been alerted to an epidemic."""

    lockdown: int = 0 #QUESTION, is this implmented, and should it restric players. 
    """The number of rounds of lockdown remaining."""

    infection_pause: int = 0
    """The number of rounds of infection pause remaining."""

    conditions: list[str] = field(default_factory=list)
    """The conditions currently affecting the city."""

    event: Event = field(default_factory=Event)
    """The event that the city resolved this round."""


class City:
    """A city in the game."""

    names: list[str] = load_city_names()
    """The list of available city names."""

    _name: str
    """The name of the city."""

    _history: list[CityState]
    """The history of the city's states."""

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
    """The thresholds for whether a d100 roll will detect infection in the city at each stage of infection."""

    MAX_INFECTION_STAGE: int = max(SURVEY_THRESHOLDS.keys())
    """The maximum infection stage."""

    def __init__(self) -> None:
        """
        Create a new City object.
        The city will be assigned a random name from the list of available names.
        """
        index = randint(0, len(City.names) - 1)
        self._name = City.names.pop(index)
        self._history = []

    def __str__(self) -> str:
        return self.name

    @property
    def in_lockdown(self) -> bool:
        """Whether the city is in lockdown."""
        return self.state.lockdown > 0

    @property
    def conditions(self) -> list[str]:
        """The conditions currently affecting the city."""
        return self.state.conditions

    @property
    def name(self) -> str:
        """The name of the city."""
        return self._name

    @property
    def state(self) -> CityState:
        """The current state of the city."""
        return self._history[-1]

    @property
    def alerted(self) -> bool:
        """Whether the city has been alerted to an epidemic."""
        return self.state.alerted

    @property
    def infection_stage(self) -> int:
        """The level of infection in the city."""
        return self.state.infection_stage

    def can_roll_suspicious(
        self,
        game_round: int,
        suspicious_cooldown: int,
    ) -> bool:
        """Determine if the city can roll a Suspicious event.

        Args:
            game_round: The current round.
            suspicious_cooldown: The number of rounds to wait between rolls (from the game configuration).

        Returns:
            True if the Governor of the city can roll a Suspicious event; False otherwise.
        """

        # If the city has been alerted, should be rolling from the Epidemic table
        if self.alerted:
            return False

        if self.state.last_sus_roll is not None:
            return (
                game_round - self.state.last_sus_roll >= suspicious_cooldown
            )

        return True

    @staticmethod
    def survey(current: CityState, advantage: bool) -> bool:
        """Survey a city for infection.

        Args:
            current: The current state of the city.
            advantage: Whether the survey has advantage.

        Returns:
            True if the city is detected to be infected; False otherwise.
        """

        # Roll a d100, twice if the survey has advantage
        for _ in range(1 + advantage):

            # If the roll is no greater than the threshold, the city is detected to be infected
            # (At stage 0, the threshold is 0, so the city is never detected to be infected.)
            if randint(1, 100) <= City.SURVEY_THRESHOLDS[
                current.infection_stage
            ]:
                return True

        return False

    def add_state(self, state: CityState) -> None:
        """Add a new state to the city's history.

        Args:
            state: The new state to add."""
        self._history.append(state)
