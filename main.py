from typing import Generator, Iterable, TypeVar

T = TypeVar('T')


class NestedLoopHandler:
    def __init__(self):
        self.nesting_levels: dict[int, Generator] = dict()

    def loop(
            self,
            iterable: Iterable[T],
            level: int
            ) -> Generator[T, None, None]:
        self.nesting_levels[level] = lv = (_ for _ in iterable)
        for item in lv:
            yield item

    def break_from(self, level: int):
        max_level = max(self.nesting_levels)
        for i in range(max_level, level-1, -1):
            print(f"level={i}")
            self.nesting_levels[i].close()


it = (i for i in range(5))

nested = NestedLoopHandler()

for i in nested.loop(it, level=0):
    print(f'{i=}')
    for j in nested.loop(range(3), level=1):
        print(f'{j=}')
        for k in nested.loop(range(2), level=2):
            print(f'{k=}')
            if j > 1:
                print(f"Broken at {(i, j, k)=}")
                nested.break_from(level=1)
        if i > 3:
            nested.break_from(level=0)

print(list(it))
