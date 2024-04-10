

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: rectangleMain
    width: 1920
    height: 1080
    color: "#00ffffff"

    property int formID: 1
    property alias buttonRequest: buttonRequest

    Column {
        id: col
        spacing: 100
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        Button {
            id: buttonRequest
            width: 350
            height: 178
            text: qsTr("Request")
            //anchors.rightMargin: 100
            checked: false
            font.bold: true
            font.family: "Arial"
            font.pointSize: 40
            checkable: false

            // background: Rectangle {
            //     radius: 5
            //     //color: "skyblue" // Change this to your desired color
            // }

            // Connections {
            //     target: button
            //     onClicked: animation.start()
            // }
        }

        Button {
            id: buttonReturn
            width: 350
            height: 178
            text: qsTr("Return")
            //nchors.leftMargin: 100
            checked: false
            font.bold: true
            font.family: "Arial"
            font.pointSize: 40
            checkable: false
            // background: Rectangle {
            //     radius: 5
            //     //color: "skyblue" // Change this to your desired color
            // }

            // Connections {
            //     target: button
            //     onClicked: animation.start()
            // }
        }
    }

    // Text {
    //     id: label
    //     text: qsTr("Hello KIOSK_ui")
    //     anchors.top: button.bottom
    //     font.family: Constants.font.family
    //     anchors.topMargin: 45
    //     anchors.horizontalCenter: parent.horizontalCenter

    //     SequentialAnimation {
    //         id: animation

    //         ColorAnimation {
    //             id: colorAnimation1
    //             target: rectangle
    //             property: "color"
    //             to: "#2294c6"
    //             from: Constants.backgroundColor
    //         }

    //         ColorAnimation {
    //             id: colorAnimation2
    //             target: rectangle
    //             property: "color"
    //             to: Constants.backgroundColor
    //             from: "#2294c6"
    //         }
    //     }
    // }

    // states: [
    //     State {
    //         name: "clicked"
    //         when: button.checked

    //         PropertyChanges {
    //             target: label
    //             text: qsTr("Button Checked")
    //         }
    //     }
    // ]
}
