"""Console-based interface for the game."""

from findpatientzero.engine.game import Game, GameConfig


def main():
    # Get human players
    player_names = ["Lock", "Richardson", "Beckett", "Bea", "Ryan", "Wolf"] #temp for testing
    #while True:
    #    name = input("Enter player name (or press Enter to finish): ")
    #    if name == "":
    #        break
    #    player_names.append(name)

    # Get number of CPU players
    # while True:
    #     num_cpu = input("Enter number of CPU players (default 6): ")
    #     if num_cpu == "":
    #         num_cpu = 6
    #         break
    #     try:
    #         num_cpu = int(num_cpu)
    #         break
    #     except ValueError:
    #         print("Please enter a valid number.")

    # Get number of cities
    # while True:
    #     num_cities = input(
    #         f"Enter number of cities (default {len(player_names)}): " #+CPU players
    #         )
    #     if num_cities == "":
    #         num_cities = len(player_names)# + num_cpu
    #         break
    #     try:
    #         num_cities = int(num_cities)
    #         break
    #     except ValueError:
    #         print("Please enter a valid number.")

    num_cities = len(player_names) # temp for testing
    # Create a new game control object
    try:
        config = GameConfig(num_players=len(player_names), num_cities=num_cities)
        game = Game(config, player_names)
    except ValueError as e:
        print(e)
        return

    game.game_start()
    print(game)

if __name__ == "__main__":
    main()
