import dataclasses
import datetime

@dataclasses.dataclass(frozen=True)
class Output:
    id: int | None
    amount: float
    category: str
    date: datetime.date
    description: str