import os
from yaml import safe_load as load  # type: ignore

_cwd = os.path.join(os.path.dirname(__file__))
_event_dir = os.path.join(_cwd, 'events')


def _load_file(file: str) -> list[str] | dict[str, str]:
    with open(file, 'r') as f:
        data = load(f)
    return data


def load_cpu_names() -> list[str]:
    return _load_file(os.path.join(_cwd, 'cpu_names.yml'))


def load_city_names() -> list[str]:
    return _load_file(os.path.join(_cwd, 'city_names.yml'))


def load_event_types(key: str) -> list[dict[str, str | int]]:
    return _load_file(
        os.path.join(_event_dir, 'event_types', f"{key}.yml")
    )['event_types']


def load_conditions(key: str) -> list[dict[str, str]]:
    return _load_file(
        os.path.join(_event_dir, 'conditions', f"{key}.yml")
    )['conditions']


def load_events(key: str) -> list[dict[str, str | int]]:
    loaded = _load_file(
        os.path.join(_event_dir, f"{key}.yml")
    )
    return loaded['events']
