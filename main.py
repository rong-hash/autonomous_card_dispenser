import sys
import os

from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine, qmlRegisterType
from CameraService import QPicamera2Item, QPicamera2ItemService
from picamera2 import Picamera2
from AppService import QMLSigHub

if __name__ == "__main__":
    os.environ["QT_QPA_PLATFORM"]="eglfs"
    os.environ["QT_QPA_EGLFS_HIDECURSOR"]="1"
    app = QGuiApplication(sys.argv)
    #Register types
    qmlRegisterType(QPicamera2Item, 'PiCamera2', 1, 0, 'Picamera2Item')
    
    engine = QQmlApplicationEngine()
    engine.quit.connect(app.quit)
    engine.load('KIOSK_ui_py/content/App.qml')
    # engine.load('ui/App.qml')

    if (engine.rootObjects().count == 0): raise RuntimeError("QML initialization failed")
    rootObject = engine.rootObjects()[0]
    # cameraItem:QPicamera2Item = rootObject.findChild(QPicamera2Item, "cameraViewItem")

    # picamera2 = Picamera2()  # Your Picamera2 setup here
    cameraService = QPicamera2ItemService()
    sighub = QMLSigHub()
    sighub.registerQML(rootObject)
    sighub.registerCameeraService(cameraService)

    # # Connect signals and slots
    # cameraService.update_frame.connect(cameraItem.updateFrame)
    # cameraService.update_overlay_signal.connect(cameraItem.updateOverlay)

    # picamera2.start()

    print("fw")
    sys.exit(app.exec())

# from PyQt5.QtWidgets import QApplication
# from picamera2.previews.qt import QGlPicamera2
# from picamera2.previews.qt import QPicamera2
# from picamera2 import Picamera2
# os.environ["QT_QPA_PLATFORM"]="eglfs"
# os.environ["QT_QPA_EGLFS_HIDECURSOR"]="1"
# picam2 = Picamera2()
# picam2.configure(picam2.create_preview_configuration())
# app = QApplication([])
# qpicamera2 = QGlPicamera2(picam2, width=800, height=600, keep_ar=False)
# qpicamera2.setWindowTitle("Qt Picamera2 App")
# picam2.start()
# qpicamera2.show()
# app.exec()

# import time

# from picamera2 import Picamera2, Preview

# picam2 = Picamera2()
# picam2.start_preview(Preview.QT)

# preview_config = picam2.create_preview_configuration()
# picam2.configure(preview_config)

# picam2.start()
# time.sleep(5)
