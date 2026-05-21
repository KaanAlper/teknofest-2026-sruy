import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

ApplicationWindow {
    id: root
    visible: true
    width: 1366
    height: 768
    title: "CargoBot — Operatör Panel"
    color: "#0d1117"

    property var snapshot: AppContext.snapshot

    Connections {
        target: AppContext
        function onSnapshotChanged() {
            root.snapshot = AppContext.snapshot
        }
    }

    header: ToolBar {
        background: Rectangle { color: "#161b22" }
        RowLayout {
            anchors.fill: parent
            spacing: 16
            Rectangle {
                width: 12; height: 12; radius: 6
                // PLC'ye değil, görsel olarak "yaşıyor" göstergesi
                color: root.snapshot.plc && root.snapshot.plc.connected ? "#3fb950" : "#f85149"
            }
            Label {
                text: root.snapshot.status || "—"
                color: "white"
                font.bold: true
                font.pixelSize: 16
            }
            Item { Layout.fillWidth: true }
            Label {
                text: "PLC " + (root.snapshot.plc && root.snapshot.plc.connected ? "● bağlı" : "○ kopuk")
                color: root.snapshot.plc && root.snapshot.plc.connected ? "#3fb950" : "#f85149"
            }
            Label {
                text: "Mod: " + (root.snapshot.mode || "—")
                color: "white"
            }
            Label {
                text: Qt.formatDateTime(new Date(), "HH:mm:ss")
                color: "#8b949e"
            }
        }
    }

    StackView {
        id: stack
        anchors.fill: parent
        initialItem: dashboardComponent
    }

    Component {
        id: dashboardComponent
        Loader { source: "pages/DashboardPage.qml" }
    }
}
