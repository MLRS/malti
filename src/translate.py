import os.path

from token_mappings import get_token_mappings

DIRECTORY_PATH = "translations"
FILE_EXTENSION = ".tsv"


def translate_token(token: str, system: str) -> str:
    return get_token_mappings(os.path.join(DIRECTORY_PATH, f"{system}{FILE_EXTENSION}"))[token]
