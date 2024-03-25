import random

from gamedata.load import load_data
from engine.states import *


class Player:
    name: str
    """The name of the player."""

    history: list[PlayerState]

    def __init__(self, name: str) -> None:
        self.name = name
    
    def __str__(self) -> str:
        return self.name


class CPUPlayer(Player):
    names: list[str] = load_data('gamedata/cpu_names.txt')

    def __init__(self) -> None:
        index = random.randint(0, len(CPUPlayer.names) - 1)
        super().__init__(CPUPlayer.names.pop(index))

    def __str__(self) -> str:
        return f"{self.name} (CPU)"



class City:

    names: list[str] = load_data('gamedata/city_names.txt')

    name: str
    """The name of the city."""

    state: CityState
    """The state of the city."""

    governor: Player|None
    """The player who is currently the governor of the city."""

    def __init__(self) -> None:
        index = random.randint(0, len(City.names) - 1)
        self.name = City.names.pop(index)
        self.state = CityState()
        self.governor = None

    def __str__(self) -> str:
        if self.governor is not None:
            return f"{self.name} (Governor: {self.governor})"
        return self.name


class GameControl:
    MIN_PLAYERS = 2
    """The minimum number of players in a game."""

    MIN_CITIES = 2
    """The minimum number of cities in a game."""

    round: int
    """The current round number of the game."""

    players: list[Player]
    """The list of players in the game."""

    cities: list[City]
    """The list of cities in the game."""

    patient_zero: Player
    """The player who is patient zero of the epidemic."""

    def __init__(self, player_names: list[str], num_cpu: int, num_cities: int) -> None:
        if len(player_names) + num_cpu < GameControl.MIN_PLAYERS:
            raise ValueError(f"Must have at least {self.MIN_PLAYERS} players.")
        elif num_cities < GameControl.MIN_CITIES:
            raise ValueError(f"Must have at least {self.MIN_CITIES} cities.")
        
        self.round = 0
        self.players = [Player(name) for name in player_names]
        self.players += [CPUPlayer() for _ in range(num_cpu)]
        self.cities = [City() for _ in range(num_cities)]
        self.patient_zero = random.choice(self.players)
    
    def round_start(self) -> None:
        self.round += 1
        # Roll player events
    
    def __str__(self) -> str:
        output = "PLAYERS"
        for i, player in enumerate(self.players):
            output += f"\n\tPlayer {i+1}: {player}"
        output += f"\n\nCITIES"
        for i, city in enumerate(self.cities):
            output += f"\n\tCity {i+1}: {city}"
        output += f"\n\nPatient Zero: {self.patient_zero}"

        return output
