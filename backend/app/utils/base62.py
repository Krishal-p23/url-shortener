"""Base62 encoding utilities for compact URL identifiers."""

import string


ALPHABET = string.digits + string.ascii_uppercase + string.ascii_lowercase
BASE = len(ALPHABET)


def encode_base62(value: int) -> str:
    """Encode a non-negative integer as a compact Base62 string."""

    if value < 0:
        raise ValueError("Base62 encoding requires a non-negative integer")
    if value == 0:
        return ALPHABET[0]

    characters: list[str] = []
    remaining = value
    while remaining:
        remaining, remainder = divmod(remaining, BASE)
        characters.append(ALPHABET[remainder])
    return "".join(reversed(characters))


def decode_base62(value: str) -> int:
    """Decode a Base62 string into its non-negative integer value."""

    if not value:
        raise ValueError("Base62 decoding requires a non-empty string")

    result = 0
    for character in value:
        try:
            digit = ALPHABET.index(character)
        except ValueError as error:
            raise ValueError(f"Invalid Base62 character: {character}") from error
        result = result * BASE + digit
    return result