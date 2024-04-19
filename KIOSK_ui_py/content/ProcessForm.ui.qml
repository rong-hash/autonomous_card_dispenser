

/*
This is a UI file (.ui.qml) that is intended to be edited in Qt Design Studio only.
It is supposed to be strictly declarative and only uses a subset of QML. If you edit
this file manually, you might introduce QML code that is not supported by Qt Design Studio.
Check out https://doc.qt.io/qtcreator/creator-quick-ui-forms.html for details on .ui.qml files.
*/
import QtQuick 2.15
import QtQuick.Controls 2.15

Item {
    id: processform
    width: 1920
    height: 1080

    property int formID: 3
    property alias busyIndicator: busyIndicator
    property alias cross: cross
    property alias text1: text1

    BusyIndicator {
        id: busyIndicator
        width: 300
        height: 300
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
    }

    Image {
        id: cross
        source: "images/cross.png"
        fillMode: Image.PreserveAspectFit
        width: 300
        height: 300
        anchors.verticalCenter: parent.verticalCenter
        anchors.horizontalCenter: parent.horizontalCenter
        visible: false
    }

    Text {
        id: text1
        y: 755
        width: 190
        height: 15
        text: qsTr("Processing")
        anchors.bottom: parent.bottom
        font.pixelSize: 48
        horizontalAlignment: Text.AlignHCenter
        font.bold: true
        anchors.bottomMargin: 310
        anchors.horizontalCenter: parent.horizontalCenter
    }
}
