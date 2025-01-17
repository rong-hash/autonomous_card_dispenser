import QtQuick 2.15
import QtQuick.Controls 2.15

MainScreenForm {

    Component.onCompleted: {
        stackView.newStackFormLoaded(this);
        console.debug("main_loaded");
    }

    buttonRequest.onClicked: {
        stackView.cleanForm()
        stackView.replace("Auth.qml", StackView.PushTransition);
    }

    buttonReturn.onClicked: {
        stackView.cleanForm()
        stackView.replace("Process.qml", StackView.PushTransition);
    }
}
