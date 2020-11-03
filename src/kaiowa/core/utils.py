from typing import Any, Optional


def quote(value: Any, quote_char: Optional[str] = None) -> str:
    return "{quote}{value}{quote}".format(value=value, quote=quote_char or "")


def make_alias(
    query: str,
    alias: Optional[str] = None,
    quote_char: Optional[str] = None,
    as_: bool = True,
) -> str:
    return "{query}{_as}{alias}".format(
        query=query, _as=" AS " if as_ else " ", alias=quote(alias, quote_char)
    )
