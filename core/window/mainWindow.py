from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QPushButton,QMessageBox
)
from PyQt6.QtCore import QDate, pyqtSignal
from PyQt6.QtGui import QAction
from core.components import CalendarView, DiaryView, QuickNoteView, TodayTODOView
from core.window.settingsDialog import SettingsDialog
class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()
    def __init__(self, username, file_manager):
        super().__init__()
        self.username = username
        self.file_manager = file_manager
        self.current_date = QDate.currentDate()
        self.init_ui()


    def init_ui(self):

        # 创建菜单栏
        menubar = self.menuBar()
        
        # 1. 账户菜单
        account_menu = menubar.addMenu("账户(&A)")
        # 添加账户设置选项
        settings_action = QAction("账户设置", self)
        settings_action.triggered.connect(self.open_settings)
        account_menu.addAction(settings_action)
        
        # 添加分隔符
        account_menu.addSeparator()
        
        # 添加退出账户选项
        logout_action = QAction("退出当前账户", self)
        logout_action.triggered.connect(self.logout)
        account_menu.addAction(logout_action)


        self.setWindowTitle(f"KairoDiary - {self.username}")
        self.setGeometry(100, 100, 1000, 700)
        
        # 在状态栏显示用户名
        self.statusBar().showMessage(f"欢迎回来，{self.username}")

        # 主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # 顶部导航
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(10, 10, 10, 10)
        
        self.today_btn = QPushButton("今日待办")
        self.calendar_btn = QPushButton("日历")
        self.note_btn = QPushButton("快速笔记")
        
        nav_buttons = [self.calendar_btn, self.today_btn, self.note_btn]
        for btn in nav_buttons:
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    border: none;
                    padding: 10px 20px;
                    font-size: 16px;
                    border-radius: 6px;        
                }
                QPushButton:checked {
                    background-color: #5D3FD3;
                    color: white;
                }
            """)
        nav_layout.addWidget(self.today_btn)
        nav_layout.addWidget(self.calendar_btn)
        nav_layout.addWidget(self.note_btn)
        
        # 视图切换区域
        self.stacked_widget = QStackedWidget()

        # 创建日历视图
        self.calendar_view = CalendarView(self.file_manager)
        self.calendar_view.date_selected.connect(self.open_diary)

        self.diary_view = DiaryView(self.file_manager)
        # 连接返回信号
        self.diary_view.back_to_calendar.connect(self.switch_to_calendar)
        self.diary_view.editor.diary_saved.connect(self.show_diary_saved_message)
                                                        
        self.today_view = TodayTODOView(self.file_manager)
        self.today_view.diary_saved.connect(self.show_diary_saved_message)
        self.notes_view = QuickNoteView(self.file_manager)
        self.notes_view.note_created.connect(self.new_note_created)
        self.diary_view.editor.open_note_signal.connect(self.notes_view.open_note_editor)
        

        self.stacked_widget.addWidget(self.calendar_view)
        self.stacked_widget.addWidget(self.today_view)
        self.stacked_widget.addWidget(self.notes_view)  
        self.stacked_widget.addWidget(self.diary_view)

        
        # 信号连接
        self.calendar_btn.clicked.connect(lambda: self.switch_view(0))
        self.today_btn.clicked.connect(lambda: self.switch_view(1))
        self.note_btn.clicked.connect(lambda: self.switch_view(2))
        
        # 添加布局
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.stacked_widget)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 默认选中日历视图
        self.switch_view(0)
    
    def open_diary(self, date):
        """打开指定日期的日记"""
        self.diary_view.load_date(date)
        self.stacked_widget.setCurrentIndex(3)

    def switch_view(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        # 更新按钮状态
        self.calendar_btn.setChecked(index == 0)
        self.today_btn.setChecked(index == 1)
        self.note_btn.setChecked(index == 2)
        
        # 视图更新
        if index == 0:
            self.diary_view.refresh()
        elif index == 1:
            self.today_view.refresh()
        elif index == 2:
            self.notes_view.refresh()

    def switch_to_calendar(self):   
        """切换到日历视图"""
        self.stacked_widget.setCurrentIndex(0)  # 切换到日历视图

    def show_diary_saved_message(self, date):
        # 在状态栏显示用户名
        self.statusBar().showMessage(f"{date.toString('yyyy-MM-dd HH:mm:ss')} Diary saved", 3000)

    def new_note_created(self, filename):
        """处理新笔记创建事件"""
        print(f"新笔记已创建: {filename}")
        self.statusBar().showMessage(f"新笔记已创建: {filename}", 3000)
        self.diary_view.editor.load_date(QDate.currentDate())  # 确保将新笔记添加到今天
        self.diary_view.editor.add_note(filename)
    
    def open_settings(self):
        """打开设置对话框"""
        settings_dialog = SettingsDialog(self.file_manager, self)
        settings_dialog.exec()
    
    def logout(self):
        """触发退出登录流程"""
        # 确认对话框
        reply = QMessageBox.question(
            self, '确认退出',
            '确定要退出当前账户吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.logout_requested.emit()
            self.close()  # 关闭主窗口
