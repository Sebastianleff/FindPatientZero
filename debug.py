"""This file should be used to debug the project. It is not intended to be
used in the final product."""

from findpatientzero.engine.entities.event import EVENTS

if __name__ == "__main__":
    for category, event_list in EVENTS.items():
        print(f"=={category.value.upper()}==")
        for event in event_list:
            print(f"\t{event}")
        print()
