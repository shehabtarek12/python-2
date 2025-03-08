import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTableWidget, QTableWidgetItem, 
    QVBoxLayout, QWidget, QMessageBox, QComboBox, QLineEdit, QLabel, QHBoxLayout, QStackedWidget
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont, QMovie

class RTMApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Management Dashboard")
        self.setGeometry(100, 100, 900, 600)
        
        self.accounts = ["101 Account", "Non Voice Account", "SMB Account", "Smiles Account", "Prestige Account"]
        self.initUI()
        self.loadData()
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadData)
        self.timer.start(10000)

    def initUI(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #E0E0E0;
                font-size: 14px;
            }
            QPushButton {
                background-color: #1E88E5;
                color: white;
                border-radius: 10px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QTableWidget {
                background-color: #1E1E1E;
                color: white;
                gridline-color: #333;
            }
            QHeaderView::section {
                background-color: #333;
                color: white;
            }
            QComboBox, QLineEdit {
                background-color: #1E1E1E;
                color: white;
                border: 1px solid #333;
                padding: 5px;
            }
        """)
        
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        self.mainPage = QWidget()
        self.page1 = QWidget()
        self.page2 = QWidget()
        self.page3 = QWidget()
        self.page4 = QWidget()
        
        self.setupPage(self.page1)
        self.setupPage(self.page2)
        self.setupPage(self.page3)
        self.setupPage(self.page4)
        
        self.stack.addWidget(self.mainPage)
        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)
        self.stack.addWidget(self.page3)
        self.stack.addWidget(self.page4)
        
        layout = QHBoxLayout()
        
        left_panel = QVBoxLayout()
        
        self.page1_button = QPushButton("Go to Page 1")
        self.page1_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.page1))
        left_panel.addWidget(self.page1_button)
        
        self.page2_button = QPushButton("Go to Page 2")
        self.page2_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.page2))
        left_panel.addWidget(self.page2_button)
        
        self.page3_button = QPushButton("Go to Page 3")
        self.page3_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.page3))
        left_panel.addWidget(self.page3_button)
        
        self.page4_button = QPushButton("Go to Page 4")
        self.page4_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.page4))
        left_panel.addWidget(self.page4_button)
        
        layout.addLayout(left_panel)
        
        main_content = QVBoxLayout()
        
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
        
        main_content.addLayout(filter_layout)
        
        self.agent_status_table = QTableWidget()
        main_content.addWidget(self.agent_status_table)
        
        self.refresh_button = QPushButton("Refresh Now")
        self.refresh_button.clicked.connect(self.loadData)
        main_content.addWidget(self.refresh_button)
        
        layout.addLayout(main_content)
        self.mainPage.setLayout(layout)

        # Background Animation
        self.background_label = QLabel(self.mainPage)
        self.background_label.setGeometry(0, 0, 900, 600)
        self.movie = QMovie("background.gif")  # Replace with your actual GIF path
        self.background_label.setMovie(self.movie)
        self.movie.start()
        self.background_label.lower()
    
    def setupPage(self, page):
        layout = QVBoxLayout()
        back_button = QPushButton("Back to Menu")
        back_button.clicked.connect(lambda: self.stack.setCurrentWidget(self.mainPage))
        layout.addWidget(back_button)
        page.setLayout(layout)
    
    def loadData(self):
        try:
            df = pd.read_csv("agent_status.csv")
            required_columns = {"Login ID", "Status", "Duration (min)"}
            if not required_columns.issubset(df.columns):
                raise KeyError("Missing required columns in CSV")
            
            status_filter = self.status_filter.currentText()
            search_text = self.search_box.text().lower()
            
            if status_filter != "All":
                df = df[df['Status'] == status_filter]
            
            if search_text:
                df = df[df['Agent Name'].str.lower().str.contains(search_text, na=False)]
            
            self.agent_status_table.setRowCount(df.shape[0])
            self.agent_status_table.setColumnCount(df.shape[1])
            self.agent_status_table.setHorizontalHeaderLabels(df.columns)
            
            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    self.agent_status_table.setItem(row, col, QTableWidgetItem(str(df.iat[row, col])))
        except Exception as e:
            print(f"Error loading agent status data: {e}")
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RTMApp()
    window.show()
    sys.exit(app.exec_())
