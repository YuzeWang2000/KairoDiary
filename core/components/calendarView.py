from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QCalendarWidget, QLabel
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QTextCharFormat

class CalendarView(QWidget):
    date_selected = pyqtSignal(QDate)  # 日期选择信号
    
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # 标题
        title = QLabel("选择日期")
        title.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: #5D3FD3; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # 日历控件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self.calendar.clicked.connect(self.on_date_selected)
        # 连接页面变化信号，当月份或年份改变时重新标记日记日期
        self.calendar.currentPageChanged.connect(self.mark_diary_dates)
        layout.addWidget(self.calendar)
        
        # 标记有日记的日期
        self.mark_diary_dates()
        
        self.setLayout(layout)
    
    def on_date_selected(self, date):
        """处理日期选择事件"""
        self.date_selected.emit(date)
    
    def mark_diary_dates(self):
        """标记有日记的日期"""
        # 清除所有日期的格式，重新开始
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # 获取当前显示的月份
        year = self.calendar.yearShown()
        month = self.calendar.monthShown()
        
        # 获取该月所有有日记的日期
        diary_dates = self.file_manager.get_diary_dates_for_month(year, month)
            # 根据系统主题选择颜色
        palette = self.calendar.palette()
        if palette.window().color().lightness() < 128:  # 深色模式
            bg_color = QColor("#5E35B1")  # 深紫色
        else:  # 浅色模式
            bg_color = QColor("#EDE7F6")  # 浅紫色
        # 创建文本格式
        format = QTextCharFormat()
        format.setBackground(bg_color)
        format.setFontWeight(QFont.Weight.Bold)
        
        # 应用格式
        for date in diary_dates:
            self.calendar.setDateTextFormat(date, format)
