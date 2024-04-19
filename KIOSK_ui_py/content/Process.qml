import QtQuick 2.15

ProcessForm {
    Component.onCompleted: {
        stackView.newStackFormLoaded(this);
        console.debug("process_loaded");
    }
    Connections:{
        target: stackView
        function onResult(status){
            console.log("[Process]Status:", status);
        }
    }
}
