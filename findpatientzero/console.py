"""Console-based interface for the game."""

from findpatientzero.engine.game import Game, GameConfig, GamePhase

yes_no_map = {
    "yes": True,
    "y": True,
    "no": False,
    "n": False,
}

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

    game_over = False

    while not game_over:
        # TODO refactor so inputs are taken to game class first before being passed to players
        if game.phase == GamePhase.SUS_PROMPTS and game.prompts_pending:
            for player in game.players:
                if player.sus_prompt_pending:
                    prompt = (player.name + " - Do you want to roll for a suspicion event? Yes or No: ")
                    while True:
                        user_response = input(prompt).strip()
                        try:
                            player.respond_suspicious(yes_no_map[user_response.lower()])
                            break
                        except KeyError:
                            print("Invalid input. Try again.")

        elif game.phase == GamePhase.CITY_PROMPTS and game.prompts_pending:
            for player in game.players:
                if player.pending_city_prompt:
                    city_list = player.city_options(game.cities)
                    prompt = (
                            f"{player.name} - What city do you want to move to? Type City name or Number in list:\n"
                            + "\n".join(f"{idx}: {city}" for idx, city in enumerate(city_list, 1))
                            + "\n"
                    )
                    while True:
                        user_response = input(prompt).strip()
                        chosen_city = next((city for city in city_list if str(city).lower() == user_response.lower()), None)
                        if chosen_city is None:
                            try:
                                chosen_city = city_list[int(user_response) - 1]
                            except (ValueError, IndexError):
                                pass
                        if chosen_city:
                            player.respond_city_choice(chosen_city)
                            break
                        else:
                            print("Invalid input. Try again.")


        # Other phases: game logic only, no user input
        game.go_to_next_phase()
        assert game.phase != GamePhase.ERROR

if __name__ == "__main__":
    main()
