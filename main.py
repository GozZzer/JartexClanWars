import os
from clanwars import run_gateway_bot

if os.name != "nt":
    import uvloop
    uvloop.install()

if __name__ == "__main__":
    run_gateway_bot()
