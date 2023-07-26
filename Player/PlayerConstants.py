from enum import Enum

class PlayerConstants(Enum):
    IN_GAME = "in_game"
    PRESSING_BUTTON = "pressing_button"
    WAITING_MSG = "waiting_msg"
    PROMPT = "prompt"
    LIE = "lie"
    NEXT_LIE = "next_lie"
    HAS_VOTED = "has_voted"
    ARCADE_PROMPT_LIST = "arcade_prompt_list"
    ARCADE_GEN_STRING = "arcade_gen_string"
    BANNED_CATEGORY = "banned_category"
    NEXT_CAPTION = "next_caption"
    CAPTION = "caption"
    HAS_PICKED = "has_picked"
    ARCADE_IMAGE = "arcade_image"