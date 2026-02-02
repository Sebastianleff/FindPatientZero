"""Console-based interface for the game."""
import random
from findpatientzero.engine.entities.player import InfectionState
from findpatientzero.engine.game import Game, GameConfig, GamePhase
from findpatientzero.gamedata.load import load_console_text

console_text = load_console_text()
yes_no_map = console_text["yes_no_map"]
wrongly_accused_traveler = console_text["wrongly_accused_traveler"]
wrongly_accused_governor = console_text["wrongly_accused_governor"]
wrongly_accused_observer = console_text["wrongly_accused_observer"]


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

    print("\n\033[1mLoading The Deaths And Remnants of the Warfare Inherent to Nature...\033[0m\n")

    game_over = False
    deliberation_round_counter = 0

    # Get human players
    player_names = []
    while True:
        name = input("Enter player name (or press Enter to finish): ")
        if name == "":
            if len(player_names) >= 1:
                break
            else:
                print("Please enter at least 1 name.")
                continue
        player_names.append(name)

    # Get a number of CPU players
    while True:
        num_cpu = input("Enter number of AI players (default 6): ")
        if num_cpu == "":
            num_cpu = 6
            break
        if len(player_names) <= 1 and int(num_cpu) <= 0:
            num_cpu = 1
            break
        try:
            num_cpu = int(num_cpu)
            break
        except ValueError:
            print("Please enter a valid number.")

    # Get number of cities
    while True:
        num_cities = input(
            f"Enter number of cities (default {len(player_names) + + num_cpu}): "
            )
        if num_cities == "":
            num_cities = len(player_names) + num_cpu
            break
        try:
            num_cities = int(num_cities)
            break
        except ValueError:
            print("Please enter a valid number.")

    #Choose if game master mode is on or off
    while True:
        prompt = "Do you want to turn on Game Master mode (Shows who is patient zero)? Yes or No: "
        user_response = input(prompt).strip()
        try:
            game_master_mode = (yes_no_map[user_response.lower()])
            break
        except KeyError:
            print("Invalid input. Try again.")

    #Choose if dice rolls are automatic
    while True:
        prompt = "Do you want to turn on manual dice rolls (Requires manually inputting numbers rolled by players with D100s)? Yes or No: "
        user_response = input(prompt).strip()
        try:
            #Invert response to match internal logic, while still having sensible prompt phrasing
            roll_response = not (yes_no_map[user_response.lower()])
            break
        except KeyError:
            print("Invalid input. Try again.")

    #Choose to show events for CPU players if more then 0
    if num_cpu > 0:
        while True:
            prompt = "Do you want to show events taken by AI players? (Yes or No): "
            user_response = input(prompt).strip()
            try:
                ai_events = (yes_no_map[user_response.lower()])
                break
            except KeyError:
                print("Invalid input. Try again.")
    else:
        ai_events = False

    #Choose if there will be a deliberation round
    while True:
        prompt = "Do you want to have the deliberation round? (Yes or No): "
        user_response = input(prompt).strip()
        try:
            deliberation_round = (yes_no_map[user_response.lower()])
            break
        except KeyError:
            print("Invalid input. Try again.")

    if deliberation_round:
        while True:
            deliberation_round_frequency = input("How often should the deliberation round be? (Default 4): ")
            if deliberation_round_frequency == "":
                deliberation_round_frequency = 4
                break
            try:
                deliberation_round_frequency = int(deliberation_round_frequency)
                break
            except ValueError:
                print("Please enter a valid number.")
    else:
        deliberation_round_frequency = 0


    # Create a new game control object
    try:
        config = GameConfig(num_players=len(player_names) + num_cpu, num_cities=num_cities, auto_roll=roll_response)
        game = Game(config, player_names)
    except ValueError as e:
        print(e)
        return

    print("\n\033[1mD.A.R.W.I.N. Online\033[0m")

    while not game_over:
        if game.phase == GamePhase.ROUND_START:
            deliberation_round_counter += 1
            wait_for_enter("\nPress Enter to start round...")
            if not game_master_mode:
                print(
                    "\n"
                    + f"Round {game.round} start"
                    + "\n\nPLAYERS"
                    + "".join(f"\n\t{player} (Role: {player.role.value}, City: {player.city})" for i, player in
                              enumerate(game.players))
                    + "\n\nCITIES"
                    + "".join(
                        f"\n\t{city} (Alerted: {city.alerted})"
                        for i, city in enumerate(game.cities)
                    )
                )
            else:
                print(
                    "\n"
                    + f"Round {game.round} start"
                    + f"\n\nPatient Zero: {game.patient_zero}"
                    + "\n\nPLAYERS"
                    + "".join(
                        f"\n\t{player} (Health: {player.health.value}, City: {player.city})"
                        for i, player in enumerate(game.players)
                    )
                    + "\n\nCITIES"
                    + "".join(
                        f"\n\t{city} (Infection: {city.infection_stage}, Alerted: {city.alerted} )"
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

        elif game.phase == GamePhase.ROLL_DICE and game.prompts_pending:
            for player in game.players:
                if player.roll_prompt_pending:
                    prompt = (player.name + " - Roll for your next event. Number between 1 and 100: ")
                    while True:
                        user_response = input(prompt).strip()
                        try:
                            roll = int(user_response)
                            if not 1 <= roll <= 100:
                                raise ValueError
                            player.respond_roll(roll)
                            break
                        except ValueError:
                            print("Invalid input. Try again.")

        elif game.phase == GamePhase.ROLL_EVENTS:
            print("\nEvents:")
            for player in game.players:
                if ai_events or not player.is_cpu:
                    if not player.next_event_choice:
                        print(
                            f"{player.name} - {format_event(player)}"
                        )

        elif game.phase == GamePhase.CITY_PROMPTS and game.prompts_pending:
            for player in game.players:
                if player.pending_city_prompt:
                    city_list = player.city_options(game.cities)
                    prompt = (
                            f"{player.name} - {format_event(player)} Type City name or Number in list:\n"
                            + f"Current City: {player.city}\n"
                            + "\n".join(f"{idx}: {city}" for idx, city in enumerate(city_list, 1))
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

        elif (game.phase == GamePhase.GUESS_PATIENT_ZERO
            and deliberation_round == True
            and deliberation_round_frequency <= deliberation_round_counter):
            if any(player.state.health in (InfectionState.SYMPTOMATIC, InfectionState.DEAD, InfectionState.IMMUNE)
                   for player in game.players):
                deliberation_round_counter = 0
                prompt = (
                        "\nPlease guess which player is Patient Zero, press enter to skip guessing.\n"
                        + "\n".join(f"{idx}: {player}" for idx, player in enumerate(game.players, 1))
                        + "\nInput: "
                )
                while True:
                    user_response = input(prompt).strip()
                    if user_response == "":
                        break
                    chosen_player = next(
                        (player for player in game.players if str(player).lower() == user_response.lower()), None)
                    if chosen_player is None:
                        try:
                            chosen_player = game.players[int(user_response) - 1]
                        except (ValueError, IndexError):
                            pass
                    if chosen_player:
                        game.patient_zero_suspect = chosen_player
                        #NOTE game logic does not recognize player death until after resolve, this is flavor text only
                        #it should stay current to game logic in current form, but if refactored double check
                        if not game.suspect_is_patient_zero:
                            if game.patient_zero_suspect.is_traveler:
                                print(f"{chosen_player.name} {random.choice(wrongly_accused_traveler)}"
                                      f"\nThey were not Patient Zero.")
                            elif game.patient_zero_suspect.is_governor:
                                print(f"{chosen_player.name} {random.choice(wrongly_accused_governor)}"
                                      f"\nThey are not Patient Zero.")
                            elif game.patient_zero_suspect.is_observer:
                                print(f"{chosen_player.name} {random.choice(wrongly_accused_observer)}"
                                      f"\nThey were not Patient Zero.")
                        break
                    else:
                        print("Invalid input. Try again.")

        elif game.phase == GamePhase.GAME_OVER:
            if game.all_dead:
                print("\nGame over. You all succumbed to plague")
            elif game.all_immune:
                print("\nGame over. You are all immune to plague, you got lucky")
            elif game.suspect_is_patient_zero:
                print("\nGame over. You found out who is Patient Zero")
            else:
                print("\nGame over. \nSurvivors with immunity: " +
                      ", ".join(player.name for player in game.players if player.state.health == InfectionState.IMMUNE))
                print("Players who died: " +
                      ", ".join(player.name for player in game.players if player.state.health == InfectionState.DEAD))
            break


        game.go_to_next_phase()
        assert game.phase != GamePhase.ERROR

    print("\n\033[1mD.A.R.W.I.N. Offline\033[0m")
    print("Thank you for playing.\nGame Design by Anastasio Bonhomme\nPrograming and Software Design"
          " by Valentina Proskauer Valerio and Sebastian Leff")
    wait_for_enter("\nPress Enter to end game.")

if __name__ == "__main__":
    main()
