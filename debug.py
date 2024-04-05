from engine.entities.event import load_events

if __name__ == "__main__":
    events = load_events()
    for category, event_list in events.items():
        print(f"{category.upper()} events:")
        for event in event_list:
            print(event)
        print()
