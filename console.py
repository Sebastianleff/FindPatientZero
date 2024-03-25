from engine.engine import GameControl


def main():
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
        num_cities = input(f"Enter number of cities (default {len(player_names) + num_cpu}): ")
        if num_cities == "":
            num_cities = len(player_names) + num_cpu
            break
        try:
            num_cities = int(num_cities)
            break
        except ValueError:
            print("Please enter a valid number.")
        


    # Create a new game control object
    try: 
        game = GameControl(player_names, num_cpu, num_cities)
    except ValueError as e:
        print(e)
        return
    
    print(game)

if __name__ == "__main__":
    main()
