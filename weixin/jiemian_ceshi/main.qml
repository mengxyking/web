import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import QtQuick.Window 2.15

// 主窗口
Window {
    width: 1200
    height: 800
    title: "设备服务管理系统"
    visible: true

    // 初始化时，主动请求 Python 的服务列表数据
    Component.onCompleted: {
        console.log("QML界面初始化完成，请求服务列表数据")
        backend.requestServiceData()
    }

    // 左右分栏布局（SplitView 支持拖拽调整宽度）
    SplitView {
        anchors.fill: parent
        orientation: Qt.Horizontal

        // 左侧：服务 IP 列表栏（固定最小宽度）
        Rectangle {
            width: 300
            color: "#f5f5f5"
            SplitView.minimumWidth: 200

            // 标题
            Text {
                text: "服务 IP 列表"
                font.pixelSize: 20
                font.bold: true
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.margins: 10
            }

            // 服务列表 ListView
            ListView {
                id: serviceListView
                anchors.top: parent.children[0].bottom
                anchors.fill: parent
                anchors.margins: 10
                spacing: 5

                // 模型：存储 Python 传递的服务列表数据
                model: ListModel { id: serviceModel }

                // 自定义委托：核心修复→直接访问role，放弃modelData
                delegate: Rectangle {
                    id: serviceItem
                    width: serviceListView.width  // 显式绑定ListView宽度，避免父宽度异常
                    height: 60
                    color: mouseArea.hovered ? "#e0e0e0" : "white"
                    border.color: "#cccccc"
                    border.width: 1
                    radius: 5

                    // 点击请求设备数据：直接访问ip role
                    MouseArea {
                        id: mouseArea
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            if (ip) {  // 直接判断ip role是否存在
                                backend.requestDeviceData(ip)
                            }
                        }
                    }

                    // IP 文本：直接访问ip role，添加兜底
                    Text {
                        text: ip || "未知IP"  // 直接用ip，而非modelData.ip
                        font.pixelSize: 18
                        font.bold: true
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.margins: 10
                    }

                    // 设备标识文本：直接访问id role，添加兜底
                    Text {
                        text: id || "未知标识"  // 直接用id，而非modelData.id
                        font.pixelSize: 12
                        color: "#666666"
                        anchors.left: parent.left
                        anchors.bottom: parent.bottom
                        anchors.margins: 10
                    }
                }

                // 空列表提示
                Text {
                    id: serviceEmptyTip
                    text: "暂无服务IP数据"
                    font.pixelSize: 16
                    color: "#999999"
                    anchors.centerIn: parent
                    visible: serviceModel.count === 0
                }
            }
        }

        // 右侧：设备详情列表栏
        Rectangle {
            color: "#ffffff"
            SplitView.fillWidth: true

            // 标题
            Text {
                text: "设备详情列表"
                font.pixelSize: 20
                font.bold: true
                anchors.top: parent.top
                anchors.left: parent.left
                anchors.margins: 10
            }

            // 设备列表 ListView
            ListView {
                id: deviceListView
                anchors.top: parent.children[0].bottom
                anchors.fill: parent
                anchors.margins: 10
                spacing: 8

                // 模型：存储设备数据
                model: ListModel { id: deviceModel }

                // 自定义委托：移除阴影，用渐变替代+空值判断
                delegate: Rectangle {
                    width: deviceListView.width  // 显式绑定宽度
                    height: 120
                    color: "white"
                    border.color: "#cccccc"
                    border.width: 1
                    radius: 5
                    // 用轻微的背景色渐变模拟立体效果
                    gradient: Gradient {
                        GradientStop { position: 0.0; color: "#fafafa" }
                        GradientStop { position: 1.0; color: "#f0f0f0" }
                    }

                    // 网格布局：展示设备多字段，所有属性添加空值兜底
                    GridLayout {
                        anchors.fill: parent
                        anchors.margins: 10
                        columns: 2
                        rowSpacing: 5
                        columnSpacing: 20

                        // 字段1：ADB 端口
                        Text { text: "ADB 端口："; font.bold: true }
                        Text { text: adb || "" }  // 直接访问role

                        // 字段2：API 端口
                        Text { text: "API 端口："; font.bold: true }
                        Text { text: api_port || "" }  // 直接访问role

                        // 字段3：设备名称（自动省略）
                        Text { text: "设备名称："; font.bold: true }
                        Text {
                            text: name || "无名称";  // 直接访问role
                            elide: Text.ElideRight;
                            width: parent.width - 120
                        }

                        // 字段4：设备状态
                        Text { text: "设备状态："; font.bold: true }
                        Text {
                            text: state || "无状态";  // 直接访问role
                            color: (state === "exited") ? "red" : "green"
                        }

                        // 字段5：分辨率
                        Text { text: "分辨率："; font.bold: true }
                        Text {
                            text: (width && height) ? (width + "x" + height) : ""  // 直接访问role
                        }

                        // 字段6：详细状态（自动省略）
                        Text { text: "详细状态："; font.bold: true }
                        Text {
                            text: status || "";  // 直接访问role
                            elide: Text.ElideRight;
                            width: parent.width - 120
                        }
                    }
                }

                // 空列表提示
                Text {
                    id: deviceEmptyTip
                    text: "请选择左侧的服务IP查看设备数据"
                    font.pixelSize: 16
                    color: "#999999"
                    anchors.centerIn: parent
                    visible: deviceModel.count === 0
                }
            }
        }
    }

    // 接收服务列表数据：核心修复→改用Object.keys遍历对象
    Connections {
        target: backend
        function onSendServiceData(jsonStr) {
            console.log("QML接收的原始数据：", jsonStr)
            let data = JSON.parse(jsonStr)
            console.log("QML解析后的数据：", data)
            if (data.code === 200 && data.data) {
                serviceModel.clear()
                // 核心修复：用Object.keys遍历对象的属性（避免原型链干扰）
                let ipList = Object.keys(data.data)
                console.log("遍历到的IP列表：", ipList)
                ipList.forEach(ip => {
                    let deviceId = data.data[ip]
                    console.log(`添加IP：${ip}，ID：${deviceId}`)
                    serviceModel.append({
                        ip: ip,
                        id: deviceId
                    })
                })
                console.log("服务列表模型最终数量：", serviceModel.count)
            } else {
                serviceModel.clear()
                console.log("服务列表数据异常")
            }
        }
    }

    // 接收设备数据
    Connections {
        target: backend
        function onSendDeviceData(jsonStr) {
            let data = JSON.parse(jsonStr)
            if (data.code === 200) {
                deviceModel.clear()
                // 遍历设备数组，添加到模型
                for (let device of data.data) {
                    deviceModel.append(device)
                }
            } else {
                deviceModel.clear()
                // 空数据时添加兜底项，避免modelData为undefined
                deviceModel.append({
                    adb: "", api_port: "", name: "无设备数据",
                    state: "error", width: "", height: "", status: ""
                })
            }
        }
    }
}