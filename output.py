import dataclasses
import datetime

@dataclasses
class Output:
    id: int
    amount: int
    category: str
    date: datetime
    description: str