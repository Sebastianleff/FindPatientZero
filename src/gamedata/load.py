import os
from yaml import safe_load as load

from src.gamedata.schema import (
    ConditionData,
    ConditionList,
    EventData,
    EventList,
    EventTypeData,
    EventTypeList,
    NameList,
)

_cwd = os.path.join(os.path.dirname(__file__))
_event_dir = os.path.join(_cwd, "events")


def _load_file(file: str):
    with open(file, "r") as f:
        data = load(f)
    return data


def load_cpu_names() -> NameList:
    return _load_file(os.path.join(_cwd, "cpu_names.yml"))


def load_city_names() -> NameList:
    return _load_file(os.path.join(_cwd, "city_names.yml"))


def load_event_types(key: str) -> list[EventTypeData]:
    loaded: EventTypeList = _load_file(
        os.path.join(_event_dir, "event_types", f"{key}.yml")
    )
    return loaded["event_types"]


def load_conditions(key: str) -> list[ConditionData]:
    loaded: ConditionList = _load_file(
        os.path.join(_event_dir, "conditions", f"{key}.yml")
    )
    return loaded["conditions"]


def load_events(key: str) -> list[EventData]:
    loaded: EventList = _load_file(os.path.join(_event_dir, f"{key}.yml"))
    return loaded["events"]
