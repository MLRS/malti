TOKEN_MAPPINGS = {}


def get_token_mappings(path: str) -> dict[str, str]:
    if path not in TOKEN_MAPPINGS:
        with open(path, "r", encoding="utf-8") as file:
            mappings = {}
            for line in file:
                token, mapping = line.strip().split("\t")
                mappings[token] = mapping
            TOKEN_MAPPINGS[path] = mappings
    return TOKEN_MAPPINGS[path]
