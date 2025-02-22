import sys
import os
import yt_dlp
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QComboBox, QFileDialog
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIcon

class DownloadThread(QThread):
    update_status = pyqtSignal(str)
    download_complete = pyqtSignal()

    def __init__(self, url, resolution):
        super().__init__()
        self.url = url
        self.resolution = resolution

    def run(self):
        def progress_hook(d):
            if d['status'] == 'downloading':
                self.update_status.emit(f"📥 กำลังดาวน์โหลด: {d['_percent_str']} - {d['_eta_str']} เหลือเวลา")
            elif d['status'] == 'finished':
                self.update_status.emit("✅ ดาวน์โหลดเสร็จสิ้น!")
                self.download_complete.emit()

        if getattr(sys, 'frozen', False):  # ตรวจสอบว่ารันจาก .exe หรือไม่
            base_path = sys._MEIPASS  # PyInstaller จะสร้างโฟลเดอร์ชั่วคราวที่นี่
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))

        ffmpeg_path = os.path.join(base_path, "ffmpeg/bin/ffmpeg.exe")

        if not os.path.exists(ffmpeg_path):
            self.update_status.emit("⚠️ ไม่พบ ffmpeg.exe กรุณาตรวจสอบไฟล์")
            return

        os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)

        # กำหนดตัวเลือกการดาวน์โหลด
        ydl_opts = {
            'outtmpl': "%(title)s.%(ext)s",
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
        }

        # เลือกฟอร์แมตตามความละเอียดที่ผู้ใช้เลือก
        if self.resolution == "480p":
            ydl_opts['format'] = "bv*[height<=480]+ba/best"
        elif self.resolution == "720p":
            ydl_opts['format'] = "bv*[height<=720]+ba/best"
        elif self.resolution == "1080p":
            ydl_opts['format'] = "bv*[height<=1080]+ba/best"

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([self.url])
            except yt_dlp.utils.DownloadError:
                self.update_status.emit("❌ ดาวน์โหลดล้มเหลว ตรวจสอบ URL หรือการเชื่อมต่ออินเทอร์เน็ต")

class VideoDownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube Video Downloader")
        self.setWindowIcon(QIcon("1.ico"))
        self.setGeometry(200, 200, 600, 300)
        self.setStyleSheet("background-color: #2E2E2E; color: white; font-size: 14px;")
        self.layout = QVBoxLayout()

        self.url_label = QLabel("🔗 ใส่ลิงก์ YouTube:")
        self.layout.addWidget(self.url_label)

        self.url_input = QLineEdit(self)
        self.url_input.setStyleSheet("background-color: #444; color: white; padding: 5px; border-radius: 5px;")
        self.layout.addWidget(self.url_input)

        self.resolution_label = QLabel("🎞 เลือกความละเอียดวิดีโอ:")
        self.layout.addWidget(self.resolution_label)

        self.resolution_combo = QComboBox(self)
        self.resolution_combo.addItems(["480p", "720p", "1080p"])
        self.resolution_combo.setStyleSheet("background-color: #444; color: white; padding: 5px; border-radius: 5px;")
        self.layout.addWidget(self.resolution_combo)

        self.download_button = QPushButton("⬇️ ดาวน์โหลดวิดีโอ", self)
        self.download_button.setStyleSheet("background-color: #FF5733; color: white; padding: 8px; border-radius: 5px;")
        self.download_button.clicked.connect(self.download_video)
        self.layout.addWidget(self.download_button)

        self.mp3_button = QPushButton("🎵 ดาวน์โหลด MP3", self)
        self.mp3_button.setStyleSheet("background-color: #1E90FF; color: white; padding: 8px; border-radius: 5px;")
        self.mp3_button.clicked.connect(self.download_mp3)
        self.layout.addWidget(self.mp3_button)

        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #FFD700; font-weight: bold;")
        self.layout.addWidget(self.status_label)

        self.setLayout(self.layout)

    def download_video(self):
        url = self.url_input.text()
        resolution = self.resolution_combo.currentText()

        if url:
            self.status_label.setText("🔄 เริ่มดาวน์โหลด...")
            self.download_button.setEnabled(False)

            self.download_thread = DownloadThread(url, resolution)
            self.download_thread.update_status.connect(self.update_status)
            self.download_thread.download_complete.connect(self.refresh_app)
            self.download_thread.start()
        else:
            self.status_label.setText("❌ กรุณาใส่ URL ที่ถูกต้อง")

    def update_status(self, status):
        self.status_label.setText(status)

    def refresh_app(self):
        self.status_label.setText("<-------------------------------------------✅ ดาวน์โหลดเสร็จแล้ว!!----------------------------------------->\n<--------------------------------------Desing by kanes sakula v1.0.11-------------------------------------->")
        self.url_input.clear()
        self.download_button.setEnabled(True)

    def download_mp3(self):
        url = self.url_input.text()
        if not url:
            self.status_label.setText("❌ กรุณาใส่ URL ที่ถูกต้อง")
            return

        save_path = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์บันทึก MP3")
        if not save_path:
            return

        self.status_label.setText("🎵 กำลังดาวน์โหลด MP3...")

        ydl_opts = {
            "format": "bestaudio/best",
            "outtmpl": f"{save_path}/%(title)s.%(ext)s",
            "progress_hooks": [self.progress_hook],
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        }

        self._download(url, ydl_opts)

    def progress_hook(self, d):
        if d['status'] == 'downloading':
            self.status_label.setText(f"📥 {d['_percent_str']} - {d['_eta_str']} เหลือเวลา")
        elif d['status'] == 'finished':
            self.status_label.setText("🎶 ดาวน์โหลด MP3 เสร็จแล้ว!")

    def _download(self, url, ydl_opts):
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
            except yt_dlp.utils.DownloadError:
                self.status_label.setText("❌ ดาวน์โหลดล้มเหลว ตรวจสอบ URL หรือการเชื่อมต่ออินเทอร์เน็ต")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VideoDownloaderApp()
    window.show()
    sys.exit(app.exec())
