from typing import Generator, Iterable, TypeVar

T = TypeVar('T')


class _loop_status:
    def __init__(self, iterable: Iterable):
        self.gen: Generator = (_ for _ in iterable)
        self.done: bool = False

    def __iter__(self):
        for i in self.gen:
            yield i
        self.done = True


class NestedLoopHandler:
    def __init__(self):
        self.nesting_levels: dict[int, _loop_status] = dict()
        self.scope: int = 0

    @property
    def parent(self):
        return self.scope - 1

    def loop(self, iterable: Iterable[T]) -> Generator[T, None, None]:
        if self.parent == -1 or not self.nesting_levels[self.parent].done:
            self.nesting_levels[self.scope] = lv = _loop_status(iterable)
            self.scope += 1
        else:
            self.nesting_levels[self.parent] = lv = _loop_status(iterable)
        for item in lv:
            yield item

    def break_from(self, level: int):
        max_level = max(self.nesting_levels)
        for i in range(max_level, level-1, -1):
            print(f"level={i}")
            self.nesting_levels[i].gen.close()
            self.nesting_levels[i].done = True
            self.scope -= 1


it = (i for i in range(6))

nested = NestedLoopHandler()

for i in nested.loop(it):
    print(f'{i=}')
    for j in nested.loop(range(3)):
        print(f'{j=}')
        for k in nested.loop(range(2)):
            print(f'{k=}')
            if j > 1:
                print(f"Broken at {(i, j, k)=}")
                nested.break_from(level=1)
        if i > 3:
            nested.break_from(level=0)

print(list(it))
