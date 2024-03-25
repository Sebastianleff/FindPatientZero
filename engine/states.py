class PlayerState:
    pass

class CityState:
    pass

class GameState:
    round: int
    """The current round number of the game."""
    cities: list[CityState]
    """The list of cities in the game."""
