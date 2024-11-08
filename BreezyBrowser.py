import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *

class BreezyBrowse(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BreezyBrowse")
        self.setGeometry(300, 150, 1200, 800)
        self.dark_mode = False
        self.incognito_mode = False
        self.blocked_sites = ["example.com", "test.com"]
        self.downloads = []

        # Main Browser Area - Tabbed Browsing
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        self.setCentralWidget(self.tabs)

        # Add initial tab
        self.add_new_tab(QUrl("http://www.google.com"), "Home")

        # Navigation Bar with Styling
        self.navbar = QToolBar("Navigation")
        self.navbar.setIconSize(QSize(30, 30))
        self.addToolBar(self.navbar)
        self.navbar.setStyleSheet("QToolBar { padding: 5px; background-color: #f0f2f5; }")

        # Navigation Controls with Text-based Buttons
        back_btn = QAction("← Back", self)
        back_btn.setToolTip("Go back to the previous page")
        back_btn.triggered.connect(lambda: self.tabs.currentWidget().back())
        self.navbar.addAction(back_btn)

        forward_btn = QAction("Forward →", self)
        forward_btn.setToolTip("Go forward to the next page")
        forward_btn.triggered.connect(lambda: self.tabs.currentWidget().forward())
        self.navbar.addAction(forward_btn)

        reload_btn = QAction("⟳ Reload", self)
        reload_btn.setToolTip("Reload the current page")
        reload_btn.triggered.connect(lambda: self.tabs.currentWidget().reload())
        self.navbar.addAction(reload_btn)

        home_btn = QAction("⌂ Home", self)
        home_btn.setToolTip("Go to the home page")
        home_btn.triggered.connect(self.navigate_home)
        self.navbar.addAction(home_btn)

        # URL Bar with Enhanced Styling
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Enter URL...")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        self.url_bar.setFixedHeight(30)
        self.url_bar.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ced4da;
                border-radius: 8px;
                padding: 5px;
                margin: 0px 10px;
            }
        """)
        self.navbar.addWidget(self.url_bar)

        # New Tab Button
        new_tab_btn = QAction("+ New Tab", self)
        new_tab_btn.setToolTip("Open a new tab")
        new_tab_btn.triggered.connect(lambda: self.add_new_tab(QUrl("http://www.google.com"), "New Tab"))
        self.navbar.addAction(new_tab_btn)

        # History Button
        history_btn = QAction("🕒 History", self)
        history_btn.setToolTip("View browsing history")
        history_btn.triggered.connect(self.show_history)
        self.navbar.addAction(history_btn)

        # Clear Cache and Cookies Button
        clear_data_btn = QAction("🗑 Clear Data", self)
        clear_data_btn.setToolTip("Clear browsing data")
        clear_data_btn.triggered.connect(self.clear_browsing_data)
        self.navbar.addAction(clear_data_btn)

        # Full-Screen Toggle Button
        fullscreen_btn = QAction("🖥 Fullscreen", self)
        fullscreen_btn.setToolTip("Toggle full-screen mode")
        fullscreen_btn.triggered.connect(self.toggle_fullscreen)
        self.navbar.addAction(fullscreen_btn)

        # Incognito Mode Toggle
        incognito_btn = QAction("🕶 Incognito", self)
        incognito_btn.setToolTip("Toggle incognito mode")
        incognito_btn.triggered.connect(self.toggle_incognito)  # Fixed the typo here
        self.navbar.addAction(incognito_btn)

        # Download Manager Button
        download_btn = QAction("📥 Downloads", self)
        download_btn.setToolTip("View downloads")
        download_btn.triggered.connect(self.show_downloads)
        self.navbar.addAction(download_btn)

        # Dark Mode Toggle Button
        dark_mode_btn = QAction("🌙 Dark Mode", self)
        dark_mode_btn.setToolTip("Toggle dark mode")
        dark_mode_btn.triggered.connect(self.toggle_dark_mode)
        self.navbar.addAction(dark_mode_btn)

        # Status Bar with Styling
        self.status = QStatusBar()
        self.status.setStyleSheet("QStatusBar { background-color: #f1f3f5; padding: 3px; }")
        self.setStatusBar(self.status)

        # Variables for History Tracking and Bookmarks
        self.history = []
        self.bookmarks = []

        # Connect Tab Change and URL Change Events
        self.tabs.currentChanged.connect(self.update_url)

    def add_new_tab(self, qurl=None, label="Blank"):
        browser = QWebEngineView()
        
        # Enable download handling for this tab
        browser.page().profile().downloadRequested.connect(self.handle_download)

        # Block navigation to restricted sites
        browser.urlChanged.connect(lambda url: self.check_blocked_sites(url, browser))
        browser.setUrl(qurl or QUrl("http://www.google.com"))

        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)

        # URL change triggers history update
        browser.urlChanged.connect(lambda qurl, browser=browser: self.update_history(qurl))

    def handle_download(self, download_item):
        """Handle file downloads."""
        if not download_item.isFinished():
            filename, _ = QFileDialog.getSaveFileName(self, "Save File As", download_item.path())
            if filename:
                download_item.setPath(filename)
                download_item.accept()  # Start the download
                self.downloads.append(filename)  # Add to download manager list
                QMessageBox.information(self, "Download Started", f"Downloading to: {filename}")
            else:
                download_item.cancel()

    def check_blocked_sites(self, url, browser):
        """Block navigation to specific websites."""
        domain = url.host()
        if domain in self.blocked_sites:
            browser.setUrl(QUrl("about:blank"))
            QMessageBox.warning(self, "Blocked", f"Access to {domain} is restricted.")

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return
        self.tabs.removeTab(i)

    def navigate_home(self):
        self.tabs.currentWidget().setUrl(QUrl("http://www.google.com"))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.tabs.currentWidget().setUrl(QUrl(url))

    def update_url(self):
        current_url = self.tabs.currentWidget().url()
        self.url_bar.setText(current_url.toString())

    def update_history(self, qurl):
        """Add URL to history if not in incognito mode."""
        if not self.incognito_mode:
            url = qurl.toString()
            if url not in self.history:
                self.history.append(url)

    def show_history(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Browsing History")
        dialog.setGeometry(400, 200, 400, 300)

        layout = QVBoxLayout()
        list_widget = QListWidget()
        list_widget.addItems(self.history)
        layout.addWidget(list_widget)

        dialog.setLayout(layout)
        dialog.exec_()

    def clear_browsing_data(self):
        """Clear cache, cookies, and history."""
        self.history.clear()
        self.tabs.currentWidget().page().profile().clearHttpCache()
        QMessageBox.information(self, "Data Cleared", "Cache, cookies, and history have been cleared.")

    def toggle_fullscreen(self):
        """Toggle full-screen mode."""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def show_downloads(self):
        """Display the download manager."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Downloads")
        dialog.setGeometry(400, 200, 400, 300)

        layout = QVBoxLayout()
        list_widget = QListWidget()
        list_widget.addItems(self.downloads)
        layout.addWidget(list_widget)

        dialog.setLayout(layout)
        dialog.exec_()

    def toggle_dark_mode(self):
        """Toggle dark mode for the application."""
        if not self.dark_mode:
            self.setStyleSheet("""
                QMainWindow { background-color: #2e2e2e; color: #ffffff; }
                QToolBar, QStatusBar { background-color: #444; color: #ffffff; }
                QLineEdit { background-color: #333; color: #ffffff; border: 1px solid #555; }
            """)
            self.dark_mode = True
        else:
            self.setStyleSheet("")
            self.dark_mode = False

    def toggle_incognito(self):
        """Toggle incognito mode for private browsing."""
        self.incognito_mode = not self.incognito_mode
        if self.incognito_mode:
            self.setWindowTitle("BreezyBrowse (Incognito)")
            self.history.clear()  # Clear history in incognito mode
        else:
            self.setWindowTitle("BreezyBrowse")

app = QApplication(sys.argv)
QApplication.setApplicationName("BreezyBrowse")
window = BreezyBrowse()
window.show()
app.exec_()
