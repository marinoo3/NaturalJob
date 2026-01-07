from dataclasses import dataclass
from collections.abc import Sequence

@dataclass
class TableResult(Sequence):
    rows: list
    columns: list[str]
    rowids: list[int]

    def __len__(self):
        return len(self.rows)

    def __getitem__(self, index):
        return self.rows[index]

    def __iter__(self):
        return iter(self.rows)
    
    @property
    def dict(self) -> list[dict]:
        return [dict(zip(self.columns, row)) for row in self.rows]