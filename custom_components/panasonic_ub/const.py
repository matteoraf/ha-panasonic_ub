"""Constants for the Panasonic UB Blu-ray integration."""

from typing import Final

DOMAIN: Final = "panasonic_ub"
CONF_KEY: Final = "secret_key"
CONF_AUTH_ENABLE: Final = "auth_enable"
CONF_POLL_INTERVAL: Final = "poll_interval"

DEFAULT_NAME: Final = "Panasonic Blu-ray"
DEFAULT_POLL_INTERVAL: Final = 30  # Seconds
DEFAULT_SECRET_KEY: Final = "0" * 32

# Mapping of Home Assistant commands to Internal Device Protocol (RC) Codes
COMMAND_MAPPING: Final = {
    # --- Power ---
    "POWER_ON": "RC_POWERON",
    "POWER_OFF": "RC_POWEROFF",
    # --- Transport ---
    "PLAY": "RC_PLAYBACK",
    "STOP": "RC_STOP",
    "PAUSE": "RC_PAUSE",
    "SKIP_FWD": "RC_SKIPFWD",
    "SKIP_REV": "RC_SKIPREV",
    "SCAN_FWD": "RC_CUE",  # Fast Forward
    "SCAN_REV": "RC_REV",  # Rewind
    "OPEN_CLOSE": "RC_OP_CL",
    # --- Navigation ---
    "UP": "RC_UP",
    "DOWN": "RC_DOWN",
    "LEFT": "RC_LEFT",
    "RIGHT": "RC_RIGHT",
    "ENTER": "RC_SELECT",
    "RETURN": "RC_RETURN",
    "INFO": "RC_DSPSEL",  # "Status" / Display Info
    "HOME": "RC_MLTNAVI",  # "Home" Menu
    "OPTION": "RC_MENU",  # "Option" Menu
    "TOP_MENU": "RC_TITLE",
    "POPUP_MENU": "RC_PUPMENU",
    "CLEAR": "RC_CLEAR",
    # --- Color Buttons ---
    "RED": "RC_RED",
    "GREEN": "RC_GREEN",
    "YELLOW": "RC_YELLOW",
    "BLUE": "RC_BLUE",
    # --- Numbers ---
    "DIGIT_0": "RC_D0",
    "DIGIT_1": "RC_D1",
    "DIGIT_2": "RC_D2",
    "DIGIT_3": "RC_D3",
    "DIGIT_4": "RC_D4",
    "DIGIT_5": "RC_D5",
    "DIGIT_6": "RC_D6",
    "DIGIT_7": "RC_D7",
    "DIGIT_8": "RC_D8",
    "DIGIT_9": "RC_D9",
    "DOT": "RC_SHARP",  # The "." or "*" key
    # --- Special Features ---
    "AUDIO": "RC_AUDIOSEL",
    "SUBTITLE": "RC_TITLEONOFF",
    "HDR_SETTING": "RC_HDR_PICTUREMODE",
    "NETFLIX": "RC_NETFLIX",
    "INTERNET": "RC_V_CAST",
    "MIRRORING": "RC_MIRACAST",
    "SETUP": "RC_SETUP",
    "PLAYBACK_INFO": "RC_PLAYBACKINFO",
    "MANUAL_SKIP_MINUS_10": "RC_MNBACK",
    "MANUAL_SKIP_PLUS_60": "RC_MNSKIP",
    "CLOSED_CAPTION": "RC_CLOSED_CAPTION",
    "PICTURE_SETTING": "RC_PICTURESETTINGS",
    "SOUND_EFFECT": "RC_SOUNDEFFECT",
    "HIGH_CLARITY": "RC_HIGHCLARITY",
    # --- Polling Commands ---
    "STATUS": "REVIEW",
    "TIME": "PST",
}

# Status Codes returned by the device in the REVIEW command
STATUS_MAPPING: Final = {
    "00": "STOPPED",
    "01": "TRAY_OPEN",
    "02": "REV_PLAYBACK",
    "05": "CUE_PLAYBACK",
    "06": "SLOW_FORWARD",
    "07": "POWER_OFF",
    "08": "PLAYBACK",
    "09": "PAUSED",
    "86": "SLOW_BACKWARD",
}
