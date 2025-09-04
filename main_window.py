# gui/main_window.py
import sys, cv2, numpy as np, logging
from pathlib import Path
from PyQt5.QtWidgets import *
from PyQt5.QtGui     import *
from PyQt5.QtCore    import *
from core.pipeline   import MangaTranslationPipeline

# Qt → logging bridge
from PyQt5.QtCore import qInstallMessageHandler, QtMsgType

def qt_message_handler(mode, context, message):
    if mode == QtMsgType.QtDebugMsg:
        logging.debug(message)
    elif mode == QtMsgType.QtWarningMsg:
        logging.warning(message)
    elif mode == QtMsgType.QtCriticalMsg:
        logging.error(message)
    elif mode == QtMsgType.QtFatalMsg:
        logging.critical(message)

qInstallMessageHandler(qt_message_handler)

def cv2_to_pixmap(img):
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    h,w,ch = rgb.shape
    qimg = QImage(rgb.data, w, h, ch*w, QImage.Format_RGB888)
    return QPixmap.fromImage(qimg).scaled(400,600, Qt.KeepAspectRatio)

class Worker(QThread):
    finished = pyqtSignal(np.ndarray)
    error    = pyqtSignal(str)
    def __init__(self, path, pipeline):
        super().__init__()
        self.path = path
        self.pipeline = pipeline

    def run(self):
        try:
            img,_ = self.pipeline.process(self.path)
            self.finished.emit(img)
        except Exception as e:
            logging.getLogger("Worker").exception("Worker failed")
            self.error.emit(str(e))

class PerformanceWidget(QWidget):
    def __init__(self, translator):
        super().__init__()
        self.translator = translator
        v = QVBoxLayout()
        v.addWidget(QLabel("📊 إحصائيات الأداء"))
        self.txt = QTextEdit(); self.txt.setReadOnly(True); self.txt.setMaximumHeight(150)
        v.addWidget(self.txt)
        self.setLayout(v)
        self.timer = QTimer(); self.timer.timeout.connect(self.update_stats); self.timer.start(2000)

    def update_stats(self):
        s = self.translator.get_performance_stats()
        out = (f"🔧 جهاز: {s['device']}\n"
               f"🧠 CPU: {s['cpu_percent']:.1f}%\n"
               f"💾 RAM: {s['ram_used_gb']:.1f}/{s['ram_total_gb']:.1f} GB\n")
        if 'gpu_memory_used_gb' in s:
            out += f"🎮 GPU: {s['gpu_memory_used_gb']:.1f}/{s['gpu_memory_total_gb']:.1f} GB\n"
        self.txt.setPlainText(out)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("مترجم مانجا v2.0")
        self.resize(1000,700)

        self.pipeline   = MangaTranslationPipeline()
        self.translator = self.pipeline.translator

        layout = QVBoxLayout()
        self.label = QLabel("اسحب الصورة أو انقر لفتح")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border:2px dashed #aaa; padding:20px;")
        self.label.setAcceptDrops(True)
        self.label.mousePressEvent = self.open_file

        self.btn = QPushButton("⚡ ترجم إلى العربية")
        self.btn.clicked.connect(self.translate)
        self.btn.setEnabled(False)

        self.perf = PerformanceWidget(self.translator)

        layout.addWidget(self.label)
        layout.addWidget(self.btn)
        layout.addWidget(self.perf)

        container = QWidget(); container.setLayout(layout)
        self.setCentralWidget(container)
        self.image_path = None

    def dragEnterEvent(self, e):
        if e.mimeData().hasUrls(): e.accept()

    def dropEvent(self, e):
        p = e.mimeData().urls()[0].toLocalFile()
        if p.lower().endswith(('.png','.jpg','.jpeg','.webp')):
            self.load_image(p)

    def open_file(self, e=None):
        p,_ = QFileDialog.getOpenFileName(self, "اختر صورة", "", "Images (*.png *.jpg *.jpeg *.webp)")
        if p: self.load_image(p)

    def load_image(self, p):
        self.image_path = p
        pix = cv2.imread(p)
        self.label.setPixmap(cv2_to_pixmap(pix))
        self.btn.setEnabled(True)

    def translate(self):
        self.btn.setText("جاري الترجمة...")
        self.worker = Worker(self.image_path, self.pipeline)
        self.worker.finished.connect(self.on_done)
        self.worker.error.connect(lambda e: QMessageBox.critical(self, "خطأ", e))
        self.worker.start()

    def on_done(self, img):
        self.label.setPixmap(cv2_to_pixmap(img))
        self.btn.setText("✅ تمت!")

def run_gui():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())