CONFIRMATION_VALUES = ["confirm", "conf", "accept", "acc"]


def confirm_conv(value: str, /) -> bool:
    return True if value.lower().strip() in CONFIRMATION_VALUES else False
