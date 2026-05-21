"""Mission agregası birim testleri."""

from __future__ import annotations

import pytest

from cargobot.domain._shared.exceptions import InvalidPhaseTransition
from cargobot.domain.mission.aggregate import Mission
from cargobot.domain.mission.events import LoadPicked, MissionPhaseChanged, MissionStarted
from cargobot.domain.mission.states import MissionPhase


def test_new_mission_publishes_started_event():
    m = Mission.new("P1", "D1")
    events = m.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], MissionStarted)
    assert events[0].pickup_node == "P1"


def test_valid_phase_transition_publishes_event():
    m = Mission.new("P1", "D1")
    m.collect_events()
    m.transition(MissionPhase.PLANNING)
    events = m.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], MissionPhaseChanged)
    assert events[0].to_phase == MissionPhase.PLANNING


def test_invalid_phase_transition_raises():
    m = Mission.new("P1", "D1")
    with pytest.raises(InvalidPhaseTransition):
        m.transition(MissionPhase.PICKING)


def test_full_happy_path_to_completed():
    m = Mission.new("P1", "D1")
    flow = [
        MissionPhase.PLANNING,
        MissionPhase.MOVING_TO_PICKUP,
        MissionPhase.APPROACHING_LOAD,
        MissionPhase.PICKING,
        MissionPhase.MOVING_TO_DOOR,
        MissionPhase.AT_DOOR,
        MissionPhase.MOVING_TO_DROPOFF,
        MissionPhase.APPROACHING_DROP,
        MissionPhase.DROPPING,
        MissionPhase.RETURNING_TO_DOOR,
        MissionPhase.RETURNING_HOME,
        MissionPhase.COMPLETED,
    ]
    for phase in flow:
        m.transition(phase)
    assert m.phase == MissionPhase.COMPLETED


def test_mark_picked_publishes_load_picked():
    m = Mission.new("P1", "D1")
    m.collect_events()
    m.mark_picked("QR-P1")
    events = m.collect_events()
    assert any(isinstance(e, LoadPicked) for e in events)
