

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick 2.15
import QtQuick.Controls 2.15
import PiCamera2 1.0

Rectangle {
    id: rectangle
    width: 1920
    height: 1080
    color: "#00ffffff"

    property int formID: 2
    property alias buttonCancel: buttonCancel
    property alias cameraView: cameraView

    Button {
        id: buttonCancel
        x: 1524
        y: 72
        width: 275
        height: 100
        text: qsTr("Cancel")

        checked: false
        font.bold: true
        font.family: "Arial"
        font.pointSize: 25
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

    Picamera2Item {
        id: cameraView
        objectName: "cameraViewItem"
        width: 640
        height: 480
        scale: 1.5
        anchors.centerIn: parent
    }
}
