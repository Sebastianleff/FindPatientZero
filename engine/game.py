import random
from dataclasses import dataclass, replace
from enum import Enum

from engine.entities.city import City, CityState
from engine.entities.player import (
    CPUPlayer,
    InfectionState,
    Player,
    PlayerRole,
    PlayerState,
)


@dataclass
class GameConfig:
    """The configuration of a game."""

    num_players: int
    """The number of players in the game."""

    num_cities: int
    """The number of cities in the game."""

    suspicious_cooldown: int = 3
    """The number of rounds before a Suspicious event can be rolled again."""

    lockdown_duration: int = 2
    """The number of rounds a city remains in lockdown."""

    def __post_init__(self):
        assert self.num_players >= 2
        assert self.num_cities >= 2
        assert self.suspicious_cooldown >= 0
        assert self.lockdown_duration >= 0


@dataclass
class GameState:
    round: int
    """The current round number of the game."""

    players: dict[Player, PlayerState]
    """The states of each player in the game."""

    cities: dict[City, CityState]
    """The states of each city in the game."""


class GamePhase(Enum):
    """The phase of a game."""

    GAME_START = "Starting a new game"
    ROUND_START = "Starting a new round"
    SUS_PROMPTS = "Governors deciding whether to roll a Suspicious event"
    ROLL_EVENTS = "Rolling events"
    CITY_PROMPTS = "Prompting players to choose cities"
    RESOLVE_MOVES = "Resolving moves"
    ERROR = "An error occurred"


class Game:

    config: GameConfig
    """The configuration of the game."""

    _players: list[Player]
    """The list of players in the game."""

    _cities: list[City]
    """The list of cities in the game."""

    _history: list[GameState] = []
    """The history of the game's states."""

    _round: int = 0
    """The current round number of the game."""

    _phase: GamePhase = GamePhase.GAME_START
    """The current phase of the game."""

    _phase_complete: bool = False
    """Whether the current phase is complete."""

    _patient_zero: Player
    """The player who is patient zero of the epidemic."""

    @property
    def players(self) -> list[Player]:
        """The list of players in the game."""
        return self._players.copy()

    @property
    def cities(self) -> list[City]:
        """The list of cities in the game."""
        return self._cities.copy()

    @property
    def patient_zero(self) -> Player:
        return self._patient_zero

    def __init__(self, config: GameConfig, player_names: list[str]):

        self.config = config
        self._players = [Player(name) for name in player_names]
        self._players += [
            CPUPlayer() for _ in range(config.num_players - len(player_names))
        ]
        self._cities = [City() for _ in range(config.num_cities)]

    def __str__(self) -> str:
        output = "PLAYERS"
        for i, player in enumerate(self._players):
            output += f"\n\tPlayer {i+1}: {player}"
        output += "\n\nCITIES"
        for i, city in enumerate(self._cities):
            output += f"\n\tCity {i+1}: {city}"
        output += f"\n\nPatient Zero: {self._patient_zero}"

        return output

    # TODO Implement phase control
    @property
    def phase(self) -> GamePhase:
        if not self._phase_complete:
            return self._phase
        if self._phase == GamePhase.GAME_START:
            return GamePhase.ROUND_START
        elif self._phase == GamePhase.ROUND_START:
            return GamePhase.SUS_PROMPTS

        return GamePhase.ERROR

    def game_start(self) -> None:
        # Pick a random player to be patient zero
        self._patient_zero = random.choice(self._players)

        # Initialize player states
        city_choices = list()
        for player in self._players:
            if len(city_choices) == 0:
                city_choices = random.sample(self._cities, len(self._cities))
            city = city_choices.pop()
            player.add_state(PlayerState(city=city))

        # Initialize city states
        for city in self._cities:
            city.add_state(CityState(
                travelers=[
                    player for player in self._players if player.city == city
                ]
            ))

        # Commit initial states to history
        self._history.append(
            GameState(
                round=self._round,
                players={player: player.state for player in self._players},
                cities={city: city.state for city in self._cities},
            )
        )

        self._phase_complete = True

    def round_start(self) -> None:
        self._round += 1

        # Determine which Governors can roll a Suspicious event
        for city in self._cities:
            if city.can_roll_suspicious(self._round, self.config):
                assert city.governor is not None
                city.governor.prompt_suspicious()
        # TODO mark phase as done when all governors have responded

    def update_city_state(self, current: CityState) -> CityState:
        """Determine the next state of a city."""

        # Copy the current state with updated values
        new = replace(
            current,
            conditions=(current.conditions.copy()
                        if current.lockdown > 0
                        else list()),
            infection_pause=max(0, current.infection_pause - 1),
            lockdown=max(0, current.lockdown - 1),
            infection_stage=(
                min(current.infection_stage + 1, City.MAX_INFECTION_STAGE)
                if current.infection_stage > 0 and current.infection_pause == 0
                else 0
            ),
        )

        # Resolve event if there is a governor
        if current.governor is not None:
            # Actions
            event = current.governor.next_event
            if event.action == "pause":
                new.infection_pause = event.amount
            elif event.action.startswith("survey"):
                new.alerted = City.survey(
                    current, event.action.endswith("adv")
                )
            elif event.action == "rollback":
                new.infection_stage = max(
                    0, current.infection_stage - event.amount
                )

            # Conditions
            if event.condition == "lockdown":
                new.lockdown = self.config.lockdown_duration
                new.conditions = ["harbor", "road", "merch"]
            elif event.condition is not None:
                new.conditions.append(event.condition)

        return new

    def update_player_state(
                self,
                player: Player,
                current: PlayerState,
                dest: City,
                dest_state: CityState,
            ) -> tuple[PlayerState, CityState]:
        """
        Determine the next state of a player and the city they are moving to.

        Args:
            current: The current state of the player.
            dest: The city the player is moving to.
            dest_state: The next state of the destination city.

        Returns:
            A tuple containing the next state of the player and the city.
        """

        # Copy the current state with updated values
        new = replace(current, city=dest)

        # Resolve traveler move
        if current.role == PlayerRole.TRAVELER:
            # Move to the next city
            assert new.city is not None
            # Update health status
            if (
                current.health == InfectionState.HEALTHY
                and dest.infection_stage > 0
            ):
                new.health = InfectionState.ASYMPTOMATIC
                new.infected_round = self._round
            elif current.health != InfectionState.IMMUNE:
                assert current.infected_round is not None
                roll = random.randint(1, 100)
                if self._round - current.infected_round <= 4:
                    if roll > 50:
                        dest_state.infection_stage += 1
                elif self._round - current.infected_round <= 9:
                    dest_state.infection_stage += 1
                    if 40 < roll <= 87:
                        new.health = InfectionState.SYMPTOMATIC
                    elif roll > 87:
                        new.health = InfectionState.DEAD
                else:
                    dest_state.infection_stage += 1
                    if roll <= 50:
                        new.health = InfectionState.IMMUNE
                    else:
                        new.health = InfectionState.DEAD

        return (new, dest_state)

    def reassign_players(
                self,
                dead_plyrs: dict[Player, PlayerState],
                cities: dict[City, CityState],
            ) -> tuple[dict[Player, PlayerState], dict[City, CityState]]:
        """
        Reassign newly dead players to a new role.

        Args:
            dead_plyrs: A dictionary of dead players and their states.
            cities: A dictionary of cities and their states.

        Returns:
            A tuple containing the updated states of the players and cities.
        """
        open_cities = [
            city for city, state in cities.items() if state.governor is None
        ]
        for player, state in dead_plyrs.items():
            if len(open_cities) == 0:
                state.role = PlayerRole.OBSERVER
                state.city = None
                continue
            state.role = PlayerRole.GOVERNOR
            if state.city in open_cities:
                state.city.governor = player
                open_cities.remove(state.city)
            else:
                state.city = open_cities.pop()
                state.city.governor = player

        return (dead_plyrs, cities)

    def resolve_moves(self) -> None:
        """
        Resolve the moves of all players in the game.
        """

        # Update city states
        new_city_states = {
            city: self.update_city_state(city.state) for city in self._cities
        }

        # Update player states
        new_player_states = dict()
        for player in self._players:
            assert player.city_prompt_response is not None
            dest = player.city_prompt_response
            new_player_states[player], new_city_states[dest] = \
                self.update_player_state(
                    player, player.state, dest, new_city_states[dest]
                )

        # Reassign dead players to new roles
        dead_players = {
            player: state
            for player, state in new_player_states.items()
            if state.health == InfectionState.DEAD
        }
        dead_players, new_city_states = self.reassign_players(
            dead_players, new_city_states
        )
        new_player_states.update(dead_players)

        # Commit changes to history
        self._history.append(
            GameState(
                round=self._round,
                players=new_player_states,
                cities=new_city_states,
            )
        )
        for player, state in new_player_states.items():
            player.add_state(state)
        for city, state in new_city_states.items():
            city.add_state(state)
