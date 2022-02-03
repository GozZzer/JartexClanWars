import json


def get_config() -> dict:
    return json.load(open("clanwars/config.json", "r"))

