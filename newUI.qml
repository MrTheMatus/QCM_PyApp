import QtQuick 2.15
import QtQuick.Controls 2.15
import QtCharts 2.15

ApplicationWindow {
    visible: true
    width: 1280
    height: 800
    title: "Sensor Data App"

    // Main Navigation
    Drawer {
        id: navigationDrawer
        width: 250
        height: parent.height
        Rectangle {
            width: parent.width
            height: parent.height
            color: "#f3f3f3"
            Column {
                spacing: 20
                anchors.centerIn: parent
                Button { text: "Dashboard"; onClicked: stackView.push(dashboardView) }
                Button { text: "Sensors"; onClicked: stackView.push(sensorConfigView) }
                Button { text: "Logs"; onClicked: stackView.push(logView) }
                Button { text: "Plots"; onClicked: stackView.push(plotView) }
                Button { text: "Settings"; onClicked: stackView.push(settingsView) }
            }
        }
    }

    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: dashboardView

        Component {
            id: dashboardView

            Rectangle {
                color: "white"
                anchors.fill: parent

                Column {
                    spacing: 20
                    anchors.centerIn: parent

                    Text { text: "Dashboard"; font.pixelSize: 30 }

                    // Real-time sensor data
                    Rectangle {
                        width: 400; height: 200
                        color: "#efefef"
                        Text { text: "Sensor Data: Live Values"; anchors.centerIn: parent }
                    }

                    // Acquisition Status
                    Row {
                        spacing: 10
                        Text { text: "Acquisition Status: " }
                        Rectangle {
                            width: 20; height: 20
                            color: "green" // Change dynamically
                        }
                    }

                    // Elapsed Time
                    Row {
                        spacing: 10
                        Text { text: "Time Elapsed: " }
                        Text { text: "00:00:10" } // Bind dynamically
                    }
                }
            }
        }

        Component {
            id: sensorConfigView

            Rectangle {
                color: "white"
                anchors.fill: parent

                Column {
                    spacing: 20
                    anchors.centerIn: parent

                    Text { text: "Sensor Configuration"; font.pixelSize: 30 }

                    ListView {
                        width: parent.width; height: 400
                        model: ListModel {
                            ListElement { name: "Sensor 1" }
                            ListElement { name: "Sensor 2" }
                            ListElement { name: "Sensor 3" }
                        }
                        delegate: Rectangle {
                            width: parent.width
                            height: 50
                            color: "#efefef"
                            Text { text: name; anchors.centerIn: parent }
                        }
                    }

                    Button { text: "Upload YAML" }
                }
            }
        }

        Component {
            id: logView

            Rectangle {
                color: "white"
                anchors.fill: parent

                Column {
                    spacing: 20
                    anchors.centerIn: parent

                    Text { text: "Logs"; font.pixelSize: 30 }

                    TextField { placeholderText: "Search Logs"; width: parent.width * 0.8 }

                    ListView {
                        width: parent.width; height: 400
                        model: ListModel {
                            ListElement { log: "[12:01] Sensor 1 connected" }
                            ListElement { log: "[12:02] Data acquisition started" }
                        }
                        delegate: Rectangle {
                            width: parent.width
                            height: 50
                            color: "#efefef"
                            Text { text: log; anchors.centerIn: parent }
                        }
                    }
                }
            }
        }

        Component {
            id: plotView

            Rectangle {
                color: "white"
                anchors.fill: parent

                Column {
                    spacing: 20
                    anchors.centerIn: parent

                    Text { text: "Data Visualization"; font.pixelSize: 30 }

                    ChartView {
                        width: 800
                        height: 400
                        LineSeries {
                            name: "Sensor Data"
                            points: [Qt.point(0, 10), Qt.point(1, 15), Qt.point(2, 20)]
                        }
                    }

                    Button { text: "Export as PDF" }
                }
            }
        }

        Component {
            id: settingsView

            Rectangle {
                color: "white"
                anchors.fill: parent

                Column {
                    spacing: 20
                    anchors.centerIn: parent

                    Text { text: "Settings"; font.pixelSize: 30 }

                    Row {
                        spacing: 10
                        Text { text: "Units: " }
                        ComboBox { model: ["Metric", "Imperial"] }
                    }

                    Row {
                        spacing: 10
                        Text { text: "Channel: " }
                        ComboBox { model: ["USB", "Wi-Fi", "Bluetooth"] }
                    }

                    Button { text: "Save Settings" }
                }
            }
        }
    }
}
