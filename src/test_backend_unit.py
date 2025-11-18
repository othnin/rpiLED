import time
import threading
import pytest

from backend import PatternManager, PatternBase, SystemEventHook


class MockNeo:
    def __init__(self):
        self.num_leds = 10
    def clear_strip(self):
        pass
    def update_strip(self):
        pass


class DummyPattern(PatternBase):
    def __init__(self):
        self.started = False
        self.cleaned = False

    @property
    def name(self) -> str:
        return "Dummy Pattern"

    @property
    def description(self) -> str:
        return "A dummy pattern for tests"

    def run(self, neo, stop_event: threading.Event):
        # mark started and block until the stop_event is set
        self.started = True
        stop_event.wait()

    def cleanup(self, neo):
        self.cleaned = True


class FakeHook(SystemEventHook):
    def __init__(self, event_name: str, check_result: bool = False):
        self._event_name = event_name
        self._check_result = check_result
        self.triggered_with = None

    @property
    def event_name(self) -> str:
        return self._event_name

    def check(self) -> bool:
        return self._check_result

    def on_trigger(self, pattern_manager):
        # record that on_trigger was called
        self.triggered_with = pattern_manager


@pytest.fixture
def manager():
    neo = MockNeo()
    mgr = PatternManager(neo)
    yield mgr
    # ensure we stop any running pattern to avoid leaking threads
    mgr.stop_all_patterns()


def test_register_and_startup_pattern(manager):
    dummy = DummyPattern()
    manager.patterns[dummy.name] = dummy

    manager.register_startup_pattern(dummy.name)
    manager.start_startup_patterns()

    # give thread a moment to start
    time.sleep(0.1)

    assert manager.current_pattern is not None
    assert isinstance(manager.current_pattern, DummyPattern)
    assert dummy.started is True

    # stop and verify cleanup
    manager.stop_all_patterns()
    time.sleep(0.1)
    assert manager.current_pattern is None
    assert dummy.cleaned is True


def test_hook_linked_to_pattern_triggers_start(manager):
    dummy = DummyPattern()
    manager.patterns[dummy.name] = dummy

    # link hook event name to the pattern
    manager.register_startup_pattern(dummy.name, linked_hook="fake_event")

    hook = FakeHook("fake_event", check_result=True)

    # calling handle_hook_trigger should start the linked pattern
    manager.handle_hook_trigger(hook)

    time.sleep(0.1)
    assert manager.current_pattern is not None
    assert dummy.started is True

    manager.stop_all_patterns()


def test_callbacks_emitted_on_start_stop(manager):
    dummy = DummyPattern()
    manager.patterns[dummy.name] = dummy

    events = {"started": [], "stopped": []}

    def on_start(name):
        events["started"].append(name)

    def on_stop(name):
        events["stopped"].append(name)

    manager.register_callback("pattern_started", on_start)
    manager.register_callback("pattern_stopped", on_stop)

    manager.start_pattern(dummy.name)
    time.sleep(0.1)

    assert events["started"] == [dummy.name]

    manager.stop_pattern()
    time.sleep(0.1)

    assert events["stopped"] == [dummy.name]
