import QtQuick 2.15

ProcessForm {
    Component.onCompleted: {
        stackView.newStackFormLoaded(this);
        console.debug("process_loaded");
    }
}
