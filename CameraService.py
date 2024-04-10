import logging

import numpy as np
from PyQt5.QtCore import (QSize, QSocketNotifier,QObject, QTimer,
                          pyqtSignal, pyqtSlot, pyqtProperty)
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtQuick import QQuickPaintedItem
from picamera2.picamera2 import Picamera2
from pyzbar.pyzbar import decode

class QPicamera2Item(QQuickPaintedItem):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._frame = None
        self._overlay = None

    @pyqtSlot(QImage)
    def updateFrame(self, frame: QImage):
        self._frame = frame
        self.update()  
    
    @pyqtSlot(QImage)
    def updateOverlay(self, overlay: QImage):
        self._overlay = overlay
        self.update()  

    def paint(self, painter: QPainter):
        if self._frame:
            painter.drawImage(self.contentsBoundingRect(), self._frame)
        else:
            #painter.drawImage(self.contentsBoundingRect(), self._ph)
            pass
        if self._overlay:
            painter.drawImage(self.contentsBoundingRect(), self._overlay)
        return

class QPicamera2ItemService(QObject):
    update_overlay_signal = pyqtSignal(QImage)
    update_frame_signal = pyqtSignal(QImage)
    qr_decode = pyqtSignal(bytes)
    

    def __init__(self, picam2:Picamera2|None = None, width=800, height=600, preview_window=None):
        super().__init__(parent=None)
        if picam2 == None:
            self.picamera2:Picamera2 = Picamera2()
        else:
            self.picamera2:Picamera2 = picam2
        self.preview_window = preview_window
        self.image_size = None
        self.size = QSize(width, height)
        self.image:QImage|None = None
        self.overlay:QImage|None = None
        self.timer:QTimer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.capture)
        self.orderCapture = False

        #self.update_overlay_signal.connect(self.update_overlay)
        
        
        # Must always run cleanup when this widget goes away.
        self.destroyed.connect(lambda: self.cleanup()) #TODO: Connect Destoryed to clean up?
        self.running = False

    def cam_start(self):
        self.picamera2.start()

    def cleanup(self):
        print("cleanup called")
        if not self.running:
            return
        self.running = False
        self.timer.stop()
        del self.overlay
        self.camera_notifier.deleteLater()
        # We have to tell both the preview window and the Picamera2 object that we have
        # disappeared.
        self.picamera2.detach_preview()
        self.picamera2.stop()
        if self.preview_window is not None:  # will be none when a proper Qt app
            self.preview_window.qpicamera2 = None

    def init(self):
        if self.running: return
        self.overlay = None
        self.picamera2.attach_preview(self.preview_window)
        self.camera_notifier = QSocketNotifier(self.picamera2.notifyme_r,
                                               QSocketNotifier.Read, self)
        self.camera_notifier.activated.connect(self.handle_requests)
        self.running = True

    def set_overlay(self, overlay):
        camera_config = self.picamera2.camera_config
        if camera_config is None:
            raise RuntimeError("Camera must be configured before using set_overlay")
        if overlay is not None:
            overlay = np.copy(overlay, order='C')
            shape = overlay.shape
            qim = QImage(overlay.data, shape[1], shape[0], QImage.Format_RGBA8888)
            self.overlay = qim
            # No scaling here - we leave it to fitInView to set that up.
        self.update_overlay_signal.emit(self.overlay)


    def resizeEvent(self, event):
        self.fitInView()

    def render_request(self, completed_request):
        """Draw the camera image using Qt."""
        if not self.running:
            return

        camera_config = completed_request.config
        display_stream_name = camera_config['display']
        stream_config = camera_config[display_stream_name]

        img = completed_request.make_array(display_stream_name)
        # Crop width for two reasons: (1) to remove "stride" padding from YUV images;
        # (2) to ensure the RGB buffer passed to QImage has mandatory 4-byte alignment.
        # [TODO: Consider QImage.Format_RGB32, if byte order can be made correct]
        imgnp = np.ascontiguousarray(img[:, :, :3])
        fmt = QImage.Format_BGR888 if stream_config['format'] in ('RGB888', 'XRGB8888') else QImage.Format_RGB888
        self.image = QImage(imgnp.data, imgnp.shape[1], imgnp.shape[0], fmt)
        # Add the pixmap to the scene if there wasn't one, or replace it if the images have
        # changed size.
        self.update_frame_signal.emit(self.image)
        if (self.orderCapture):
            self.orderCapture = False
            #self.image.save('temp.bmp','BMP',100)
            rl:list = decode(imgnp)
            if (len(rl) != 1): return
            self.timer.stop()   #Stop Timer
            print(rl[0].data)
            # print(type(rl[0].data))
            self.qr_decode.emit(rl[0].data)


    @pyqtSlot()
    def handle_requests(self):
        if not self.running:
            return
        self.picamera2.notifymeread.read()
        self.picamera2.process_requests(self)


    @pyqtSlot(QPicamera2Item)
    def register_camearitem(self, obj:QPicamera2Item):
        self.init()
        obj.destroyed.connect(lambda: self.cleanup())
        self.update_frame_signal.connect(obj.updateFrame)
        self.update_overlay_signal.connect(obj.updateOverlay)
        self.picamera2.start()
        self.timer.start()

    @pyqtSlot()
    def capture(self):
        self.orderCapture = True
        

