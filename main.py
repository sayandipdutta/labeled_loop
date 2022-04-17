from dataclasses import dataclass
from typing import Any, Generator, Generic, Iterable, TypeVar


class BreakLoop(StopIteration):
    def __init__(self, *args, label, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.label = label


T = TypeVar('T')


@dataclass
class LoopVar(Generic[T]):
    data: Iterable[T]
    label: int
    terminate: bool = False

    def __iter__(self) -> Generator[T, bool, int]:
        label = self.label
        for item in self.data:
            self.terminate = yield item
            if self.terminate:
                return label
        return -1


class LabeledLoopHandler:
    def __init__(self):
        self.labels = dict()
        self.broken_from = None

    def __enter__(self) -> 'LabeledLoopHandler':
        return self

    def __exit__(self, *exc: Any) -> bool:
        _, exc_value, _ = exc
        self.labels.clear()
        if (isinstance(exc_value, BreakLoop)
                and exc_value.label == self.broken_from):
            return True
        return False

    def loop(
            self,
            iterable: Iterable,
            label: int
            ) -> Generator[Any, None, None]:
        self.labels[label] = lv = iter(LoopVar(iterable, label, False))
        for item in lv:
            yield item

    def break_from(self, label: int):
        lv = self.labels[label]
        self.broken_from = label
        try:
            lv.send(True)
        except StopIteration:
            raise BreakLoop(label=label)
        else:
            raise RuntimeError("Generator didn't stop.")


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
