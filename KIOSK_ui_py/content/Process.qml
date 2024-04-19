import QtQuick 2.15

ProcessForm {
    Component.onCompleted: {
        stackView.newStackFormLoaded(this);
        console.debug("process_loaded");
    }
    /*
      Status Define:
      0:Success
      1:Failed_Timed_Out
      2:Failed_Bad_Identity
      3:Failed_Bad_Card
    */
    Connections {
        target: stackView
        function onResult(status){
            console.log("[Process]Status:", status);
        }
    }
}
