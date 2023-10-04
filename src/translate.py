import os.path
from pathlib import Path

from token_mappings import get_token_mappings

DIRECTORY_PATH = "translations"
FILE_EXTENSION = ".tsv"


def get_available_translations() -> list[str]:
    return [file_path.stem for file_path in Path(DIRECTORY_PATH).glob(f"*{FILE_EXTENSION}")]


def translate_token(token: str, system: str) -> str:
    return get_token_mappings(os.path.join(DIRECTORY_PATH, f"{system}{FILE_EXTENSION}"))[token]
