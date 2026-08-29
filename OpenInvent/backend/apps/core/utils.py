from __future__ import annotations

from datetime import datetime, timezone

from bson import ObjectId
from bson.errors import InvalidId


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def to_object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)
    except (InvalidId, TypeError) as exc:
        raise ValueError(f"'{value}' não é um ObjectId válido.") from exc


def serialize_doc(doc: dict) -> dict:
    """Converte um documento do MongoDB em algo JSON-serializável.

    - `_id` (ObjectId) -> `id` (str)
    - Qualquer outro ObjectId aninhado também é convertido para str.
    """
    if doc is None:
        return doc

    result = dict(doc)
    if "_id" in result:
        result["id"] = str(result.pop("_id"))

    for key, value in list(result.items()):
        if isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, dict):
            result[key] = serialize_doc(value)

    return result
