"""Defines the schema for the game data files."""

from typing import Required, NotRequired, TypedDict


# Define the schema for name lists
NameList = list[str]


# Define the schema for event type lists
class EventTypeData(TypedDict):
    action: Required[str]
    amount: NotRequired[int]
    description: Required[str]


class EventTypeList(TypedDict):
    event_types: Required[list[EventTypeData]]


# Define the schema for condition lists
class ConditionData(TypedDict):
    name: Required[str]
    description: Required[str]


class ConditionList(TypedDict):
    conditions: Required[list[ConditionData]]


# Define the schema for event lists
class EventData(TypedDict):
    description: Required[str]
    action: Required[str]
    amount: NotRequired[int]
    frequency: Required[int]
    condition: NotRequired[str]


class EventList(TypedDict):
    events: Required[list[EventData]]
