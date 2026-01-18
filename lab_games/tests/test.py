from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class Test:
    id: int
    value: int | None

a = Test(1)
print(a)