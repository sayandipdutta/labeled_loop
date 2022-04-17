from dataclasses import dataclass
from typing import Iterable


class BreakLoop(StopIteration):
    def __init__(self, *args, label, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.label = label


@dataclass
class LoopVar:
    data: Iterable
    label: int
    terminate: bool = False

    def __iter__(self):
        label = self.label
        for item in self.data:
            self.terminate = yield item
            if self.terminate:
                return label


class LabeledLoopHandler:
    def __init__(self):
        self.labels = dict()
        self.broken_from = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.labels.clear()
        if (isinstance(exc_value, BreakLoop)
                and exc_value.label == self.broken_from):
            return True

    def loop(self, iterable: Iterable, label: int):
        self.labels[label] = lv = iter(LoopVar(iterable, label, False))
        for item in lv:
            yield item

    def break_from(self, label):
        lv = self.labels[label]
        self.broken_from = label
        try:
            lv.send(True)
        except StopIteration:
            raise BreakLoop(label=label)


it = (i for i in range(5))

with LabeledLoopHandler() as labeled:
    for i in labeled.loop(it, label=0):
        print(f'{i=}')
        for j in labeled.loop(range(3), label=1):
            print(f'{j=}')
            for k in labeled.loop(range(2), label=2):
                print(f'{k=}')
                if i > 1:
                    labeled.break_from(label=0)

print(list(it))
