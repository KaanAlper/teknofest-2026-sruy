import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Item {
    id: dashboard
    anchors.fill: parent

    GridLayout {
        anchors.fill: parent
        anchors.margins: 16
        columns: 3
        columnSpacing: 16
        rowSpacing: 16

        // Sol-üst — Görev Paneli
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.columnSpan: 2
            color: "#161b22"
            radius: 8
            border.color: "#30363d"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8
                Label {
                    text: "Görev"
                    color: "#8b949e"
                    font.pixelSize: 12
                }
                Label {
                    text: AppContext.snapshot.mission
                        ? AppContext.snapshot.mission.pickup_node + " → " + AppContext.snapshot.mission.dropoff_node
                        : "—"
                    color: "white"
                    font.pixelSize: 24
                    font.bold: true
                }
                Label {
                    text: AppContext.snapshot.mission
                        ? "Faz: " + AppContext.snapshot.mission.phase
                        : ""
                    color: "#58a6ff"
                }
            }
        }

        // Sağ-üst — Batarya & Mod
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#161b22"
            radius: 8
            border.color: "#30363d"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8
                Label { text: "Batarya"; color: "#8b949e"; font.pixelSize: 12 }
                Label {
                    text: (AppContext.snapshot.battery_pct || 0).toFixed(0) + "%"
                    color: "white"
                    font.pixelSize: 32
                    font.bold: true
                }
                ProgressBar {
                    Layout.fillWidth: true
                    from: 0; to: 100
                    value: AppContext.snapshot.battery_pct || 0
                }
                Label {
                    text: "Acil Stop: " + (AppContext.snapshot.emergency ? "AKTİF" : "—")
                    color: AppContext.snapshot.emergency ? "#f85149" : "#3fb950"
                    font.bold: true
                }
            }
        }

        // Alt-sol — Pose & QR
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.columnSpan: 2
            color: "#161b22"
            radius: 8
            border.color: "#30363d"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8
                Label { text: "Robot Pozisyonu"; color: "#8b949e"; font.pixelSize: 12 }
                Label {
                    text: AppContext.snapshot.pose
                        ? "x=" + AppContext.snapshot.pose.x.toFixed(2)
                          + "  y=" + AppContext.snapshot.pose.y.toFixed(2)
                          + "  θ=" + (AppContext.snapshot.pose.theta * 57.3).toFixed(1) + "°"
                        : "—"
                    color: "white"
                    font.family: "monospace"
                    font.pixelSize: 16
                }
                Label { text: "Son QR"; color: "#8b949e"; font.pixelSize: 12 }
                Label {
                    text: AppContext.snapshot.last_qr
                        ? AppContext.snapshot.last_qr.qr_id
                        : "—"
                    color: "white"
                    font.pixelSize: 16
                }
            }
        }

        // Alt-sağ — PLC
        Rectangle {
            Layout.fillWidth: true
            Layout.fillHeight: true
            color: "#161b22"
            radius: 8
            border.color: "#30363d"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 12
                spacing: 8
                Label { text: "PLC"; color: "#8b949e"; font.pixelSize: 12 }
                Label {
                    text: AppContext.snapshot.plc
                        ? "Son TX: " + (AppContext.snapshot.plc.last_tx || "—")
                        : ""
                    color: "white"
                    font.pixelSize: 12
                    wrapMode: Text.Wrap
                }
                Label {
                    text: AppContext.snapshot.plc
                        ? "Son RX: " + (AppContext.snapshot.plc.last_rx || "—")
                        : ""
                    color: "white"
                    font.pixelSize: 12
                    wrapMode: Text.Wrap
                }
            }
        }
    }
}
