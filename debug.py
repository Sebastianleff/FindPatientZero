from engine.entities.event import EVENTS

if __name__ == "__main__":
    for category, event_list in EVENTS.items():
        print(f"=={category.upper()}==")
        for event in event_list:
            print(f"\t{event}")
        print()
