from dataclasses import dataclass
from typing import Self


@dataclass
class Node:
    symbols: list[str]
    children: list[Self]
