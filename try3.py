import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QLabel, QHBoxLayout, QStackedWidget, QComboBox, QLineEdit, QSpinBox
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont, QColor, QIcon

class RTMApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Management Application")
        self.setGeometry(100, 100, 1100, 700)

        self.accounts = ["101 Account", "Non Voice Account", "SMB Account", "Smiles Account", "Prestige Account"]
        self.nav_visible = False
        self.initUI()
        self.loadData()
        self.loadSLData()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadData)
        self.timer.start(10000)

    def initUI(self):
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.mainPage = QWidget()
        main_layout = QHBoxLayout(self.mainPage)

        self.nav_container = QWidget()
        self.nav_layout = QVBoxLayout(self.nav_container)

        self.burger_button = QPushButton()
        self.burger_button.setIcon(QIcon("menu_icon.png"))
        self.burger_button.clicked.connect(self.toggleNav)
        self.burger_button.setFixedSize(40, 40)
        self.burger_button.setStyleSheet("position: absolute; top: 100px; left: 10px;")
        main_layout.insertWidget(0, self.burger_button)

        self.nav_container.setVisible(self.nav_visible)
        main_layout.insertWidget(1, self.nav_container)

        for i in range(1, 5):
            button = QPushButton(f"Page {i}")
            button.clicked.connect(lambda _, idx=i: self.stack.setCurrentIndex(idx))
            self.nav_layout.addWidget(button)

        self.nav_container.setLayout(self.nav_layout)

        self.left_container = QWidget()
        self.left_layout = QVBoxLayout(self.left_container)

        filter_layout = QHBoxLayout()
        self.account_dropdown = QComboBox()
        self.account_dropdown.addItems(self.accounts)
        self.account_dropdown.currentIndexChanged.connect(self.loadData)
        filter_layout.addWidget(QLabel("Account:"))
        filter_layout.addWidget(self.account_dropdown)

        self.status_filter = QComboBox()
        self.status_filter.addItem("All")
        self.status_filter.addItems(["Available", "AUX", "Break", "Offline", "Unaligned AUX"])
        self.status_filter.currentIndexChanged.connect(self.loadData)
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search Agent...")
        self.search_box.textChanged.connect(self.loadData)
        filter_layout.addWidget(self.search_box)

        self.left_layout.addLayout(filter_layout)
        
        threshold_layout = QHBoxLayout()
        self.yellow_threshold = QSpinBox()
        self.yellow_threshold.setRange(0, 10000)
        self.yellow_threshold.setValue(10)
        threshold_layout.addWidget(QLabel("Yellow Threshold:")) #filters el yellow
        threshold_layout.addWidget(self.yellow_threshold)
        
        self.red_threshold = QSpinBox()
        self.red_threshold.setRange(0, 10000)
        self.red_threshold.setValue(20)
        threshold_layout.addWidget(QLabel("Red Threshold:")) #filters el red
        threshold_layout.addWidget(self.red_threshold)
        
        apply_button = QPushButton("Apply Thresholds")  #Zorar el apply bta3 el alwan
        apply_button.clicked.connect(self.loadData)
        threshold_layout.addWidget(apply_button)
        
        self.left_layout.addLayout(threshold_layout)

        self.agent_status_table = QTableWidget()
        self.left_layout.addWidget(self.agent_status_table)

        self.refresh_button = QPushButton("Refresh Now")  #Refresh kol 10 sec 
        self.refresh_button.clicked.connect(self.loadData)
        self.left_layout.addWidget(self.refresh_button)

        self.left_container.setLayout(self.left_layout)
        main_layout.addWidget(self.left_container)

        self.right_container = QWidget()
        self.right_layout = QVBoxLayout(self.right_container)

        self.right_layout.addWidget(QLabel("Status"))
        self.break_status_table = QTableWidget()
        self.right_layout.addWidget(self.break_status_table)

        self.sl_label = QLabel("SL %: Loading...")
        self.sl_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.right_layout.addWidget(self.sl_label)

        self.dropped_intervals_label = QLabel("Dropped Intervals: Loading...")
        self.dropped_intervals_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.right_layout.addWidget(self.dropped_intervals_label)

        self.right_container.setLayout(self.right_layout)
        main_layout.addWidget(self.right_container)

        self.mainPage.setLayout(main_layout)
        self.stack.addWidget(self.mainPage)
        
        for i in range(1, 5):
            page = QWidget()
            layout = QVBoxLayout()
            layout.addWidget(QLabel(f"This is Page {i}"))
            back_button = QPushButton("Back to Main Page")
            back_button.clicked.connect(lambda _, idx=0: self.stack.setCurrentIndex(idx))
            layout.addWidget(back_button)
            page.setLayout(layout)
            self.stack.addWidget(page)

    def toggleNav(self):
        self.nav_visible = not self.nav_visible
        self.nav_container.setVisible(self.nav_visible)

    def loadData(self):
        try:
            df = pd.read_csv("agent_status.csv")
            selected_status = self.status_filter.currentText()
            search_text = self.search_box.text().strip().lower()
            
            if selected_status != "All":
                df = df[df["Status"] == selected_status]
            
            if search_text:
                df = df[df["Login ID"].astype(str).str.lower().str.contains(search_text)]
            
            self.agent_status_table.setRowCount(df.shape[0])
            self.agent_status_table.setColumnCount(df.shape[1])
            self.agent_status_table.setHorizontalHeaderLabels(df.columns)

            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    item = QTableWidgetItem(str(df.iat[row, col]))
                    if col == 2:
                        duration = df.iat[row, col]
                        if duration >= self.red_threshold.value():
                            item.setBackground(QColor(255, 0, 0))
                        elif duration >= self.yellow_threshold.value():
                            item.setBackground(QColor(255, 255, 0))
                    self.agent_status_table.setItem(row, col, item)
            
            self.loadSLData()
        except Exception as e:
            print(f"Error loading data: {e}")

    def loadSLData(self):
        try:
            sl_df = pd.read_csv("sl_data.csv")
            dropped_df = pd.read_csv("dropped_intervals.csv")
            selected_account = self.account_dropdown.currentText()
            if "Account" in sl_df.columns and "SL %" in sl_df.columns:
                filtered_sl_df = sl_df[sl_df["Account"] == selected_account]
                if not filtered_sl_df.empty:
                    sl_value = filtered_sl_df["SL %"].iloc[-1]
                    self.sl_label.setText(f"SL %: {sl_value:.2f}")
                else:
                    self.sl_label.setText("SL %: No Data Available")
            if "Account" in dropped_df.columns and "Dropped Intervals" in dropped_df.columns:
                filtered_dropped_df = dropped_df[dropped_df["Account"] == selected_account]
                if not filtered_dropped_df.empty:
                    dropped_value = filtered_dropped_df["Dropped Intervals"].iloc[-1]
                    self.dropped_intervals_label.setText(f"Dropped Intervals: {dropped_value}")
        except Exception as e:
            print(f"Error loading SL data: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RTMApp()
    window.show()
    sys.exit(app.exec_())
