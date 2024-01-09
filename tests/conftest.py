from pytest import fixture

@fixture
def monkeypatch():
    from _pytest.monkeypatch import MonkeyPatch
    mp = MonkeyPatch()
    yield mp
    mp.undo()
