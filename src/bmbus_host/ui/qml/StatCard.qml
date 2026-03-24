import QtQuick
import QtQuick.Controls

Rectangle {
    property string title: "Title"
    property string value: "--"
    property string unit: ""
    property color colorTheme: "#3b82f6"

    width: 200
    height: 100
    color: "#1e293b"
    radius: 8
    border.color: "#334155"

    Column {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 6

        Row {
            width: parent.width
            Text {
                text: title
                color: "#94a3b8"
                font.pixelSize: 14
            }
            Item { width: parent.width - parent.children[0].width - 40 }
            Rectangle {
                width: 32
                height: 18
                radius: 4
                color: Qt.darker(colorTheme, 1.5) // A bit darker
                border.color: colorTheme
                Text {
                    anchors.centerIn: parent
                    text: unit
                    color: "white"
                    font.pixelSize: 10
                    font.bold: true
                }
            }
        }

        Text {
            text: value
            color: "white"
            font.pixelSize: 24
            font.bold: true
        }
    }
}
