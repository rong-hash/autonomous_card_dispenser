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
      4:Failed_Mechanical_Failure
      5:Failed_Hardware_Fault
      6:Authorized
      7:Request Expired
      8:Prepare
      9:Insert
      10:Not Detected
      11:Invalid Card
    */
    Connections {
        target: stackView
        function onResult(status){
            console.log("[Process]Status:", status);
            if (status == 0) {
                busyIndicator.visible = false;
                cross.source = "images/check.png";
                cross.visible = true;
                text1.text = qsTr("Success");
            } else if (status == 1) {
                busyIndicator.visible = false;
                cross.visible = true;
                text1.text = qsTr("Failed: Connection Timed Out");
            } else if (status == 2) {
                busyIndicator.visible = false;
                cross.visible = true;
                text1.text = qsTr("Failed: Authentication Failed");
            } else if (status == 3) {
                busyIndicator.visible = false;
                cross.visible = true;
                text1.text = qsTr("Failed: Card Not Recognized");
            } else if (status == 4) {
                busyIndicator.visible = false;
                cross.visible = true;
                text1.text = qsTr("Failed: Mechanical Failure");
            } else if (status == 5) {
                busyIndicator.visible = false;
                cross.visible = true;
                text1.text = qsTr("Failed: Hardware Failure");
            } else if (status == 6) {
                console.log("Authorized");
                text1.text = qsTr("Authorized, Please Wait...");
            } else if (status == 7) {
                busyIndicator.visible = false;
                cross.visible = true;
                text1.text = qsTr("Request Expired");
            } else if (status == 8) {
                text1.text = qsTr("Preparing, Please Wait...")
            } else if (status == 9) {
                text1.text = qsTr("Please Insert Your Card...")
            } else if (status == 10) {
                busyIndicator.visible = false
                cross.visible = true;
                text1.text = qsTr("Card Not Detected!")
            } else if (status == 11) {
                busyIndicator.visible = false
                cross.visible = true;
                text1.text = qsTr("Invalid Card")
            }
            
        }
    }
}
