"""GUI snapshot bütünlüğü — şartname §3.1.1 madde 10.

Eksik her alan için −4 puan; CI'da bu test fail olursa snapshot'a alan eklemeden
release alınamaz.
"""

from __future__ import annotations

from domain.telemetry.snapshot import RobotSnapshot

MANDATORY_FIELDS = {
    "status",
    "mission",
    "last_qr",
    "plc",
    "pose",
    "battery_pct",
    "mode",
    "emergency",
}


def test_snapshot_contains_all_mandatory_ui_fields():
    snap = RobotSnapshot().asdict()
    missing = MANDATORY_FIELDS - set(snap.keys())
    assert not missing, f"Eksik şartname alanları: {missing}"


def test_plc_view_includes_messages():
    snap = RobotSnapshot().asdict()
    plc = snap["plc"]
    assert "connected" in plc
    assert "last_tx" in plc
    assert "last_rx" in plc
