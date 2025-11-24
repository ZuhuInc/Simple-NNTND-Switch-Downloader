"""
Zuhu's Keys & Firmware Downloader V1.0.1

By Zuhu | DC: ZuhuInc | DCS: https://discord.gg/Wr3wexQcD3
"""
import sys
import os
import requests
import json
import re
import time
import ctypes
from plyer import notification
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QVBoxLayout,
                             QHBoxLayout, QScrollArea, QStackedWidget, QPushButton,
                             QProgressBar, QLineEdit, QFormLayout, QFileDialog, 
                             QCheckBox, QMessageBox, QFrame)
from PyQt6.QtGui import QIcon, QFontDatabase, QFont, QPainter, QColor
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QObject, QThread, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty

# --- CONFIGURATION ---
CURRENT_VERSION = "V1.0.1"
KEYS_URL = "https://prodkeys.net/ryujinx-prod-keys-n25/#more-18"
FW_URL = "https://prodkeys.net/latest-switch-firmwares-v16/"
DATA_FOLDER = os.path.join(os.path.expanduser('~'), 'Documents', 'ZuhuProjects', 'ZuhuKeys')
SETTINGS_FILE = os.path.join(DATA_FOLDER, 'Settings.json')
ICON_URL = "https://raw.githubusercontent.com/ZuhuInc/Simple-NNTND-Switch-Downloader/refs/heads/main/Assets/NSPF-DWND-ICO.ico"
SETTINGS_ICON_URL = "https://raw.githubusercontent.com/ZuhuInc/Simple-NNTND-Switch-Downloader/refs/heads/main/Assets/NSPF-STNG-ICO.ico"
RELOAD_ICON_URL = "https://raw.githubusercontent.com/ZuhuInc/Simple-NNTND-Switch-Downloader/refs/heads/main/Assets/NSPF-RLD-ICO.ico"
FONT_URL = "https://github.com/ZuhuInc/Simple-NNTND-Switch-Downloader/raw/refs/heads/main/Assets/pixelmix.ttf"
ICON_PATH = os.path.join(DATA_FOLDER, 'cache', 'app_icon.ico')
SETTINGS_ICON_PATH = os.path.join(DATA_FOLDER, 'cache', 'settings_icon.ico')
RELOAD_ICON_PATH = os.path.join(DATA_FOLDER, 'cache', 'reload_icon.ico')
FONT_PATH = os.path.join(DATA_FOLDER, 'cache', 'pixelmix.ttf')
DEFAULT_DOWNLOAD_PATH = ""
SHOW_SPEED_IN_MBPS = True
ENABLE_NOTIFICATIONS = True

# --- STYLING ---
STYLESHEET = """
    QWidget { background-color: #1e1e1e; color: #e0e0e0; }
    
    QScrollArea { border: none; background-color: #1e1e1e; }
    
    /* Progress Bar */
    QProgressBar {
        border: 1px solid #444; border-radius: 4px; text-align: center;
        background-color: #2d2d2d; height: 14px; color: white; font-size: 10px;
    }
    QProgressBar::chunk { background-color: #00ff7f; border-radius: 3px; }
    
    /* Top Bar Inputs */
    QLineEdit {
        border: 1px solid #444; background-color: #2d2d2d;
        border-radius: 15px; 
        padding: 5px 12px; 
        color: #e0e0e0;
        min-height: 10px; 
    }
    QLineEdit:focus { border: 1px solid #00ff7f; }

    /* Circle Buttons */
    QPushButton#CircleBtn {
        border: 1px solid #444; background-color: #2d2d2d;
        border-radius: 17px; 
    }
    QPushButton#CircleBtn:hover { border-color: #00ff7f; background-color: #333; }

    /* Action Buttons */
    QPushButton.actionBtn {
        background-color: transparent;
        border: 1px solid #666;
        border-radius: 6px;
        color: #ccc;
        padding: 4px 12px;
        font-weight: bold;
    }
    QPushButton.actionBtn:hover {
        border-color: #00ff7f;
        color: #00ff7f;
        background-color: rgba(0, 255, 127, 0.05);
    }
    QPushButton.actionBtn:pressed {
        background-color: rgba(0, 255, 127, 0.1);
    }
    
    /* Back Button Style */
    QPushButton#TopBackBtn {
        background: transparent; border: none; color: #00ff7f; 
        text-align: left; font-weight: bold; font-size: 14px;
    }
    QPushButton#TopBackBtn:hover { color: #fff; }
"""

# --- SETTINGS MANAGER ---
def load_settings():
    global DEFAULT_DOWNLOAD_PATH, SHOW_SPEED_IN_MBPS, ENABLE_NOTIFICATIONS
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                DEFAULT_DOWNLOAD_PATH = settings.get('default_download_path', DEFAULT_DOWNLOAD_PATH)
                SHOW_SPEED_IN_MBPS = settings.get('show_speed_in_mbps', False)
                ENABLE_NOTIFICATIONS = settings.get('enable_notifications', True)
        except: pass

def save_settings_to_file():
    os.makedirs(DATA_FOLDER, exist_ok=True)
    settings = {
        'default_download_path': DEFAULT_DOWNLOAD_PATH,
        'show_speed_in_mbps': SHOW_SPEED_IN_MBPS,
        'enable_notifications': ENABLE_NOTIFICATIONS
    }
    with open(SETTINGS_FILE, 'w') as f: json.dump(settings, f, indent=4)

# --- CUSTOM TOGGLE ---
class PyToggle(QCheckBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(50, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._bg_color, self._circle_color, self._active_color = "#777", "#DDD", "#00ff7f"
        self._circle_position = 3
        self.animation = QPropertyAnimation(self, b"circle_position", self)
        self.animation.setDuration(300)
        self.stateChanged.connect(self.start_transition)

    def hitButton(self, pos):
        """Allows the entire 50x28 widget area to be clickable"""
        return self.contentsRect().contains(pos)

    def start_transition(self, state):
        self.animation.stop()
        self.animation.setEndValue(self.width() - 24 if state else 3)
        self.animation.start()
        
    def paintEvent(self, e):
        p = QPainter(self); p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self._active_color if self.isChecked() else self._bg_color))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawRoundedRect(0, 0, self.width(), self.height(), 14, 14)
        p.setBrush(QColor(self._circle_color))
        p.drawEllipse(int(self._circle_position), 3, 22, 22)
        p.end()
    
    def get_cp(self): return self._circle_position
    def set_cp(self, pos): self._circle_position = pos; self.update()
    circle_position = pyqtProperty(float, get_cp, set_cp)

# --- SCRAPER ENGINE ---
class ProdKeysScraper(QObject):
    status_update = pyqtSignal(str)
    
    def fetch_data(self):
        headers = {'User-Agent': 'Mozilla/5.0'}
        merged_data = {}
        self.status_update.emit("Fetching Keys...")
        try:
            r = requests.get(KEYS_URL, headers=headers, timeout=15)
            if r.status_code == 200:
                rows = re.findall(r'<tr.*?>(.*?)</tr>', r.text, re.DOTALL)
                for row in rows:
                    ver_match = re.search(r'<td[^>]*>\s*(v[\d\.]+)\s*</td>', row, re.IGNORECASE)
                    link_match = re.search(r'<a\s+href="([^"]+)"[^>]*>DOWNLOAD</a>', row, re.IGNORECASE)
                    if ver_match and link_match:
                        ver = ver_match.group(1).strip()
                        if ver not in merged_data: merged_data[ver] = {'version': ver}
                        merged_data[ver]['keys_url'] = link_match.group(1).strip()
        except Exception as e: print(f"Keys Error: {e}")

        self.status_update.emit("Fetching Firmware...")
        try:
            r = requests.get(FW_URL, headers=headers, timeout=15)
            if r.status_code == 200:
                rows = re.findall(r'<tr.*?>(.*?)</tr>', r.text, re.DOTALL)
                for row in rows:
                    ver_match = re.search(r'<td[^>]*>\s*(v[\d\.]+)\s*</td>', row, re.IGNORECASE)
                    if not ver_match: continue
                    ver = ver_match.group(1).strip()
                    links = re.findall(r'<a\s+href="([^"]+)"[^>]*>DOWNLOAD</a>', row, re.IGNORECASE)
                    if links:
                        norm_ver = ver.replace('V', 'v')
                        target_key = next((k for k in merged_data if k.lower() == norm_ver.lower()), norm_ver)
                        if target_key not in merged_data: merged_data[target_key] = {'version': target_key}
                        merged_data[target_key]['fw_url'] = links[0]
        except Exception as e: print(f"FW Error: {e}")

        def sort_key(item):
            v_str = item['version'].lower().replace('v', '')
            try: return [int(x) for x in v_str.split('.')]
            except: return [0]

        final_list = sorted(merged_data.values(), key=sort_key, reverse=True)
        self.status_update.emit("Ready")
        return final_list

# --- DOWNLOAD WORKER ---
class DownloadWorker(QThread):
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str)

    def __init__(self, download_tasks):
        super().__init__()
        self.tasks = download_tasks
        self.is_running = True

    def run(self):
        for i, (url, save_path) in enumerate(self.tasks):
            if not self.is_running: break
            filename = os.path.basename(save_path)
            self.progress.emit(0, f"Starting {filename}...")
            try:
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                total_length = int(response.headers.get('content-length', 0))
                dl = 0
                start_time = time.time()
                with open(save_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if not self.is_running: break
                        if chunk:
                            f.write(chunk)
                            dl += len(chunk)
                            if total_length > 0:
                                percent = int((dl / total_length) * 100)
                                elapsed = time.time() - start_time
                                speed = (dl / elapsed) if elapsed > 0 else 0
                                speed_str = f"{(speed * 8) / 1000000:.1f} Mbps" if SHOW_SPEED_IN_MBPS else f"{speed / 1000000:.1f} MB/s"
                                self.progress.emit(percent, f"Downloading {filename} | {percent}% | {speed_str}")
                if self.is_running: self.progress.emit(100, f"{filename} Complete")
            except Exception as e:
                self.finished.emit(False, f"Failed: {str(e)}")
                return
        if self.is_running: self.finished.emit(True, "All Downloads Complete")

# --- WIDGETS ---
class VersionRowWidget(QWidget):
    download_requested = pyqtSignal(str, dict) 
    def __init__(self, data, font):
        super().__init__()
        self.data = data
        self.setFixedHeight(60)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 5, 30, 5)
        layout.setSpacing(15)

        lbl_ver = QLabel(data['version'])
        lbl_ver.setFont(font)
        lbl_ver.setStyleSheet("font-size: 14px; font-weight: bold; color: #00ff7f;")
        layout.addWidget(lbl_ver)
        layout.addStretch()

        has_keys, has_fw = 'keys_url' in data, 'fw_url' in data
        if has_keys: self._add_btn(layout, "Download Keys", 'keys', font)
        if has_fw: self._add_btn(layout, "Download Firmware", 'fw', font)
        if has_keys and has_fw: self._add_btn(layout, "Download Both", 'both', font, True)

        self.line = QFrame(self)
        self.line.setGeometry(0, 59, 2000, 1)
        self.line.setStyleSheet("background-color: #333;")

    def _add_btn(self, layout, text, action, font, is_both=False):
        btn = QPushButton(text)
        btn.setFont(font)
        btn.setProperty("class", "actionBtn")
        if is_both:
            btn.setStyleSheet("""
                QPushButton { border: 1px solid #00ff7f; color: #00ff7f; background-color: rgba(0,255,127,0.05); }
                QPushButton:hover { background-color: rgba(0,255,127,0.2); }
            """)
        btn.clicked.connect(lambda: self.download_requested.emit(action, self.data))
        layout.addWidget(btn)

class SettingsPage(QWidget):
    def __init__(self, font):
        super().__init__()
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(20)
        
        lbl_path = QLabel("Default Path:")
        lbl_path.setFont(font)
        self.path_edit = QLineEdit(DEFAULT_DOWNLOAD_PATH)
        self.path_edit.setFont(font)
        self.path_edit.setPlaceholderText("Click Save to update default...")
        form.addRow(lbl_path, self.path_edit)

        lbl_speed = QLabel("MB/s or Mbps:")
        lbl_speed.setFont(font)

        speed_container = QWidget()
        speed_layout = QHBoxLayout(speed_container)
        speed_layout.setContentsMargins(0, 0, 0, 0)
        speed_layout.setSpacing(10)

        self.tog_speed = PyToggle()
        self.tog_speed.setChecked(SHOW_SPEED_IN_MBPS)
        
        self.lbl_speed_unit = QLabel("Mbps" if SHOW_SPEED_IN_MBPS else "MB/s")
        self.lbl_speed_unit.setFont(font)
        self.lbl_speed_unit.setStyleSheet("color: #aaa;") 
        self.tog_speed.stateChanged.connect(self.update_speed_label)

        speed_layout.addWidget(self.tog_speed)
        speed_layout.addWidget(self.lbl_speed_unit)
        speed_layout.addStretch() 
        form.addRow(lbl_speed, speed_container)

        lbl_notif = QLabel("Notifications:")
        lbl_notif.setFont(font)

        notif_container = QWidget()
        notif_layout = QHBoxLayout(notif_container)
        notif_layout.setContentsMargins(0, 0, 0, 0)
        notif_layout.setSpacing(10)

        self.tog_notif = PyToggle()
        self.tog_notif.setChecked(ENABLE_NOTIFICATIONS)
        self.lbl_notif_state = QLabel("On" if ENABLE_NOTIFICATIONS else "Off")
        self.lbl_notif_state.setFont(font)
        self.lbl_notif_state.setStyleSheet("color: #aaa;")

        self.tog_notif.stateChanged.connect(self.update_notif_label)

        notif_layout.addWidget(self.tog_notif)
        notif_layout.addWidget(self.lbl_notif_state)
        notif_layout.addStretch()
        form.addRow(lbl_notif, notif_container)
        
        layout.addLayout(form)
        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.addStretch() 
        
        self.btn_style_normal = """
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 8px;
                color: #e0e0e0;
                font-weight: bold;
            }
            QPushButton:hover {
                border: 1px solid #00ff7f;
                color: #00ff7f;
                background-color: #333;
            }
        """
        self.btn_style_saved = """
            QPushButton {
                background-color: #2d2d2d;
                border: 1px solid #00ff7f;
                border-radius: 8px;
                padding: 8px;
                color: #00ff7f;
                font-weight: bold;
            }
        """

        btn_save = QPushButton("Save Settings")
        btn_save.setFont(font)
        btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_save.setFixedWidth(200)
        btn_save.setStyleSheet(self.btn_style_normal)
        btn_save.clicked.connect(self.save)
        
        btn_layout.addWidget(btn_save)
        layout.addLayout(btn_layout)

    def update_speed_label(self, state):
        self.lbl_speed_unit.setText("Mbps" if state else "MB/s")

    def update_notif_label(self, state):
        self.lbl_notif_state.setText("On" if state else "Off")

    def save(self):
        global DEFAULT_DOWNLOAD_PATH, SHOW_SPEED_IN_MBPS, ENABLE_NOTIFICATIONS
        DEFAULT_DOWNLOAD_PATH = self.path_edit.text()
        SHOW_SPEED_IN_MBPS = self.tog_speed.isChecked()
        ENABLE_NOTIFICATIONS = self.tog_notif.isChecked()
        save_settings_to_file()
        
        sender = self.sender()
        original_text = "Save Settings"
        
        sender.setText("Saved")
        sender.setStyleSheet(self.btn_style_saved)
        QTimer.singleShot(1500, lambda: self._reset_btn(sender, original_text))
        print("Settings Saved")

    def _reset_btn(self, btn, text):
        btn.setText(text)
        btn.setStyleSheet(self.btn_style_normal)

# --- MAIN WINDOW ---
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Zuhu's Keys & Firmware Downloader {CURRENT_VERSION}")
        self.resize(900, 575)
        self.setStyleSheet(STYLESHEET)
        
        self.data_list = []
        self.scraper = ProdKeysScraper()
        
        self.asset_cache = os.path.join(DATA_FOLDER, 'cache')
        os.makedirs(self.asset_cache, exist_ok=True)
        self.load_assets()
        
        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))
            
        load_settings()
        self.initUI()
        QTimer.singleShot(100, self.refresh_data)

    def load_assets(self):
        def download_if_missing(url, path, name):
            if not os.path.exists(path):
                try:
                    print(f"Downloading {name}...")
                    r = requests.get(url, timeout=10)
                    with open(path, 'wb') as f: f.write(r.content)
                except Exception as e: print(f"Failed {name}: {e}")

        download_if_missing(ICON_URL, ICON_PATH, "App Icon")
        download_if_missing(SETTINGS_ICON_URL, SETTINGS_ICON_PATH, "Settings Icon")
        download_if_missing(RELOAD_ICON_URL, RELOAD_ICON_PATH, "Reload Icon")
        download_if_missing(FONT_URL, FONT_PATH, "Font")
        
        self.main_font = QFont("Segoe UI", 10)
        if os.path.exists(FONT_PATH):
            fid = QFontDatabase.addApplicationFont(FONT_PATH)
            if fid != -1:
                fam = QFontDatabase.applicationFontFamilies(fid)[0]
                self.main_font = QFont(fam, 12)

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 15, 20, 15)
        main_layout.setSpacing(15)
        top_bar = QHBoxLayout()
        
        self.status_container = QWidget()
        status_layout = QVBoxLayout(self.status_container)
        status_layout.setContentsMargins(0,0,0,0); status_layout.setSpacing(2)
        
        self.status_label = QLabel("Ready")
        self.status_label.setFont(self.main_font)
        self.status_label.setStyleSheet("color: #aaa;")
        
        self.pbar = QProgressBar()
        self.pbar.setFixedWidth(550)
        self.pbar.setVisible(False)
        
        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.pbar)
        
        self.btn_back_top = QPushButton("<< Back to Library")
        self.btn_back_top.setObjectName("TopBackBtn")
        self.btn_back_top.setFont(self.main_font)
        self.btn_back_top.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_back_top.setVisible(False)
        self.btn_back_top.clicked.connect(self.go_home)

        top_bar.addWidget(self.status_container)
        top_bar.addWidget(self.btn_back_top)
        top_bar.addStretch()

        self.search_inp = QLineEdit()
        self.search_inp.setPlaceholderText("Search Version...")
        self.search_inp.setFixedWidth(210)
        self.search_inp.setFont(self.main_font)
        self.search_inp.textChanged.connect(self.filter_list)
        top_bar.addWidget(self.search_inp)

        btn_reload = QPushButton()
        btn_reload.setObjectName("CircleBtn")
        btn_reload.setFixedSize(35, 35)
        btn_reload.setToolTip("Reload List")
        if os.path.exists(RELOAD_ICON_PATH):
            btn_reload.setIcon(QIcon(RELOAD_ICON_PATH))
            btn_reload.setIconSize(QSize(25, 25))
        else: btn_reload.setText("↻")
        btn_reload.clicked.connect(self.refresh_data)
        top_bar.addWidget(btn_reload)

        btn_settings = QPushButton()
        btn_settings.setObjectName("CircleBtn")
        btn_settings.setFixedSize(35, 35)
        if os.path.exists(SETTINGS_ICON_PATH):
            btn_settings.setIcon(QIcon(SETTINGS_ICON_PATH))
            btn_settings.setIconSize(QSize(25, 25))
        else: btn_settings.setText("⚙")
        btn_settings.clicked.connect(self.go_settings)
        top_bar.addWidget(btn_settings)
        
        main_layout.addLayout(top_bar)
        main_layout.addLayout(top_bar)
        self.stack = QStackedWidget()
        
        self.page_list = QWidget()
        list_layout = QVBoxLayout(self.page_list)
        list_layout.setContentsMargins(0,0,0,0)
        
        header_widget = QWidget()
        header_widget.setStyleSheet("border-bottom: 1px solid #444; background-color: #252525; border-radius: 4px;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 30, 10) 
        
        lbl_ver_head = QLabel("Versions")
        lbl_ver_head.setFont(self.main_font)
        lbl_ver_head.setStyleSheet("color: #888; font-weight: bold; border: none;")
        
        lbl_act_head = QLabel("Actions")
        lbl_act_head.setFont(self.main_font)
        lbl_act_head.setStyleSheet("color: #888; font-weight: bold; border: none;")
        
        header_layout.addWidget(lbl_ver_head)
        header_layout.addStretch()
        header_layout.addWidget(lbl_act_head)
        
        list_layout.addWidget(header_widget)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.list_container = QWidget()
        self.list_vbox = QVBoxLayout(self.list_container)
        self.list_vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.list_container)
        list_layout.addWidget(self.scroll)
        self.stack.addWidget(self.page_list)
        
        self.page_settings = SettingsPage(self.main_font)
        self.stack.addWidget(self.page_settings)

        main_layout.addWidget(self.stack)

    def go_settings(self):
        self.status_container.hide()
        self.btn_back_top.show()
        self.stack.setCurrentIndex(1)

    def go_home(self):
        self.btn_back_top.hide()
        self.status_container.show()
        self.stack.setCurrentIndex(0)

    def refresh_data(self):
        self.status_label.setText("Loading...")
        while self.list_vbox.count():
            item = self.list_vbox.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        
        self.loader_thread = QThread()
        self.scraper.moveToThread(self.loader_thread)
        self.loader_thread.started.connect(lambda: self.run_scraper())
        self.loader_thread.start()

    def run_scraper(self):
        data = self.scraper.fetch_data()
        self.data_list = data
        self.filter_list("")
        self.status_label.setText(f"Found {len(data)} versions.")
        self.loader_thread.quit()

    def filter_list(self, text):
        while self.list_vbox.count():
            w = self.list_vbox.takeAt(0).widget()
            if w: w.setParent(None)
        
        text = text.lower()
        for item in self.data_list:
            if text in item['version'].lower():
                row = VersionRowWidget(item, self.main_font)
                row.download_requested.connect(self.handle_download)
                self.list_vbox.addWidget(row)

    def handle_download(self, mode, data):
        directory = QFileDialog.getExistingDirectory(self, "Select Download Folder", DEFAULT_DOWNLOAD_PATH)
        if not directory: return
        
        tasks = []
        if mode in ['keys', 'both'] and (url := data.get('keys_url')):
            tasks.append((url, os.path.join(directory, f"ProdKeys_{data['version']}.zip")))
        if mode in ['fw', 'both'] and (url := data.get('fw_url')):
            tasks.append((url, os.path.join(directory, f"Firmware_{data['version']}.zip")))
        if not tasks:
            QMessageBox.warning(self, "Error", "No valid links found.")
            return

        self.pbar.setVisible(True); self.pbar.setValue(0)
        self.status_label.setText("Starting download...")
        
        self.dl_thread = DownloadWorker(tasks)
        self.dl_thread.progress.connect(self.update_progress)
        self.dl_thread.finished.connect(self.download_finished)
        self.dl_thread.start()

    def update_progress(self, val, text):
        self.pbar.setValue(val); self.status_label.setText(text)

    def download_finished(self, success, msg):
        self.pbar.setVisible(False); self.status_label.setText(msg)
        if success and ENABLE_NOTIFICATIONS:
            try: notification.notify(title="Zuhu's Keys & Firmware Downloader", message="Download Complete", app_icon=ICON_PATH, timeout=5)
            except: pass
        elif not success: QMessageBox.critical(self, "Error", msg)

if __name__ == '__main__':
    myappid = 'NNTND-SWTCH-DWNLDR'
    try: ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except: pass
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())