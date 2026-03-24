import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import QtQuick.Window
import QtQuick.Controls.Material

ApplicationWindow {
    id: window
    visible: true
    width: 1280
    height: 820
    minimumWidth: 980
    minimumHeight: 640
    title: "BQ4050 上位机 - BMBus 监控"
    color: "#0f172a" // Slate 900
    
    Material.theme: Material.Dark
    Material.accent: Material.Blue

    property var latestObj: ({})
    property var sectionNamesList: []
    property var sectionFieldsDict: ({})

    Component.onCompleted: {
        var namesStr = AppModel.sectionNamesJson;
        if (namesStr) sectionNamesList = JSON.parse(namesStr);
        
        var fieldsStr = AppModel.sectionFieldsJson;
        if (fieldsStr) sectionFieldsDict = JSON.parse(fieldsStr);
    }

    onClosing: function(closeEvent) {
        AppModel.cleanupOnClose();
    }

    // Connect bridge signals
    Connections {
        target: AppModel
        function onDataChanged() {
            var rawJson = AppModel.latestDataJson;
            if (rawJson) {
                latestObj = JSON.parse(rawJson);
            }
        }
        function onLogAppended(msg) {
            logText.text += msg + "\n";
            // Auto scroll scrollview if at bottom maybe, or simple TextEdit doesn't need to
            logFlickable.contentY = Math.max(0, logFlickable.contentHeight - logFlickable.height);
        }
    }

    SplitView {
        anchors.fill: parent
        orientation: Qt.Horizontal

        // Sidebar
        Rectangle {
            SplitView.preferredWidth: 320
            SplitView.minimumWidth: 280
            SplitView.maximumWidth: 460
            color: "#1e293b" // Slate 800

            ScrollView {
                anchors.fill: parent
                anchors.margins: 16
                contentWidth: availableWidth
                clip: true

                ColumnLayout {
                    width: parent.width
                    spacing: 20

                    ColumnLayout {
                        spacing: 4
                        Label {
                            text: "BQ4050 DESKTOP HOST"
                            color: "#94a3b8" // Slate 400
                            font.pixelSize: 12
                            font.bold: true
                        }
                        Label {
                            text: "BMBus 监控系统"
                            color: "white"
                            font.pixelSize: 20
                            font.bold: true
                        }
                        Label {
                            text: "读取模拟设备或外部 SMBus 桥接端，并为 WiFi / Bluetooth 保留统一接入层。"
                            color: "#cbd5e1" // Slate 300
                            font.pixelSize: 13
                            wrapMode: Text.WordWrap
                            Layout.fillWidth: true
                        }
                    }

                    // Connection Config Group
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: connectionCol.implicitHeight + 24
                        color: "#0f172a"
                        radius: 8
                        border.color: "#334155"
                        
                        ColumnLayout {
                            id: connectionCol
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 12

                            Label {
                                text: "连接配置"
                                color: "white"
                                font.bold: true
                            }

                            ComboBox {
                                id: transportCombo
                                Layout.fillWidth: true
                                model: ["模拟设备 (mock)", "USB-TTL 串口桥 (serial)", "WiFi/TCP 桥 (tcp)", "Bluetooth 串口桥 (bluetooth)", "FT4232 直连 (ft4232)"]
                                enabled: !AppModel.isConnected && !AppModel.isBusy
                            }

                            StackLayout {
                                id: transportStack
                                Layout.fillWidth: true
                                currentIndex: transportCombo.currentIndex
                                enabled: !AppModel.isConnected && !AppModel.isBusy

                                // 0: Mock
                                ColumnLayout {
                                    Label {
                                        text: "使用内置模拟设备，无需外部硬件"
                                        color: "#94a3b8"
                                        font.pixelSize: 12
                                    }
                                }

                                // 1: Serial
                                GridLayout {
                                    columns: 2
                                    rowSpacing: 8
                                    Label { text: "串口号"; color: "#cbd5e1" }
                                    ComboBox {
                                        id: serialPortEdit
                                        editable: true
                                        model: AppModel.getSerialPorts()
                                        editText: count > 0 ? textAt(0) : "COM3"
                                        Layout.fillWidth: true
                                        onPressedChanged: {
                                            if (pressed) model = AppModel.getSerialPorts()
                                        }
                                    }
                                    Label { text: "波特率"; color: "#cbd5e1" }
                                    SpinBox { id: serialBaudSpin; value: 115200; from: 1200; to: 921600; stepSize: 9600; Layout.fillWidth: true }
                                    Label { text: "超时 (s)"; color: "#cbd5e1" }
                                    TextField { id: serialTimeoutEdit; text: "2.0"; Layout.fillWidth: true }
                                }

                                // 2: TCP
                                ColumnLayout {
                                    spacing: 8
                                    GridLayout {
                                        columns: 2
                                        rowSpacing: 8
                                        Label { text: "主机"; color: "#cbd5e1" }
                                        TextField { id: tcpHostEdit; text: "127.0.0.1"; Layout.fillWidth: true }
                                        Label { text: "端口"; color: "#cbd5e1" }
                                        SpinBox { id: tcpPortSpin; value: 8855; from: 1; to: 65535; Layout.fillWidth: true }
                                        Label { text: "超时 (s)"; color: "#cbd5e1" }
                                        TextField { id: tcpTimeoutEdit; text: "2.0"; Layout.fillWidth: true }
                                    }
                                    RowLayout {
                                        Button {
                                            text: "启动本地模拟桥"
                                            Layout.fillWidth: true
                                            enabled: !AppModel.isSimRunning && !AppModel.isBusy
                                            onClicked: AppModel.startSimulator("127.0.0.1", tcpPortSpin.value)
                                        }
                                        Button {
                                            text: "停止"
                                            enabled: AppModel.isSimRunning && !AppModel.isBusy
                                            onClicked: AppModel.stopSimulator()
                                        }
                                    }
                                    Label {
                                        text: AppModel.simStatusText
                                        color: AppModel.isSimRunning ? "#3b82f6" : "#94a3b8"
                                        font.pixelSize: 12
                                    }
                                }

                                // 3: Bluetooth
                                GridLayout {
                                    columns: 2
                                    rowSpacing: 8
                                    Label { text: "虚拟串口"; color: "#cbd5e1" }
                                    ComboBox {
                                        id: btPortEdit
                                        editable: true
                                        model: AppModel.getSerialPorts()
                                        editText: count > 0 ? textAt(0) : "COM8"
                                        Layout.fillWidth: true
                                        onPressedChanged: {
                                            if (pressed) model = AppModel.getSerialPorts()
                                        }
                                    }
                                    Label { text: "波特率"; color: "#cbd5e1" }
                                    SpinBox { id: btBaudSpin; value: 115200; from: 1200; to: 921600; stepSize: 9600; Layout.fillWidth: true }
                                    Label { text: "超时 (s)"; color: "#cbd5e1" }
                                    TextField { id: btTimeoutEdit; text: "2.0"; Layout.fillWidth: true }
                                }

                                // 4: FT4232H MPSSE
                                GridLayout {
                                    columns: 2
                                    rowSpacing: 8
                                    Label { text: "引脚接法"; color: "#cbd5e1" }
                                    Label { text: "将 SCL 接在 ADBUS0，SDA 接在 ADBUS1+2(短接)"; color: "#94a3b8"; font.pixelSize: 12 }
                                    Label { text: "设备 URL"; color: "#cbd5e1" }
                                    TextField { id: ftdiUrlEdit; text: "ftdi://ftdi:4232/1"; Layout.fillWidth: true }
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                CheckBox {
                                    id: autoPollCheck
                                    text: "自动轮询"
                                    checked: true
                                    onCheckedChanged: {
                                        if (AppModel.isConnected) {
                                            AppModel.applyPollSettings(checked, parseFloat(pollIntervalEdit.text))
                                        }
                                    }
                                }
                                Item { Layout.fillWidth: true }
                                Label { text: "间隔(s)"; color: "#cbd5e1" }
                                TextField {
                                    id: pollIntervalEdit
                                    text: "1.0"
                                    Layout.preferredWidth: 60
                                    onTextChanged: {
                                        if (AppModel.isConnected) {
                                            AppModel.applyPollSettings(autoPollCheck.checked, parseFloat(text))
                                        }
                                    }
                                }
                            }

                            RowLayout {
                                Layout.fillWidth: true
                                Button {
                                    text: "连接链路"
                                    Layout.fillWidth: true
                                    enabled: !AppModel.isConnected && !AppModel.isBusy
                                    onClicked: {
                                        var kinds = ["mock", "serial", "tcp", "bluetooth", "ft4232"];
                                        var kind = kinds[transportCombo.currentIndex];
                                        var config = {
                                            "serialPort": serialPortEdit.editText,
                                            "serialBaudrate": serialBaudSpin.value,
                                            "serialTimeout": parseFloat(serialTimeoutEdit.text) || 2.0,
                                            "tcpHost": tcpHostEdit.text,
                                            "tcpPort": tcpPortSpin.value,
                                            "tcpTimeout": parseFloat(tcpTimeoutEdit.text) || 2.0,
                                            "bluetoothPort": btPortEdit.editText,
                                            "bluetoothBaudrate": btBaudSpin.value,
                                            "bluetoothTimeout": parseFloat(btTimeoutEdit.text) || 2.0,
                                            "ftdiUrl": typeof ftdiUrlEdit !== 'undefined' ? ftdiUrlEdit.text : "ftdi://ftdi:4232/1"
                                        };
                                        AppModel.connectBridge(kind, config, autoPollCheck.checked, parseFloat(pollIntervalEdit.text) || 1.0);
                                    }
                                }
                                Button {
                                    text: "断开"
                                    enabled: AppModel.isConnected
                                    onClicked: AppModel.disconnectBridge()
                                }
                            }
                        }
                    }

                    // Quick Actions Group
                    Rectangle {
                        Layout.fillWidth: true
                        Layout.preferredHeight: actionsCol.implicitHeight + 24
                        color: "#0f172a"
                        radius: 8
                        border.color: "#334155"

                        ColumnLayout {
                            id: actionsCol
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 8

                            Label {
                                text: "快操作"
                                color: "white"
                                font.bold: true
                            }

                            Button {
                                text: "同步完整寄存器"
                                Layout.fillWidth: true
                                enabled: AppModel.isConnected && !AppModel.isBusy
                                onClicked: AppModel.requestSnapshot(true, "手动完整读取")
                            }

                            Button {
                                text: "刷新核心状态"
                                Layout.fillWidth: true
                                enabled: AppModel.isConnected && !AppModel.isBusy
                                onClicked: AppModel.requestSnapshot(false, "手动快速刷新")
                            }
                        }
                    }

                    Item { Layout.fillHeight: true }
                }
            }
        }

        // Content Area
        Rectangle {
            SplitView.fillWidth: true
            SplitView.minimumWidth: 400
            color: "#0f172a"

            ColumnLayout {
                anchors.fill: parent
                anchors.margins: 16
                spacing: 16

                // Hero
                Rectangle {
                    Layout.fillWidth: true
                    height: 90
                    color: "#1e293b"
                    radius: 8
                    border.color: "#334155"

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 16
                        spacing: 8

                        RowLayout {
                            Layout.fillWidth: true
                            Label {
                                text: "电池实时摘要"
                                font.pixelSize: 18
                                font.bold: true
                                color: "white"
                            }
                            Item { Layout.fillWidth: true }
                            Rectangle {
                                color: AppModel.statusPillState === "online" ? "#10b981" : 
                                       AppModel.statusPillState === "error" ? "#ef4444" : "#475569"
                                radius: 12
                                width: statusText.implicitWidth + 20
                                height: 24
                                Label {
                                    id: statusText
                                    anchors.centerIn: parent
                                    text: AppModel.statusPillText
                                    color: "white"
                                    font.pixelSize: 12
                                    font.bold: true
                                }
                            }
                        }
                        
                        RowLayout {
                            Layout.fillWidth: true
                            Label {
                                text: AppModel.summaryText
                                color: "#cbd5e1"
                                font.pixelSize: 13
                                Layout.fillWidth: true
                                wrapMode: Text.WordWrap
                            }
                            Label {
                                text: AppModel.updatedText
                                color: "#64748b"
                                font.pixelSize: 12
                            }
                        }
                    }
                }

                // Cards (2 rows of 3)
                GridLayout {
                    Layout.fillWidth: true
                    columns: 3
                    rowSpacing: 12
                    columnSpacing: 12

                    property var latest: window.latestObj

                    function getVoltage(lat) {
                        var v = lat ? lat["runtime.pack_voltage_mv"] : undefined;
                        return v ? (v / 1000).toFixed(3) + " V" : "--";
                    }
                    function getCurrent(lat) {
                        var c = lat ? lat["runtime.current_ma"] : undefined;
                        return c !== undefined ? (c / 1000).toFixed(2) + " A" : "--";
                    }
                    function getSoc(lat) {
                        var s = lat ? lat["runtime.relative_soc_percent"] : undefined;
                        return s !== undefined ? s + "%" : "--";
                    }
                    function getDelta(lat) {
                        var d = lat ? lat["runtime.cell_delta_mv"] : undefined;
                        return d !== undefined ? d + " mV" : "--";
                    }
                    function getTemp(lat) {
                        var t = undefined;
                        if (lat) {
                            t = lat["thermal.cell_temp_c"];
                            if (t === undefined) {
                                t = lat["thermal.internal_temp_c"];
                            }
                        }
                        return t !== undefined ? t.toFixed(1) + " C" : "--";
                    }
                    function getMode(lat) {
                        var m = undefined;
                        if (lat) {
                            m = lat["flags.security_mode"];
                            if (m === undefined) {
                                m = lat["flags.battery_status_hex"];
                            }
                        }
                        return m !== undefined ? m : "--";
                    }

                    StatCard { title: "总压"; value: parent.getVoltage(parent.latest); unit: "VOLT"; colorTheme: "#3b82f6" }
                    StatCard { title: "电流"; value: parent.getCurrent(parent.latest); unit: "CURR"; colorTheme: "#f59e0b" }
                    StatCard { title: "SOC"; value: parent.getSoc(parent.latest); unit: "CAP"; colorTheme: "#10b981" }
                    StatCard { title: "压差"; value: parent.getDelta(parent.latest); unit: "DIFF"; colorTheme: "#3b82f6" }
                    StatCard { title: "温度"; value: parent.getTemp(parent.latest); unit: "TEMP"; colorTheme: "#f59e0b" }
                    StatCard { title: "安全"; value: parent.getMode(parent.latest); unit: "SAFE"; colorTheme: "#64748b" }
                }

                // Lower split: Tabs and Log
                SplitView {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    orientation: Qt.Vertical

                    Rectangle {
                        SplitView.fillHeight: true
                        SplitView.preferredHeight: 300
                        color: "#1e293b"
                        radius: 8
                        clip: true

                        TabBar {
                            id: tabBar
                            width: parent.width
                            background: Rectangle { color: "#0f172a" }

                            Repeater {
                                model: window.sectionNamesList
                                TabButton {
                                    text: modelData
                                    width: implicitWidth + 20
                                    contentItem: Text {
                                        text: parent.text
                                        color: parent.checked ? "white" : "#94a3b8"
                                        horizontalAlignment: Text.AlignHCenter
                                        verticalAlignment: Text.AlignVCenter
                                    }
                                    background: Rectangle {
                                        color: parent.checked ? "#1e293b" : "transparent"
                                        Rectangle {
                                            width: parent.width; height: 2; color: "#3b82f6"
                                            anchors.bottom: parent.bottom
                                            visible: parent.parent.checked
                                        }
                                    }
                                }
                            }
                        }

                        StackLayout {
                            anchors.top: tabBar.bottom
                            anchors.bottom: parent.bottom
                            anchors.left: parent.left
                            anchors.right: parent.right
                            currentIndex: tabBar.currentIndex

                            Repeater {
                                model: window.sectionNamesList
                                delegate: Item {
                                    id: sectionPage
                                    property var fieldList: window.sectionFieldsDict[modelData] || []
                                    ScrollView {
                                        anchors.fill: parent
                                        anchors.margins: 12
                                        clip: true
                                        contentWidth: availableWidth

                                        ColumnLayout {
                                            width: parent.width
                                            spacing: 1

                                            Rectangle {
                                                Layout.fillWidth: true
                                                height: 32
                                                color: "#334155"
                                                RowLayout {
                                                    anchors.fill: parent
                                                    anchors.margins: 8
                                                    Label { text: "参数名称"; color: "#94a3b8"; font.bold: true; Layout.preferredWidth: 200 }
                                                    Label { text: "当前值"; color: "#94a3b8"; font.bold: true; Layout.fillWidth: true }
                                                }
                                            }

                                            Repeater {
                                                model: sectionPage.fieldList
                                                delegate: Rectangle {
                                                    property var rawVal: window.latestObj[modelData]
                                                    property string displayVal: rawVal !== undefined ? AppModel.fieldValue(modelData) : ""
                                                    
                                                    Layout.fillWidth: true
                                                    height: 32
                                                    color: index % 2 === 0 ? "transparent" : "#0f172a"
                                                    visible: displayVal !== "" // Hide empty
                                                    RowLayout {
                                                        anchors.fill: parent
                                                        anchors.margins: 8
                                                        Label { text: AppModel.fieldLabel(modelData); color: "#cbd5e1"; Layout.preferredWidth: 200 }
                                                        Label { text: displayVal; color: "white"; Layout.fillWidth: true; font.family: "Monospace" }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    Rectangle {
                        SplitView.preferredHeight: 160
                        color: "#1e293b"
                        radius: 8
                        
                        ColumnLayout {
                            anchors.fill: parent
                            anchors.margins: 12
                            spacing: 8

                            RowLayout {
                                Layout.fillWidth: true
                                Label {
                                    text: "运行日志"
                                    color: "white"
                                    font.bold: true
                                }
                                Item { Layout.fillWidth: true }
                                Button {
                                    text: "清空"
                                    onClicked: logText.text = ""
                                }
                            }

                            Rectangle {
                                Layout.fillWidth: true
                                Layout.fillHeight: true
                                color: "#0f172a"
                                border.color: "#334155"
                                radius: 4

                                ScrollView {
                                    id: scrollLog
                                    anchors.fill: parent
                                    anchors.margins: 8
                                    clip: true
                                    
                                    Flickable {
                                        id: logFlickable
                                        contentWidth: parent.width
                                        contentHeight: logText.implicitHeight
                                        boundsBehavior: Flickable.StopAtBounds

                                        TextEdit {
                                            id: logText
                                            width: parent.width
                                            readOnly: true
                                            color: "#a7f3d0" // emerald-200
                                            font.pixelSize: 12
                                            font.family: "Consolas, Courier New, monospace"
                                            wrapMode: Text.Wrap
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
