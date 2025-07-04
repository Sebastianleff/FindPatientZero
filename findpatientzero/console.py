"""Console-based interface for the game."""

from findpatientzero.engine.game import Game, GameConfig, GamePhase

yes_no_map = {
    "yes": True,
    "y": True,
    "no": False,
    "n": False,
}

def format_event(player) -> str:
    """Return the event flavor text with player-specific information."""

    output = player.next_event.description
    if "$CITY$" in output:
        output = output.replace("$CITY$", player.city.name)
    if "$PLAYER$" in output:
        output = output.replace("$PLAYER$", player.name)
    if "$GOVERNOR$" in output:
        output = output.replace("$GOVERNOR$", player.city.governor.name)

    return output

def wait_for_enter(prompt):
    while True:
        if input(prompt) == "":
            break

def main():

    game_master_mode = False

    # Get human players
    player_names = []
    while True:
       name = input("Enter player name (or press Enter to finish): ")
       if name == "":
           break
       player_names.append(name)

    # Get number of CPU players
    while True:
        num_cpu = input("Enter number of CPU players (default 6): ")
        if num_cpu == "":
            num_cpu = 6
            break
        try:
            num_cpu = int(num_cpu)
            break
        except ValueError:
            print("Please enter a valid number.")

    # Get number of cities
    while True:
        num_cities = input(
            f"Enter number of cities (default {len(player_names)}): " #+CPU players
            )
        if num_cities == "":
            num_cities = len(player_names)# + num_cpu
            break
        try:
            num_cities = int(num_cities)
            break
        except ValueError:
            print("Please enter a valid number.")

    #Set game master mode
    while True:
        prompt = "Do you want to turn on Game Master mode (Shows who is patient zero)? Yes or No: "
        user_response = input(prompt).strip()
        try:
            game_master_mode = (yes_no_map[user_response.lower()])
            break
        except KeyError:
            print("Invalid input. Try again.")

    # Create a new game control object
    try:
        config = GameConfig(num_players=len(player_names), num_cities=num_cities)
        game = Game(config, player_names)
    except ValueError as e:
        print(e)
        return

    game_over = False

    while not game_over:
        if game.phase == GamePhase.ROUND_START:
            if not game_master_mode:
                print(
                    "\n"
                    + f"Round {game.round} start"
                    + "\n\nPLAYERS"
                    + "".join(f"\n\tPlayer {i + 1}: {player} (City: {player.city})" for i, player in
                              enumerate(game.players))
                )
            else:
                print(
                    "\n"
                    + f"Round {game.round} start"
                    + f"\n\nPatient Zero: {game.patient_zero}"
                    + "\n\nPLAYERS"
                    + "".join(
                        f"\n\tPlayer {i + 1}: {player} (Health: {player.health.value}, City: {player.city})"
                        for i, player in enumerate(game.players)
                    )
                    + "\n\nCITIES"
                    + "".join(
                        f"\n\tCity {i + 1}: {city} (Infection: {city.infection_stage})"
                        for i, city in enumerate(game.cities)
                    )
                )
            wait_for_enter("\nPress Enter to continue round...")

        elif game.phase == GamePhase.SUS_PROMPTS and game.prompts_pending:
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

        elif game.phase == GamePhase.ROLL_EVENTS:
            print("\nEvents:")
            for player in game.players:
                if not player.next_event_choice:
                    print(
                        f"{player.name} - {format_event(player)}"
                    )

        elif game.phase == GamePhase.CITY_PROMPTS and game.prompts_pending:
            for player in game.players:
                if player.pending_city_prompt:
                    city_list = player.city_options(game.cities)
                    prompt = (
                            f"{player.name} - {format_event(player)} Type City name or Number in list:\n" #QUESTION can you choose to stay in current city or must move to new one? and should prompt say move to uninfected city, gives  away which city is infected?
                            + "\n".join(f"{idx}: {city}" for idx, city in enumerate(city_list, 1))
                            + f"\nCurrent City: {player.city}"
                            + "\nInput: "
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

        game.go_to_next_phase()
        game_over = game.phase == GamePhase.GAME_OVER
        assert game.phase != GamePhase.ERROR

    print("Game over")

if __name__ == "__main__":
    main()
