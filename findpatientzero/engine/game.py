"""The game module contains the overarching Game class and related classes/functions."""

import random
from dataclasses import dataclass, replace
from enum import Enum, nonmember

from findpatientzero.engine.entities.city import City, CityState
from findpatientzero.engine.entities.event import Event, NULL_EVENT
from findpatientzero.engine.entities.player import (
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

    auto_roll: bool = True
    """Whether the game should automatically roll dice or get player input."""

    survey_threshold: int = 3
    """The threshold for automatic surveying a city for infections."""

    def __post_init__(self):
        assert self.num_players >= 2
        assert self.num_cities >= 2
        assert self.suspicious_cooldown >= 0
        assert self.lockdown_duration >= 0


@dataclass
class GameState:
    """The state of a game at a given point in time."""

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
    ROLL_DICE = "Players input dice roll for events"
    ROLL_EVENTS = "Rolling events"
    CITY_PROMPTS = "Prompting players to choose cities"
    RESOLVE_MOVES = "Resolving moves"
    GAME_OVER = "Game over"
    ERROR = "An error occurred"


class Game:
    """The main control class for a game of Find Patient Zero."""

    config: GameConfig
    """The configuration of the game."""

    _players: list[Player]
    """The list of players in the game."""

    _cities: list[City]
    """The list of cities in the game."""

    _history: list[GameState]
    """The history of the game's states."""

    _round: int
    """The current round number of the game."""

    _phase: GamePhase
    """The current phase of the game."""

    _prompts_pending: bool
    """If any players have pending prompts"""

    _patient_zero: Player
    """The player who is patient zero of the epidemic."""

    def __init__(self, config: GameConfig, player_names: list[str]):
        """Initialize a new game with the given configuration and player names.

        Args:
            config: The configuration of the game.
            player_names: The names of the players in the game.
        """

        self.config = config
        self._players = [Player(name) for name in player_names]
        self._players += [
            CPUPlayer() for _ in range(config.num_players - len(player_names))
        ]
        self._cities = [City() for _ in range(config.num_cities)]
        self._history = []
        self._round = 0
        self._prompts_pending = False

        self.game_start()

    def game_start(self) -> None:
        """Carry out the setup phase of the game."""
        self._phase = GamePhase.GAME_START

        # Initialize player states
        city_choices = list()
        for player in self._players:
            if len(city_choices) == 0:
                city_choices = random.sample(self._cities, len(self._cities))
            city = city_choices.pop()
            player.add_state(PlayerState(city=city))

        # Pick a random player to be patient zero and infect them
        self._patient_zero = random.choice(self._players)
        self._patient_zero.infect_patient_zero()

        # Initialize city states
        for city in self._cities:
            city.add_state(CityState())

        # Commit initial states to history
        self._history.append(
            GameState(
                round=self._round,
                players={player: player.state for player in self._players},
                cities={city: city.state for city in self._cities},
            )
        )

    def get_governor(self, city: City) -> Player | None:
        """Get the governor of a city, if one exists.

        Args:
            city: The city to check for a governor.

        Returns:
            The governor of the city, or None if there is no governor.
        """

        for player in self._players:
            if player.city == city and player.role == PlayerRole.GOVERNOR:
                return player
        return None

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
        """The player who is patient zero of the epidemic."""
        return self._patient_zero

    @property
    def round(self) -> int:
        """The current round number of the game."""
        return self._round

    @property
    def phase(self) -> GamePhase:
        """The current phase of the game."""
        return self._phase

    @property
    def prompts_pending(self) -> bool:
        """If any player prompts are pending"""
        return self._prompts_pending

    @property
    def game_over(self) -> bool:
        """If the game has ended."""
        return all(player.state.health == InfectionState.DEAD or player.state.health == InfectionState.IMMUNE
                   for player in self._players)

    @property
    def phase_complete(self) -> bool:
        """Whether the current game phase is complete."""

        if self._phase == GamePhase.GAME_START:
            return all([self._round == 0, self.patient_zero is not None, (len(self._history) != 0)])

        if self._phase == GamePhase.ROUND_START:
            return self._round == self._history[-1].round+1

        if self._phase == GamePhase.SUS_PROMPTS:
            return all(
                not player.sus_prompt_pending
                for player in self._players
                if player.role == PlayerRole.GOVERNOR
            )

        if self._phase == GamePhase.ROLL_DICE:
            return True #TODO add check for roll dice phase

        if self._phase == GamePhase.ROLL_EVENTS:
            return all(
                player
                for player in self._players
                if player.next_event is not NULL_EVENT
            )

        if self._phase == GamePhase.CITY_PROMPTS:
            return all(
                (not player.pending_city_prompt)
                for player in self._players
                if player.role == PlayerRole.TRAVELER
            )

        if self._phase == GamePhase.RESOLVE_MOVES:
            return True #TODO add check logic for resolve moves phase

        return False

    def go_to_next_phase(self) -> bool:
        """
        Move the game to the next phase.

        Returns:
            True if the game phase was successfully executed, False otherwise.
        """

        if not self.phase_complete:
            raise RuntimeError("Cannot advance phase: current phase is not complete.")

        if self._phase == GamePhase.GAME_START:
            self._phase = GamePhase.ROUND_START
            self.round_start()

        elif self._phase == GamePhase.ROUND_START:
            self._phase = GamePhase.SUS_PROMPTS
            self.sus_prompts()

        elif self._phase == GamePhase.SUS_PROMPTS:
            self._prompts_pending = False
            if self.config.auto_roll:
                self._phase = GamePhase.ROLL_EVENTS
                self.roll_events()
            else:
                self._phase = GamePhase.ROLL_DICE
                self.roll_prompts()

        elif self._phase == GamePhase.ROLL_DICE:
            self._prompts_pending = False
            self._phase = GamePhase.ROLL_EVENTS
            self.roll_events()

        elif self._phase == GamePhase.ROLL_EVENTS:
            self._phase = GamePhase.CITY_PROMPTS
            self.city_prompts()

        elif self._phase == GamePhase.CITY_PROMPTS:
            self._prompts_pending = False
            self._phase = GamePhase.RESOLVE_MOVES
            self.resolve_moves()

        elif self._phase == GamePhase.RESOLVE_MOVES:
            if self.game_over:
                self._phase = GamePhase.GAME_OVER
            else:
                self._phase = GamePhase.ROUND_START
                self.round_start()

        else:
            self._phase = GamePhase.ERROR
            return False

        return True

    def round_start(self) -> None:
        """Carry out the setup phase of a new round."""

        self._round += 1

    def sus_prompts(self) -> None:
        """Prompt governors to roll a Suspicious event."""

        for city in self._cities:
            if city.can_roll_suspicious(
                self._round, self.config.suspicious_cooldown
            ):
                governor = self.get_governor(city)
                if governor is not None:
                    self._prompts_pending = True
                    governor.prompt_suspicious()

    def roll_prompts(self):
        """Prompt players to input dice rolls """

        for player in self._players:
            if player.role == PlayerRole.TRAVELER:
                self._prompts_pending = True
                player.prompt_roll()
            elif player.role == PlayerRole.GOVERNOR and player.sus_prompt_response:
                self._prompts_pending = True
                player.prompt_roll()

    def roll_events(self) -> None:
        """Roll events for all players."""

        for player in self._players:
            if player.role == PlayerRole.TRAVELER:
                player.roll_next_event()
            elif player.role == PlayerRole.GOVERNOR:
                if player.sus_prompt_response or player.city.alerted:
                    player.roll_next_event()

    def city_prompts(self) -> None:
        """Prompt players to choose what city to move to."""

        for player in self._players:
            if player.next_event_choice and not player.role == PlayerRole.OBSERVER:
                self._prompts_pending = True
                player.prompt_city_choice()

    def update_city_state(self, city: City, state: CityState) -> CityState:
        """
        Determine the next state of a city.
        
        Args:
            city: The city to update.
            state: The current state of the city.
            
        Returns:
            The next state of the city.
        """

        # Copy the current state with updated values
        new = replace(
            state,
            conditions=(state.conditions.copy()
                if state.lockdown > 0
                else []),
            infection_pause=max(0, state.infection_pause - 1),
            lockdown=max(0, state.lockdown - 1),
            infection_stage=(
                min(state.infection_stage + 1, City.MAX_INFECTION_STAGE)
                if state.infection_stage > 0 and state.infection_pause == 0
                else state.infection_stage
            ),
        )

        # Resolve event if there is a governor
        governor = self.get_governor(city)
        if governor is not None:
            if governor.sus_prompt_response:
                new.last_sus_roll = self.round
            # Actions
            new.event = governor.next_event
            if new.event.action == "pause":
                new.infection_pause = new.event.amount
            elif new.event.action.startswith("survey") and new.alerted == False:
                new.alerted = City.survey(
                    state, new.event.action.endswith("adv")
                )
            elif new.event.action == "rollback":
                new.infection_stage = max(
                    0, state.infection_stage - new.event.amount
                )

            # Conditions
            if new.event.condition == "lockdown":
                new.lockdown = self.config.lockdown_duration
                new.conditions = ["harbor", "road", "merch"]
            elif new.event.condition is not None:
                new.conditions.append(new.event.condition)
        else: #QUESTION should more AI logic happen for ungoverned cities?
            pass
            #If there is no player governor survey for infections after a threshold
            #if state.infection_stage > 0 and state.infection_pause == 0 and new.alerted == False:
            #    if state.infection_stage >= self.config.survey_threshold:
            #        new.alerted = City.survey(state, False)

        return new

    def update_player_state(
                self,
                current_player: PlayerState,
                dest: City,
                dest_state: CityState,
            ) -> tuple[PlayerState, CityState]:
        """
        Determine the next state of a player and the city they are moving to.

        Args:
            current_player: The current state of the player.
            dest: The city the player is moving to.
            dest_state: The next state of the destination city.

        Returns:
            A tuple containing the next state of the player and the city.
        """

        # Copy the current player state with updated values
        new = replace(current_player, city=dest)

        # Resolve traveler move
        if current_player.role == PlayerRole.TRAVELER:
            # Move to the next city
            assert new.city is not None
            # Update health status
            if (
                current_player.health == InfectionState.HEALTHY
                and dest.infection_stage > 0
            ):
                new.health = InfectionState.ASYMPTOMATIC
                new.infected_round = self._round
            elif current_player.health in (InfectionState.ASYMPTOMATIC, InfectionState.SYMPTOMATIC):
                assert current_player.infected_round is not None
                roll = random.randint(1, 100)
                if self._round - current_player.infected_round <= 4:
                    if roll > 50 and dest_state.infection_stage == 0:
                        dest_state.infection_stage += 1
                elif self._round - current_player.infected_round <= 9:
                    if dest_state.infection_stage == 0:
                        dest_state.infection_stage += 1
                    if 40 < roll <= 87:
                        new.health = InfectionState.SYMPTOMATIC
                    elif roll > 87:
                        new.health = InfectionState.DEAD
                else:
                    if dest_state.infection_stage == 0:
                        dest_state.infection_stage += 1
                    if roll <= 50:
                        new.health = InfectionState.IMMUNE
                    else:
                        new.health = InfectionState.DEAD

        return new, dest_state

    def reassign_players(
                self,
                dead_players: dict[Player, PlayerState],
                cities: dict[City, CityState],
            ) -> tuple[dict[Player, PlayerState], dict[City, CityState]]:
        """
        Reassign newly dead players to a new role.

        Args:
            dead_players: A dictionary of dead players and their states.
            cities: A dictionary of cities and their states.

        Returns:
            A pair of dictionaries containing the updated states of the players and cities.
        """
        open_cities = list(cities.keys())
        for player in self._players:
            if player.role == PlayerRole.GOVERNOR:
                assert player.city is not None
                open_cities.remove(player.city)

        for player, state in dead_players.items():
            if len(open_cities) == 0:
                state.role = PlayerRole.OBSERVER
                state.city = None
                continue
            state.role = PlayerRole.GOVERNOR
            if state.city in open_cities:
                open_cities.remove(state.city)
            else:
                state.city = open_cities.pop()

        return dead_players, cities

    def resolve_moves(self) -> None:
        """Resolve the moves of all players in the game."""

        # Update city states
        new_city_states = {
            city: self.update_city_state(
                city, city.state
            ) for city in self._cities
        }

        # Update player states
        new_player_states = dict()
        for player in self._players:
            if player.role == PlayerRole.OBSERVER or player.role == PlayerRole.GOVERNOR:
                continue

            dest = player.city_move_destination(self._cities)
            assert dest is not None
            new_player_states[player], new_city_states[dest] = \
                self.update_player_state(
                    player.state, dest, new_city_states[dest]
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
            state.event = player.next_event
            player.add_state(state)
        for player in self._players:
            player.reset()
        for city, state in new_city_states.items():
            city.add_state(state)
