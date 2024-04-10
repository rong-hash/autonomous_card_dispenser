import QtQuick 2.15
import QtQuick.Controls 2.15
AuthForm {
    Component.onCompleted: {
        stackView.newStackFormLoaded(this);
        console.debug("auth_loaded");
    }

    buttonCancel.onClicked: {
        stackView.replace("MainScreen.qml", StackView.PopTransition);
        console.debug(stackView.depth);
    }
}
