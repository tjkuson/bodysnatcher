from __future__ import annotations

import pickle
import typing

from bodysnatcher import Bodysnatcher


class DummyException(Exception): ...


def test_main_pickles_list(tmpdir: typing.Any) -> None:
    try:
        with Bodysnatcher(tmpdir):
            _foo = [1, 2, 3]
            raise DummyException
    except DummyException:
        pass

    with open(tmpdir / "_foo.pkl", "rb") as fp:
        assert pickle.load(fp) == [1, 2, 3]
