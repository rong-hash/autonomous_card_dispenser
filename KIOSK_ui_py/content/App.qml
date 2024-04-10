// Copyright (C) 2021 The Qt Company Ltd.
// SPDX-License-Identifier: LicenseRef-Qt-Commercial OR GPL-3.0-only
import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Window 2.15

Window {
    id:rootWindow
    width: 1920
    height: 1080

    visible: true
    title: "KIOSK_ui"

    property int formID: 0

    signal newFormLoaded(form:Item);

    Image {
        id: image
        anchors.fill: parent
        source: "images/back.png"
        fillMode: Image.PreserveAspectCrop
    }

    ComboBox {
        id: comboBox
        x: 1704
        y: 936
        width: 200
        height: 60
        font.pointSize: 18
        font.bold: true
        hoverEnabled: false
        model:["English","中文（简体）"]

        // delegate: Item {
        //     width: comboBox.width
        //     height: 40

        //     Rectangle {
        //         width: parent.width
        //         height: 1
        //         color: "#e0e0e0"
        //         anchors.bottom: parent.bottom
        //     }

        //     Text {
        //         text: modelData
        //         anchors.verticalCenter: parent.verticalCenter
        //         leftPadding: 10
        //         font.pixelSize: 16
        //     }
        // }
    }



    StackView {
        id: stackView
        anchors.fill: parent
        //initialItem: authScreen
        function newStackFormLoaded(form){
            rootWindow.newFormLoaded(form);

        }
    }


    Component.onCompleted: {
        var initialItem = stackView.push("MainScreen.qml");
    }

    // Screen01 {
    //     id: mainScreen
    // }

}



