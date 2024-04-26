import random

from engine.entities.city import City, CityState
from engine.entities.player import CPUPlayer, Player, PlayerState


class GameConfig:
    """The configuration of a game."""

    MIN_PLAYERS = 2
    """The minimum number of players in a game."""

    MIN_CITIES = 2
    """The minimum number of cities in a game."""

    num_players: int
    """The number of players in the game."""

    num_cities: int
    """The number of cities in the game."""

    suspicious_cooldown: int
    """The number of rounds before a Suspicious event can be rolled again."""

    def __init__(
        self,
        num_players: int,
        num_cities: int,
        suspicious_cooldown: int = 3,
    ) -> None:
        if num_players < GameConfig.MIN_PLAYERS:
            raise ValueError(f"Must have at least {self.MIN_PLAYERS} players.")
        elif num_cities < GameConfig.MIN_CITIES:
            raise ValueError(f"Must have at least {self.MIN_CITIES} cities.")
        self.num_players = num_players
        self.num_cities = num_cities
        self.suspicious_cooldown = suspicious_cooldown


class GameState:
    round: int
    """The current round number of the game."""

    players: list[PlayerState]
    """The states of each player in the game."""

    cities: list[CityState]
    """The states of each city in the game."""


class Game:

    config: GameConfig
    """The configuration of the game."""

    round: int
    """The current round number of the game."""

    _players: list[Player]
    """The list of players in the game."""

    _cities: list[City]
    """The list of cities in the game."""

    @property
    def players(self) -> list[Player]:
        """The list of players in the game."""
        return self._players

    @property
    def cities(self) -> list[City]:
        """The list of cities in the game."""
        return self._cities

    _history: list[GameState]
    """The history of the game's states."""

    patient_zero: Player
    """The player who is patient zero of the epidemic."""

    def __init__(self, config: GameConfig, player_names: list[str]):

        self.round = 0
        self.players = [Player(name) for name in player_names]
        self.players += [
            CPUPlayer() for _ in range(config.num_players - len(player_names))
        ]
        self.cities = [City() for _ in range(config.num_cities)]
        self.patient_zero = random.choice(self.players)

    # TODO Function to indicate next phase?

    def round_start(self) -> None:
        self.round += 1
        # Determine which Governors can roll a Suspicious event
        for city in self.cities:
            if city.can_roll_suspicious(self.round, self.config):
                city.governor.prompt_suspicious()

        # wait for player input... (frontend implementation should use
        # respond_suspicious())

        # Roll all events once all players have made their decisions
        # (Events are pre-rolled by the backend)

        # Check events for required city choice prompts

        # Wait for player input again

        # Resolve moves

    def __str__(self) -> str:
        output = "PLAYERS"
        for i, player in enumerate(self.players):
            output += f"\n\tPlayer {i+1}: {player}"
        output += "\n\nCITIES"
        for i, city in enumerate(self.cities):
            output += f"\n\tCity {i+1}: {city}"
        output += f"\n\nPatient Zero: {self.patient_zero}"

        return output
