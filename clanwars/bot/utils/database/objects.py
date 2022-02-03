import datetime
from dataclasses import dataclass
from typing import List


@dataclass
class Clan:
    clan_name: str
    owner_id: int
    elo: int
    proof: str
    accepted: bool
    clan_alias: str
    members: List[int]
    enabled: bool
    deleted: bool
    role: int


@dataclass
class Game:
    game_id: int
    message_id: int
    text_channel_id: int
    voice_channel_1: int
    voice_channel_2: int
    clan_1: str
    clan_2: str
    clan_1_members: List[int]
    clan_2_members: List[int]
    winner: str
    submitted: bool
    scored: bool
    left: List[str]
    proof: str


@dataclass
class Member:
    user_id: int
    ign: str
    other_igns: List[str]
    clan: str


@dataclass
class User:
    user_id: int
    joined: datetime.datetime
    left: datetime.datetime
    available: bool
    active: bool
    admin: bool
    register: bool
    score: bool