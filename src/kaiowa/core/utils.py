from typing import Any, Optional


def quote(value: Any, quote_char: Optional[str] = None) -> str:
    if quote_char is None:
        if isinstance(value, str):
            quote_char = '"' if "'" in value else "'"

    return "{quote}{value}{quote}".format(value=value, quote=quote_char or "")


def make_alias(query: str, alias: Optional[str] = None, as_: bool = True) -> str:
    return "{query}{_as}{alias}".format(
        query=query, _as=" AS " if as_ else " ", alias=alias
    )
