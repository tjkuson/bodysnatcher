# bodysnatcher

Save objects when an exception occurs using pickle.

## What it does

Bodysnatcher dumps frame `locals()` if a context is exitted via an exception.

```python
with Bodysnatcher():
    ...
    raise Exception  # Will dump context locals()
```

However, it will not dump itself as that's probably not relevant.

> [!WARNING]
> The `locals()` table can be quite large depending in which scope you create
> the context.


By default, it dumps to the current working directory. That can be configured
using the `path` argument.

```python
with Bodysnatcher("/tmp/"): ...  # Dump objects to /tmp/ (e.g., /tmp/foo.pkl)
```

## Example usage

Run

```python
from collections.abc import Generator

from bodysnatcher import Bodysnatcher


def may_err() -> Generator[str, None, None]:
    yield "Hello"
    yield "World"
    raise RuntimeError


def main() -> int:
    data = []
    with Bodysnatcher():
        for elt in may_err():
            data.append(elt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

and then unpickle to recover the data. For example,

```
$ python -c "import pickle; print(pickle.load(open('data.pkl', 'rb')))"
['Hello', 'World']
```
