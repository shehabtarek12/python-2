import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget, QLabel, QHBoxLayout, QStackedWidget, QComboBox, QLineEdit, QSpinBox
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont, QColor

class RTMApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Management Application")
        self.setGeometry(100, 100, 1100, 600)

        self.accounts = ["101 Account", "Non Voice Account", "SMB Account", "Smiles Account", "Prestige Account"]
        self.initUI()
        self.loadData()
        self.loadSLData()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadData)
        self.timer.timeout.connect(self.loadSLData)
        self.timer.start(10000)

    def initUI(self):
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.mainPage = QWidget()
        main_layout = QHBoxLayout(self.mainPage)

        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)

        filter_layout = QHBoxLayout()
        self.account_dropdown = QComboBox()
        self.account_dropdown.addItems(self.accounts)
        self.account_dropdown.currentIndexChanged.connect(self.loadData)
        self.account_dropdown.currentIndexChanged.connect(self.loadSLData)
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

        left_layout.addLayout(filter_layout)
        
        # Threshold Inputs
        threshold_layout = QHBoxLayout()
        self.yellow_threshold = QSpinBox()
        self.yellow_threshold.setRange(0, 10000)
        self.yellow_threshold.setValue(10)  # Default
        threshold_layout.addWidget(QLabel("Yellow Threshold:"))
        threshold_layout.addWidget(self.yellow_threshold)
        
        self.red_threshold = QSpinBox()
        self.red_threshold.setRange(0, 10000)
        self.red_threshold.setValue(20)  # Default
        threshold_layout.addWidget(QLabel("Red Threshold:"))
        threshold_layout.addWidget(self.red_threshold)
        
        apply_button = QPushButton("Apply Thresholds")
        apply_button.clicked.connect(self.loadData)
        threshold_layout.addWidget(apply_button)
        
        left_layout.addLayout(threshold_layout)

        self.agent_status_table = QTableWidget()
        left_layout.addWidget(self.agent_status_table)

        self.refresh_button = QPushButton("Refresh Now")
        self.refresh_button.clicked.connect(self.loadData)
        left_layout.addWidget(self.refresh_button)

        self.sl_label = QLabel("SL %: Loading...")
        self.sl_label.setFont(QFont("Arial", 14, QFont.Bold))
        left_layout.addWidget(self.sl_label)

        self.dropped_intervals_label = QLabel("Dropped Intervals: Loading...")
        self.dropped_intervals_label.setFont(QFont("Arial", 14, QFont.Bold))
        left_layout.addWidget(self.dropped_intervals_label)

        left_container.setLayout(left_layout)

        main_layout.addWidget(left_container)
        self.mainPage.setLayout(main_layout)
        self.stack.addWidget(self.mainPage)

    def loadData(self):
        try:
            df = pd.read_csv("agent_status.csv")
            if "Login ID" not in df.columns or "Status" not in df.columns:
                raise KeyError("Missing required columns in CSV")

            selected_account = self.account_dropdown.currentText()
            selected_status = self.status_filter.currentText()
            search_text = self.search_box.text().strip().lower()

            if "Account" in df.columns:
                df = df[df["Account"] == selected_account]
            if selected_status != "All" and "Status" in df.columns:
                df = df[df["Status"] == selected_status]
            if "Login ID" in df.columns:
                df = df[df["Login ID"].astype(str).str.lower().str.contains(search_text, na=False)]

            self.agent_status_table.setRowCount(df.shape[0])
            self.agent_status_table.setColumnCount(df.shape[1])
            self.agent_status_table.setHorizontalHeaderLabels(df.columns)
            
            yellow_threshold = self.yellow_threshold.value()
            red_threshold = self.red_threshold.value()
            
            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    item = QTableWidgetItem(str(df.iat[row, col]))
                    self.agent_status_table.setItem(row, col, item)
                    
                    if df.columns[col] == "Duration (min)":
                        try:
                            value = float(df.iat[row, col])
                            if value >= red_threshold:
                                item.setBackground(QColor("red"))
                            elif value >= yellow_threshold:
                                item.setBackground(QColor("yellow"))
                        except ValueError:
                            pass  # Ignore non-numeric values

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
