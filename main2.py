import sys
import os
import pandas as pd
import random
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QMessageBox, QComboBox, QLineEdit, QLabel, QHBoxLayout, QFrame
from PyQt5.QtCore import QTimer
from PyQt5.QtChart import QChart, QChartView, QPieSeries
from PyQt5.QtGui import QColor

class RTMApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Management Dashboard")
        self.setGeometry(100, 100, 1100, 700)
        
        self.accounts = ["101 Account", "Non Voice Account", "SMB Account", "Smiles Account", "Prestige Account"]
        self.initUI()
        self.loadData()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadData)
        self.timer.start(10000)

    def initUI(self):
        self.setStyleSheet("background-color: #2E3440; color: #D8DEE9;")
        layout = QHBoxLayout()
        
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(20, 20, 20, 20)
        
        filter_layout = QHBoxLayout()
        
        self.account_dropdown = QComboBox()
        self.account_dropdown.addItems(self.accounts)
        self.account_dropdown.currentIndexChanged.connect(self.updateSLData)
        self.account_dropdown.setStyleSheet("padding: 6px; border-radius: 10px; background-color: #4C566A; color: white;")
        filter_layout.addWidget(QLabel("Account:"))
        filter_layout.addWidget(self.account_dropdown)
        
        self.status_filter = QComboBox()
        self.status_filter.addItem("All")
        self.status_filter.addItems(["Available", "AUX", "Break", "Offline", "Unaligned AUX"])
        self.status_filter.currentIndexChanged.connect(self.loadData)
        self.status_filter.setStyleSheet("padding: 6px; border-radius: 10px; background-color: #4C566A; color: white;")
        filter_layout.addWidget(QLabel("Status:"))
        filter_layout.addWidget(self.status_filter)
        
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search Agent...")
        self.search_box.textChanged.connect(self.loadData)
        self.search_box.setStyleSheet("padding: 6px; border-radius: 10px; background-color: #4C566A; color: white;")
        filter_layout.addWidget(self.search_box)
        
        left_panel.addLayout(filter_layout)
        
        self.sl_label = QLabel("Service Level: Fetching...")
        self.sl_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #88C0D0;")
        left_panel.addWidget(self.sl_label)
        
        self.interval_label = QLabel("Dropped Intervals: Fetching...")
        self.interval_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #BF616A;")
        left_panel.addWidget(self.interval_label)
        
        self.table = QTableWidget()
        self.table.setStyleSheet("border-radius: 10px; background-color: #3B4252; color: white; padding: 5px;")
        left_panel.addWidget(self.table)
        
        self.refresh_button = QPushButton("Refresh Now")
        self.refresh_button.setStyleSheet("border-radius: 10px; background-color: #5E81AC; color: white; padding: 8px;")
        self.refresh_button.clicked.connect(self.loadData)
        left_panel.addWidget(self.refresh_button)
        
        layout.addLayout(left_panel)
        
        right_panel = QVBoxLayout()
        right_panel.setContentsMargins(10, 10, 10, 10)
        
        self.occupancy_chart_view = QChartView()
        self.occupancy_chart_view.setStyleSheet("border-radius: 15px; background-color: #434C5E; padding: 10px;")
        right_panel.addWidget(self.occupancy_chart_view)
        
        self.utilization_chart_view = QChartView()
        self.utilization_chart_view.setStyleSheet("border-radius: 15px; background-color: #434C5E; padding: 10px;")
        right_panel.addWidget(self.utilization_chart_view)
        
        layout.addLayout(right_panel)
        
        container = QWidget()
        container.setLayout(layout)
        container.setStyleSheet("border-radius: 15px; background-color: #2E3440;")
        self.setCentralWidget(container)

    def loadData(self):
        try:
            file_path = "agent_status.csv"
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"CSV file not found: {file_path}")
            
            df = pd.read_csv(file_path)
            if df.empty:
                raise ValueError("CSV file is empty.")
            
            selected_status = self.status_filter.currentText()
            if selected_status != "All":
                df = df[df["Status"] == selected_status]
            
            search_text = self.search_box.text().strip().lower()
            if search_text:
                df = df[df["Agent Name"].str.lower().str.contains(search_text, na=False)]
            
            self.table.setRowCount(df.shape[0])
            self.table.setColumnCount(df.shape[1])
            self.table.setHorizontalHeaderLabels(df.columns)
            
            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    self.table.setItem(row, col, QTableWidgetItem(str(df.iat[row, col])))
            
            self.updateSLData()
            self.updateCharts(df)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading data: {e}")
            print(f"Error loading data: {e}")
    
    def updateSLData(self):
        selected_account = self.account_dropdown.currentText()
        
        try:
            df = pd.read_csv("sl_data.csv")
            df = df[df["Account"] == selected_account]
            
            if df.empty:
                self.sl_label.setText("No SL data available.")
                self.interval_label.setText("No dropped intervals.")
                return
            
            latest_sl = df.iloc[-1]["Service Level"]
            dropped_intervals = df["Dropped Intervals"].sum()
            
            self.sl_label.setText(f"Service Level for {selected_account}: {latest_sl:.2f}%")
            self.interval_label.setText(f"Dropped Intervals: {dropped_intervals}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error fetching SL data: {e}")
            print(f"Error fetching SL data: {e}")
    
    def updateCharts(self, df):
        print("Charts updated with new data")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RTMApp()
    window.show()
    sys.exit(app.exec_())