from __future__ import annotations

import logging
import pickle
from pathlib import Path
from typing import TYPE_CHECKING
from typing import BinaryIO
from typing import overload

from typing_extensions import Self

if TYPE_CHECKING:
    from types import TracebackType


class Bodysnatcher:
    """Context manager that pickles objects in the local scope on exception.

    Attempts to pickle all objects in the local scope of the context manager on
    exception. The pickled objects are named after the variable they were assigned. For
    example, variable `foo` will be pickled to `foo.pkl`.

    Attributes:
        path: The directory to store the pickled objects. Defaults to the current
            working directory.
        logger: The logger to use for messages. If none is provided, a logger with
            the name of the module is used.

    """

    def __init__(
        self,
        path: str | Path = "",
        logger: logging.Logger | None = None,
    ) -> None:
        self.path = path if isinstance(path, Path) else Path(path)
        self.logger = logging.getLogger(__name__) if logger is None else logger

    def _try_dump(self, obj: object, fp: BinaryIO) -> None:
        try:
            pickle.dump(obj, fp)
        except (pickle.PicklingError, TypeError):
            self.logger.exception("Failed to pickle %s via %s, skipping", obj, fp)
        else:
            self.logger.info("Pickled %s via %s", obj, fp)

    def __enter__(self) -> Self:
        return self

    @overload
    def __exit__(self, exc_type: None, exc_val: None, exc_tb: None) -> None: ...

    @overload
    def __exit__(
        self,
        exc_type: type[BaseException],
        exc_val: BaseException,
        exc_tb: TracebackType,
    ) -> None: ...

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is None:
            return
        # The implementation is checked against the signature of the implementation,
        # not against its inferred overload. Thus, assert remaining parameters against
        # None so that type-checkers infer correctly.
        assert exc_val is not None
        assert exc_tb is not None

        self.logger.info(
            "Exception occured in %s context",
            type(self).__name__,
            exc_info=(exc_type, exc_val, exc_tb),
        )
        symbols = {
            symbol: obj
            for symbol, obj in exc_tb.tb_frame.f_locals.items()
            if obj is not self
        }
        if not self.path.exists():
            self.logger.info("Creating directory at %s", self.path)
            self.path.mkdir()
        for symbol, obj in symbols.items():
            path = self.path / f"{symbol}.pkl"
            with open(path, "wb") as fp:
                self._try_dump(obj, fp)
