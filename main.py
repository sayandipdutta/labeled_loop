from dataclasses import dataclass
from typing import Iterable


@dataclass
class LoopVar:
    data: Iterable
    level: int
    terminate: bool = False

    def __iter__(self):
        level = self.level
        for item in self.data:
            self.terminate = yield item
            if self.terminate:
                return level
                


class LabeledLoopHandler:
    def __init__(self):
        self.levels = dict()
        self.broken_from = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        if isinstance(exc_value, StopIteration) and exc_value.value == self.broken_from:
            return True

    def iter(self, iterable: Iterable, level: int):
        self.levels[level] = lv = iter(LoopVar(iterable, level, False))
        for item in lv:
            yield item

    def break_from(self, level):
        lv = self.levels[level]
        self.broken_from = level
        lv.send(True)

it = (i for i in range(5))

with LabeledLoopHandler() as lh:
    for i in lh.iter(it, level=0):
        print(f'{i=}')
        for j in lh.iter(range(3), level=1):
            print(f'{j=}')
            for k in lh.iter(range(2), level=2):
                print(f'{k=}')
                if i > 1:
                    lh.break_from(0)

print(i, j, k)
print(list(it))
