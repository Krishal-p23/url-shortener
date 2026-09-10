import pytest

from app.utils.base62 import decode_base62, encode_base62


@pytest.mark.parametrize("value", [0, 1, 61, 62, 3843, 10**12])
def test_base62_round_trip(value: int) -> None:
    assert decode_base62(encode_base62(value)) == value


def test_base62_rejects_invalid_values() -> None:
    with pytest.raises(ValueError):
        encode_base62(-1)
    with pytest.raises(ValueError):
        decode_base62("!")