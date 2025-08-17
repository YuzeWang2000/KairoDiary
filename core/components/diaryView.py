from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont
from core.editor import DiaryEditor  # 假设你有这个模块
class DiaryView(QWidget):
    # 添加返回信号
    back_to_calendar = pyqtSignal()
    
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.current_date = QDate.currentDate()
        self.init_ui()
        
    def init_ui(self):
        # 主布局
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)
        
        
        # 顶部导航栏
        nav_layout = QHBoxLayout()
        
        # 返回日历按钮
        back_btn = QPushButton("返回日历")
        back_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 8px 20px;
                background-color: #5D3FD3;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        back_btn.clicked.connect(self.go_back_to_calendar)
        nav_layout.addWidget(back_btn)
        
        # 日期导航
        prev_btn = QPushButton("◀")
        prev_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 5px 15px;
                background-color: #D6C4F0;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #EDE7F6;
            }
        """)
        prev_btn.clicked.connect(self.prev_day)
        
        next_btn = QPushButton("▶")
        next_btn.setStyleSheet(prev_btn.styleSheet())
        next_btn.clicked.connect(self.next_day)
        
        today_btn = QPushButton("今天")
        today_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 8px 20px;
                background-color: #5D3FD3;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        today_btn.clicked.connect(self.go_to_today)
        
        # 日期标签
        self.date_label = QLabel()
        self.update_date_label()
        self.date_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        self.date_label.setStyleSheet("color: #5D3FD3;")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        nav_layout.addWidget(prev_btn)
        nav_layout.addWidget(self.date_label, 1)  # 添加伸缩因子
        nav_layout.addWidget(next_btn)
        nav_layout.addWidget(today_btn)
        
        layout.addLayout(nav_layout)
        
        # 日记编辑器
        self.editor = DiaryEditor(self.file_manager)
        layout.addWidget(self.editor, 1)  # 添加伸缩因子
        
        self.setLayout(layout)
        
        # 初始加载当前日期
        self.refresh()
        
    def update_date_label(self):
        """更新日期标签显示"""
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        weekday = weekdays[self.current_date.dayOfWeek() - 1]
        self.date_label.setText(f"{self.current_date.toString('yyyy年MM月dd日')} {weekday}")
    
    def load_date(self, date):
        """加载指定日期的日记"""
        self.current_date = date
        self.update_date_label()
        self.refresh()
    
    def refresh(self):
        """刷新日记内容"""
        self.editor.load_date(self.current_date)
    
    def prev_day(self):
        """跳转到前一天"""
        self.current_date = self.current_date.addDays(-1)
        self.update_date_label()
        self.refresh()
    
    def next_day(self):
        """跳转到后一天"""
        self.current_date = self.current_date.addDays(1)
        self.update_date_label()
        self.refresh()
    
    def go_to_today(self):
        """跳转到今天"""
        self.current_date = QDate.currentDate()
        self.update_date_label()
        self.refresh()
    
    def go_back_to_calendar(self):
        """返回到日历视图"""
        self.back_to_calendar.emit()
