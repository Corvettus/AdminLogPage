
from dataclasses import dataclass


@dataclass
class ParsedMessage:
    from_user: str
    subject: str
    message: str
