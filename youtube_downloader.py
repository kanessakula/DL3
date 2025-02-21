import sys
import yt_dlp
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QFileDialog
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt

class YouTubeDownloader(QWidget):
    def __init__(self):
        super().__init__()

        # ตั้งชื่อหน้าต่างและขนาด
        self.setWindowTitle("YouTube Video Downloader")
        self.setGeometry(100, 100, 400, 300)

        # เปลี่ยนสีพื้นหลังของหน้าต่าง
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(30, 30, 30))
        palette.setColor(QPalette.ColorRole.WindowText, QColor("white"))
        self.setPalette(palette)

        # ตั้ง layout
        layout = QVBoxLayout()

        # ปรับขนาดฟอนต์สำหรับ QLineEdit
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("กรุณาใส่ลิงก์ YouTube...")
        self.url_input.setStyleSheet("background-color: #333; color: white; border-radius: 5px; padding: 5px;")
        self.url_input.setFont(QFont("Arial", 12))
        layout.addWidget(self.url_input)

        # ปุ่มดาวน์โหลดวิดีโอ
        self.download_video_button = QPushButton("ดาวน์โหลดวิดีโอ")
        self.download_video_button.setStyleSheet("""
            background-color: #28a745;
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        """)
        self.download_video_button.clicked.connect(self.download_video)
        layout.addWidget(self.download_video_button)

        # ปุ่มดาวน์โหลด MP3
        self.download_mp3_button = QPushButton("ดาวน์โหลด MP3")
        self.download_mp3_button.setStyleSheet("""
            background-color: #007bff;
            color: white;
            border-radius: 5px;
            padding: 10px;
            font-size: 14px;
        """)
        self.download_mp3_button.clicked.connect(self.download_mp3)
        layout.addWidget(self.download_mp3_button)

        # QLabel สำหรับแสดงสถานะการดาวน์โหลด
        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Arial", 12))
        self.status_label.setStyleSheet("color: white;")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def download_video(self):
        url = self.url_input.text()
        if not url:
            return

        # เคลียร์สถานะเดิม
        self.status_label.setText("")

        save_path = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์บันทึกวิดีโอ")
        if not save_path:
            return

        self.status_label.setText("🔄 กำลังกดาวน์โหลดวิดีโอ...")

        ydl_opts = {
            "format": "best[ext=mp4]",
            "outtmpl": f"{save_path}/%(title)s.%(ext)s",
            "progress_hooks": [self.progress_hook],  # ใช้ hook เพื่อติดตามสถานะการดาวน์โหลด
        }
        self._download(url, ydl_opts)

    def download_mp3(self):
        url = self.url_input.text()
        if not url:
            return

        # เคลียร์สถานะเดิม
        self.status_label.setText("")

        save_path = QFileDialog.getExistingDirectory(self, "เลือกโฟลเดอร์บันทึก MP3")
        if not save_path:
            return

        self.status_label.setText("🔄 กำลังกดาวน์โหลด MP3...")

        ydl_opts = {
            "format": "bestaudio[ext=m4a]",
            "outtmpl": f"{save_path}/%(title)s.%(ext)s",
            "progress_hooks": [self.progress_hook],  # ใช้ hook เพื่อติดตามสถานะการดาวน์โหลด
        }
        self._download(url, ydl_opts)

    def progress_hook(self, d):
        if d["status"] == "downloading":
            percent = d["downloaded_bytes"] / d["total_bytes"] * 100
            self.status_label.setText(f"กำลังกดาวน์โหลด... {percent:.2f}%")

        elif d["status"] == "finished":
            self.status_label.setText("✅ ดาวน์โหลดเสร็จสิ้น!")

    def _download(self, url, ydl_opts):
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            print(f"เกิดข้อผิดพลาด: {str(e)}")
            self.status_label.setText(f"❌ เกิดข้อผิดพลาด: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = YouTubeDownloader()
    window.show()
    sys.exit(app.exec())
