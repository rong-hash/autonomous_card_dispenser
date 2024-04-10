import QtQuick 2.15
import QtQuick.Controls 2.15

MainScreenForm {

    Component.onCompleted: {
        stackView.newStackFormLoaded(this);
        console.debug("main_loaded");
    }

    buttonRequest.onClicked: {
        stackView.replace("Auth.qml", StackView.PushTransition);
    }
}
