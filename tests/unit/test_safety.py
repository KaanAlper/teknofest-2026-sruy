"""Safety agregası testleri."""

from __future__ import annotations

import pytest

from domain._shared.exceptions import SafetyViolation
from domain._shared.value_objects import Mode
from domain.safety.aggregate import SafetyState
from domain.safety.events import EmergencyStopActivated


def test_estop_blocks_autonomous():
    s = SafetyState()
    s.engage_estop("button")
    with pytest.raises(SafetyViolation):
        s.allow_autonomous_command()


def test_release_allows_autonomous_again():
    s = SafetyState()
    s.engage_estop("button")
    s.release_estop()
    s.allow_autonomous_command()  # raise etmemeli


def test_manual_command_in_auto_mode_blocked():
    s = SafetyState()
    with pytest.raises(SafetyViolation):
        s.allow_manual_command()


def test_manual_command_in_manual_mode_allowed():
    s = SafetyState()
    s.switch_mode(Mode.MANUAL)
    s.allow_manual_command()


def test_autonomous_command_in_manual_mode_blocked():
    s = SafetyState()
    s.switch_mode(Mode.MANUAL)
    with pytest.raises(SafetyViolation):
        s.allow_autonomous_command()


def test_estop_engage_publishes_event_once():
    s = SafetyState()
    s.engage_estop("button")
    s.engage_estop("button")  # idempotent
    events = s.collect_events()
    estop_events = [e for e in events if isinstance(e, EmergencyStopActivated)]
    assert len(estop_events) == 1
