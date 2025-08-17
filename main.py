import sys
import os
import json
import hashlib
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QCalendarWidget, QListWidget, QTextEdit, QLineEdit, QListWidgetItem,
    QMessageBox, QInputDialog, QFileDialog, QLabel, QMenu, QCheckBox, QSizePolicy,QComboBox, QDialog
)
from PyQt6.QtCore import Qt, QDate, QSettings, pyqtSignal, QFileSystemWatcher, QSize, QDateTime, QTime
from PyQt6.QtGui import QFont, QAction, QIcon, QTextCursor, QColor, QTextCharFormat

# ======================
# 文件管理器
# ======================
class FileManager:
    def __init__(self, base_path, username):
        self.username = username
        self.user_base_path = os.path.join(base_path, username)
        os.makedirs(self.user_base_path, exist_ok=True)
        
        # 创建用户专属目录结构
        self.user_note_dir = os.path.join(self.user_base_path, "QuickNote")
        self.user_diary_dir = os.path.join(self.user_base_path, "Diary")
        os.makedirs(self.user_note_dir, exist_ok=True)
        os.makedirs(self.user_diary_dir, exist_ok=True)
        
        self.config_path = os.path.join(self.user_base_path, "config.json")
        self.init_config()
        
    def init_config(self):
        """初始化用户的配置文件"""
        if not os.path.exists(self.config_path):
            default_config = {
                "tags": ["工作", "学习", "生活", "重要"],
                "default_view": "Diary",
                "last_access": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "theme": "system"  # 添加用户主题偏好
            }
            self.save_config(default_config)
    
    def load_config(self):
        """加载用户配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 更新上次访问时间
                config["last_access"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.save_config(config)
                return config
        except Exception as e:
            print(f"加载配置失败: {e}")
            return self.init_config() or {}
    
    def save_config(self, config):
        """保存用户配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get_diary_dir(self):
        """获取用户日记目录"""
        return self.user_diary_dir
    
    def get_diary_path(self, date=None):
        """获取指定日期的日记文件路径"""
        if date is None:
            date = QDate.currentDate()
        year = str(date.year())
        month = str(date.month()).zfill(2)
        diary_dir = os.path.join(self.user_diary_dir, year, month)
        os.makedirs(diary_dir, exist_ok=True)
        return os.path.join(diary_dir, f"{date.toString('yyyy-MM-dd')}.md")
    
    def save_diary(self, date, content):
        """保存日记内容"""
        path = self.get_diary_path(date)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"保存日记失败: {e}")
            return False
    
    def load_diary(self, date):
        """加载日记内容"""
        path = self.get_diary_path(date)
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        except Exception as e:
            print(f"加载日记失败: {e}")
            return ""

    def get_note_dir(self):
        """获取快速笔记目录"""
        return self.user_note_dir
    
    def get_note_path(self, filename):
        """获取笔记文件路径"""
        return os.path.join(self.user_note_dir, filename)
    
    def save_note(self, filename, content, title=None):
        """保存快速笔记"""
        note_path = self.get_note_path(filename)
        if not os.path.exists(note_path):
            try:
                with open(note_path, 'w', encoding='utf-8') as f:
                    # 第一次需要写入标题和创建时间
                    f.write(f"# {title}\n\n")
                    f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(content)
                return note_path
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法创建笔记: {str(e)}")
                return None
        else:
            try:
                with open(note_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return note_path
            except Exception as e:
                print(f"保存笔记失败: {e}")
                return None
    
    def load_note(self, filename):
        """加载笔记内容"""
        path = self.get_note_path(filename)
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            return "无法加载笔记内容"
        except Exception as e:
            print(f"加载笔记失败: {e}")
            return "无法加载笔记内容"
    
    def list_notes(self):
        """列出所有笔记文件"""
        notes_dir = os.path.join(self.user_base_path, "QuickNote")
        try:
            return [os.path.join(notes_dir, f) for f in os.listdir(notes_dir) 
                    if f.endswith('.md') and os.path.isfile(os.path.join(notes_dir, f))]
        except FileNotFoundError:
            # 目录不存在时创建
            os.makedirs(notes_dir, exist_ok=True)
            return []
    
    def migrate_old_data(self):
        """迁移旧版数据（如果需要）"""
        # 如果有旧版本数据迁移逻辑可在此实现
        pass

    def get_diary_dates_for_month(self, year, month):
        """获取指定月份有日记的日期列表"""
        diary_dir = os.path.join(self.user_base_path, "Diary", str(year), f"{month:02d}")
        dates = []
        
        if os.path.exists(diary_dir):
            for file in os.listdir(diary_dir):
                if file.endswith('.md'):
                    try:
                        # 从文件名提取日期
                        date_str = file.split('.')[0]
                        date = QDate.fromString(date_str, "yyyy-MM-dd")
                        if date.isValid():
                            dates.append(date)
                    except:
                        continue
        
        return dates


# ======================
# 账户管理器
# ======================
class AccountManager:
    def __init__(self, base_path):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        self.global_config_path = os.path.join(base_path, "global_config.json")
        self.init_global_config()
    
    def init_global_config(self):
        """初始化全局配置文件"""
        if not os.path.exists(self.global_config_path):
            default_config = {
                "users": {},
                "last_login": None,
                "system_settings": {}
            }
            self.save_global_config(default_config)
    
    def load_global_config(self):
        """加载全局配置"""
        try:
            with open(self.global_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            # 文件损坏或不存在时重新初始化
            return self.init_global_config() or {}
    
    def save_global_config(self, config):
        """保存全局配置"""
        try:
            with open(self.global_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存全局配置失败: {e}")
            return False
    
    def register(self, username, password):
        """注册新用户"""
        config = self.load_global_config()
        
        # 验证用户名唯一性
        if username in config.get("users", {}):
            return False, "用户名已存在"
        
        # 验证用户名有效性
        if not username or any(char in username for char in ' \\/:'):
            return False, "用户名包含非法字符"
        
        # 验证密码强度
        if len(password) < 6:
            return False, "密码长度至少需要6个字符"
        
        # 安全存储密码
        salt = os.urandom(16)
        iterations = 150000  # 适当增加迭代次数增强安全性
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
        
        # 更新配置
        config.setdefault("users", {})[username] = {
            'salt': salt.hex(),
            'key': key.hex(),
            'iterations': iterations,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'diary_count': 0,
            'note_count': 0
        }
        
        # 设置为新用户
        config["last_login"] = username
        
        # 保存配置
        if self.save_global_config(config):
            return True, "注册成功"
        return False, "注册失败，无法保存配置"
    
    def login(self, username, password):
        """用户登录"""
        config = self.load_global_config()
        
        # 验证用户是否存在
        if username not in config.get("users", {}):
            return False, "用户不存在"
        
        user_data = config["users"][username]
        
        # 获取密码相关参数
        salt = bytes.fromhex(user_data['salt'])
        stored_key = bytes.fromhex(user_data['key'])
        iterations = user_data.get('iterations', 100000)  # 兼容旧版本
        
        # 计算输入密码的哈希
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
        
        # 安全比较密码哈希
        if self.safe_compare(stored_key, new_key):
            # 更新登录时间和次数
            user_data.setdefault('login_count', 0)
            user_data['login_count'] += 1
            user_data['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            
            # 保存更新
            self.save_global_config(config)
            
            # # 检查用户数据目录是否存在
            # user_dir = os.path.join(self.base_path, "users", username)
            # os.makedirs(user_dir, exist_ok=True)
            
            return True, "登录成功"
            
        return False, "密码错误"
    
    def safe_compare(self, a, b):
        """安全比较两个字节序列 (防御时序攻击)"""
        if len(a) != len(b):
            return False
            
        result = 0
        for x, y in zip(a, b):
            result |= x ^ y
        return result == 0
    
    def list_users(self):
        """获取所有用户列表"""
        config = self.load_global_config()
        return list(config.get("users", {}).keys())
    
    def get_user_info(self, username):
        """获取用户信息"""
        config = self.load_global_config()
        user = config.get("users", {}).get(username)
        if user:
            return {
                'username': username,
                'created_at': user.get('created_at'),
                'last_login': user.get('last_login'),
                'login_count': user.get('login_count', 0),
                'diary_count': user.get('diary_count', 0),
                'note_count': user.get('note_count', 0)
            }
        return None
    
    def change_password(self, username, old_password, new_password):
        """更改用户密码"""
        success, message = self.login(username, old_password)
        if not success:
            return False, message
            
        config = self.load_global_config()
        user_data = config["users"][username]
        
        # 更新密码哈希
        salt = bytes.fromhex(user_data['salt'])
        iterations = user_data.get('iterations', 150000)
        key = hashlib.pbkdf2_hmac('sha256', new_password.encode(), salt, iterations)
        
        user_data['key'] = key.hex()
        
        if self.save_global_config(config):
            return True, "密码更改成功"
        return False, "密码更改失败，无法保存配置"
    
    def get_last_login(self):
        """获取上次登录的用户名"""
        config = self.load_global_config()
        return config.get("last_login")
    
    def set_last_login(self, username):
        """设置最后登录的用户名"""
        config = self.load_global_config()
        config["last_login"] = username
        self.save_global_config(config)
    
# ======================
# 界面组件
# ======================
class LoginWindow(QWidget):
    login_success = pyqtSignal(str)
    def __init__(self, account_manager):
        super().__init__()
        self.account_manager = account_manager
        self.init_ui()
        self.load_last_login()
        
    def init_ui(self):
        self.setWindowTitle("KairoDiary - 登录")
        self.setFixedSize(400, 400)
        
        layout = QVBoxLayout()
        
        # Logo 和标题
        title = QLabel("KairoDiary")
        title_font = QFont("Arial", 24, QFont.Weight.Bold)
        title_font.setItalic(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #5D3FD3; margin-bottom: 30px;")
        
        # 输入框
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("用户名")
        self.username_input.setStyleSheet("padding: 10px; font-size: 14px;")
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setStyleSheet("padding: 10px; font-size: 14px;")
        
        # 记住我复选框
        self.remember_check = QCheckBox("记住我")
        self.remember_check.setChecked(True)
        self.remember_check.setStyleSheet("padding: 5px;")

        # 按钮
        login_btn = QPushButton("登录")
        login_btn.setStyleSheet("""
            background-color: #5D3FD3;
            color: white;
            padding: 12px;
            font-size: 16px;
            font-weight: bold;
            border-radius: 6px;
        """)
        login_btn.clicked.connect(self.handle_login)
        
        register_btn = QPushButton("注册新账户")
        register_btn.setStyleSheet("""
            color: #5D3FD3;
            padding: 8px;
            font-size: 14px;
            border: none;
        """)
        register_btn.clicked.connect(self.show_register_dialog)
        
        layout.addWidget(title)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.remember_check)
        layout.addWidget(login_btn)
        layout.addWidget(register_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
    
    def handle_login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "输入错误", "用户名和密码不能为空")
            return
        
        print(self.account_manager.login(username, password))

        success, message = self.account_manager.login(username, password)

        if success:
            # 如果勾选了"记住我"，保存用户名
            if self.remember_check.isChecked():
                self.account_manager.set_last_login(username)
            
            # 发射信号，传递用户名和FileManager
            self.login_success.emit(username)
        else:
            QMessageBox.critical(self, "登录失败", message)
            self.password_input.clear()  # 清空密码框

    def load_last_login(self):
        """加载上次登录的用户名"""
        last_login = self.account_manager.get_last_login()
        if last_login:
            self.username_input.setText(last_login)
            self.password_input.setFocus()  # 密码框获得焦点

    def show_register_dialog(self):
        username, ok1 = QInputDialog.getText(self, "注册新用户", "用户名:")
        password, ok2 = QInputDialog.getText(self, "注册新用户", "密码:", QLineEdit.EchoMode.Password)
        
        if ok1 and ok2 and username and password:
            success, message = self.account_manager.register(username, password)
            if success:
                QMessageBox.information(self, "注册成功", "账户已创建，请登录")
                # 自动填充新注册的用户名
                self.username_input.setText(username)
                self.password_input.setFocus()
            else:
                QMessageBox.critical(self, "注册失败", message)

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
        # self.calendar.setStyleSheet("""
        #     QCalendarWidget {
        #         background-color: white;
        #         border-radius: 8px;
        #         padding: 5px;
        #     }
        #     QCalendarWidget QToolButton {
        #         font-size: 14px;
        #         font-weight: bold;
        #     }
        #     QCalendarWidget QMenu {
        #         background-color: white;
        #         border: 1px solid #E0E0E0;
        #         border-radius: 6px;
        #     }
        #     QCalendarWidget QSpinBox {
        #         min-width: 80px;
        #     }
        #     QCalendarWidget QWidget#qt_calendar_navigationbar {
        #         background-color: #EDE7F6;
        #         border-radius: 6px;
        #         padding: 5px;
        #     }
        # """)
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

class DiaryEditor(QWidget):
    diary_saved = pyqtSignal(QDateTime) 
    open_note_signal = pyqtSignal(str)  # 新增信号用于打开笔记
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.current_date = QDate.currentDate()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        todo_note_layout = QHBoxLayout()
        # TODO部分
        todo_layout = QVBoxLayout()
        todo_label = QLabel("今日待办")
        todo_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.todo_list = QListWidget()
        self.todo_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #EEEEEE;
            }
            QListWidget::item:selected {
                background-color: #EDE7F6;
            }
        """)
        self.todo_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.todo_list.customContextMenuRequested.connect(self.show_todo_context_menu)

        todo_layout.addWidget(todo_label)
        todo_layout.addWidget(self.todo_list)
        
        # 笔记部分
        note_layout = QVBoxLayout()
        note_label = QLabel("当日笔记")
        note_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        self.note_list = QListWidget()
        self.note_list.itemClicked.connect(self.open_note)
        self.note_list.setStyleSheet(self.todo_list.styleSheet())
        
        note_layout.addWidget(note_label)
        note_layout.addWidget(self.note_list)
        
        # 总结部分
        summary_layout = QVBoxLayout()
        summary_label = QLabel("每日总结")
        summary_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        self.summary_edit = QTextEdit()
        self.summary_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.summary_edit.customContextMenuRequested.connect(self.show_context_menu)
        
        save_btn = QPushButton("保存日记")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5D3FD3;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                margin-top: 10px;
            }
        """)
        save_btn.clicked.connect(self.save_diary)
        
        summary_layout.addWidget(summary_label)
        summary_layout.addWidget(self.summary_edit)
        summary_layout.addWidget(save_btn)
        
        # 整合布局
        todo_note_layout.addLayout(todo_layout, 1)
        todo_note_layout.addLayout(note_layout, 1)
        layout.addLayout(todo_note_layout, 1)  # 添加伸缩因子
        layout.addLayout(summary_layout, 1)
        
        self.setLayout(layout)

    def load_date(self, date):
        self.current_date = date
        
        # 加载日记内容
        content = self.file_manager.load_diary(date)
        # print(content)
        # 解析内容
        self.todo_list.clear()
        self.note_list.clear()
        self.summary_edit.clear()
        
        in_todo = False
        in_notes = False
        in_summary = False
        
        for line in content.splitlines():
            if line.startswith("## TODO"):
                in_todo = True
                in_notes = False
                in_summary = False
                continue
            elif line.startswith("## Notes"):
                in_todo = False
                in_notes = True
                in_summary = False
                continue
            elif line.startswith("## Summary"):
                in_todo = False
                in_notes = False
                in_summary = True
                continue
                
            if in_todo and line.strip():
                # 提取任务文本（去掉Markdown标记）
                # print(f"Processing line: {line}")
                if line.startswith('- [x]') or line.startswith('- [X]'):
                # 已完成任务
                    task_text = line[5:].strip()  # 移除 "- [x]"
                    completed = True
                elif line.startswith('- [ ]'):
                # 未完成任务
                    task_text = line[5:].strip()  # 移除 "- [ ]"
                    completed = False
                else:
                    # 处理不规范的格式
                    task_text = line.lstrip('- []').strip()
                    completed = '[x]' in line or '[X]' in line
                # 尝试从任务文本中提取标签和优先级
                tags = []
                priority = None
                
                # 查找标签部分
                if '{' in task_text and '}' in task_text:
                    # print(f"Found tags in task: {task_text}")
                    tag_start = task_text.find('{')
                    tag_end = task_text.find('}', tag_start)
                    if tag_end != -1:
                        tag_content = task_text[tag_start+1:tag_end]
                        task_text = task_text[tag_end+1:].strip()
                        
                        # 解析标签和优先级
                        parts = [p.strip() for p in tag_content.split(',')]
                        for part in parts:
                            if ':' in part:
                                key, value = map(str.strip, part.split(':', 1))
                                if key.lower() == 'priority':
                                    priority = value
                            else:
                                tags.append(part)
                
                # 创建列表项
                item = QListWidgetItem()
                
                # 创建自定义小部件来显示任务
                widget = QWidget()
                layout = QHBoxLayout(widget)
                layout.setContentsMargins(2, 2, 2, 2)
                layout.setSpacing(2)  # 设置控件间距
                
                # 状态图标
                status_label = QLabel("✓" if completed else "◌")
                status_label.setFont(QFont("Arial", 22))
                status_label.setStyleSheet(f"color: {'#757575' if completed else '#5D3FD3'}; min-width: 20px;")
                layout.addWidget(status_label)
                
                # 任务文本
                task_label = QLabel(task_text if task_text.strip() else "(无标题任务)")
                # task_label = QLabel(task_text)
                task_label.setFont(QFont("Arial", 12))
                task_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
                if completed:
                    task_label.setStyleSheet("color: #757575; text-decoration: line-through;")
                layout.addWidget(task_label, 1)  # 添加伸缩因子1
                
                # 优先级标签
                if priority:
                    priority_label = QLabel(priority)
                    priority_label.setFont(QFont("Arial", 12))
                    priority_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    # 根据优先级设置颜色
                    priority = priority.lower()
                    if priority == 'high':
                        bg_color = "#FF6B6B"
                    elif priority == 'medium':
                        bg_color = "#FFD166"
                    elif priority == 'low':
                        bg_color = "#06D6A0"
                    else:
                        bg_color = "#5D3FD3"
                    
                    priority_label.setStyleSheet(f"""
                        background-color: {bg_color};
                        color: {'white' if priority != 'medium' else 'black'};
                        border-radius: 10px;
                        min-width: 40px;
                    """)
                    layout.addWidget(priority_label)
                
                # 标签徽章
                if tags:
                    tags_widget = QWidget()
                    tags_layout = QHBoxLayout(tags_widget)
                    tags_layout.setContentsMargins(0, 0, 0, 0)
                    tags_layout.setSpacing(2)
                    
                    # 标签颜色映射
                    tag_colors = {
                        "工作": "#5D3FD3",
                        "学习": "#06D6A0",
                        "生活": "#FFD166",
                        "重要": "#FF6B6B",
                        "紧急": "#EF476F",
                        "个人": "#118AB2"
                    }
                    
                    for tag in tags:
                        tag_label = QLabel(f"#{tag}")
                        tag_label.setFont(QFont("Arial", 12))
                        tag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                        tag_label.setStyleSheet(f"""
                            background-color: {tag_colors.get(tag, '#6C757D')};
                            color: white;
                            border-radius: 10px;
                            min-width: 40px;
                        """)
                        tags_layout.addWidget(tag_label)
                    
                    layout.addWidget(tags_widget)
                
                # 设置小部件
                # widget.setLayout(layout)
                widget.adjustSize()  # 关键：确保计算正确尺寸
                min_height = max(widget.sizeHint().height(), 40)  # 最小高度40px
                item.setSizeHint(QSize(widget.sizeHint().width(), min_height))
                # item.setSizeHint(widget.sizeHint())

                # 添加到列表
                self.todo_list.addItem(item)
                self.todo_list.setItemWidget(item, widget)
                
                # 存储原始数据
                item.setData(Qt.ItemDataRole.UserRole, {
                    'text': task_text,
                    'completed': completed,
                    'priority': priority,
                    'tags': tags
                })
                
            elif in_notes and line.strip():
                # 解析笔记条目
                today = self.current_date.toString("yyyyMMdd")
                if line.startswith('- ['):
                    start = line.find('[')
                    end = line.find(']', start)
                    if end != -1:
                        time_str = line[start+1:end]
                        note_title_start = line.find('[[')
                        note_title_end = line.find(']]', note_title_start)
                        if note_title_end != -1:
                            note_title = line[note_title_start+2:note_title_end]
                            note_text = line[note_title_end+3:].strip()
                            filename = today + "_" + note_title + ".md"
                            item = QListWidgetItem(f"{time_str} - {note_title}")
                            item.setData(Qt.ItemDataRole.UserRole, filename)
                            self.note_list.addItem(item)
            elif in_summary:
                self.summary_edit.append(line)
        
        # 将光标移到开始位置
        self.summary_edit.moveCursor(QTextCursor.MoveOperation.Start)

    def show_todo_context_menu(self, pos):
        item = self.todo_list.itemAt(pos)
        if not item:
            return
            
        menu = QMenu(self)
        
        # 获取任务数据
        task_data = item.data(Qt.ItemDataRole.UserRole)
        completed = task_data['completed']
        
        # 切换完成状态
        status_action = menu.addAction("标记为已完成" if not completed else "标记为未完成")
        status_action.triggered.connect(lambda: self.toggle_task_completion(item))
        
        # 编辑任务
        edit_action = menu.addAction("编辑任务")
        edit_action.triggered.connect(lambda: self.edit_task(item))
        
        # 删除任务
        delete_action = menu.addAction("删除任务")
        delete_action.triggered.connect(lambda: self.delete_task(item))
        
        menu.exec(self.todo_list.mapToGlobal(pos))
    
    def toggle_task_completion(self, item):
        task_data = item.data(Qt.ItemDataRole.UserRole)
        task_data['completed'] = not task_data['completed']
        item.setData(Qt.ItemDataRole.UserRole, task_data)
        
        # 不要重新加载整个列表
        # 直接更新显示
        widget = self.todo_list.itemWidget(item)
        # layout, status, text, priority, tags
        
        if widget:
            # 找到状态标签并更新
            status_label = widget.children()[1]
            if status_label:
                status_label.setText("✓" if task_data['completed'] else "◌")
                status_label.setStyleSheet(f"color: {'#757575' if task_data['completed'] else '#5D3FD3'};")
            
            text_label = widget.children()[2]
            if text_label:
                if task_data['completed']:
                    text_label.setStyleSheet("color: #757575; text-decoration: line-through;")
                else:
                    text_label.setStyleSheet("text-decoration: none;")
        
        self.save_diary()
    
    def edit_task(self, item):
        """编辑任务"""
        task_data = item.data(Qt.ItemDataRole.UserRole)
        
        # 弹出编辑对话框
        new_text, ok = QInputDialog.getText(self, "编辑任务", "任务内容:", 
                                       text=task_data['text'])
        if not ok or not new_text.strip():
            return
            # 更新数据
        task_data['text'] = new_text.strip()
        item.setData(Qt.ItemDataRole.UserRole, task_data)
        
        # 直接更新显示，避免重新加载整个列表
        widget = self.todo_list.itemWidget(item)
        # layout, status, text, priority, tags

        if widget:
            # 找到任务文本标签
            text_label = widget.children()[2]
            if text_label:
                text_label.setText(new_text.strip())
        # 保存日记
        self.save_diary()
            
    def delete_task(self, item):
        row = self.todo_list.row(item)
        self.todo_list.takeItem(row)  # 这会删除项
        
        # 不需要重新加载列表
        self.save_diary()

    def open_note(self, item):
        filename = item.data(Qt.ItemDataRole.UserRole)
        print(f"打开笔记: {filename}")
        self.open_note_signal.emit(filename)
    
    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        # 逐步添加标准菜单
        standard_menu = self.summary_edit.createStandardContextMenu()
        standard_menu.setTitle("编辑操作")
        # 添加到主菜单
        menu.addMenu(standard_menu)
        menu.addSeparator()
        # 预定义的文本处理操作
        
        process_menu = menu.addMenu("文本处理")
        # process_menu.setIcon(QIcon.fromTheme("edit-select"))
        # 占位函数
        placeholder_actions = [
            ("大写转换", lambda: self.text_process_function('upper')),
            ("小写转换", lambda: self.text_process_function('lower')),
            ("标记重点", lambda: self.text_process_function('highlight')),
            ("AI摘要", lambda: self.text_process_function('summarize')),
            # ("插入日期时间", lambda: self.text_process_function('insert_datetime')),
            # ("字数统计", lambda: self.text_process_function('show_word_count')),
        ]
        
        for name, func in placeholder_actions:
            action = QAction(name, self)
            action.triggered.connect(func)
            process_menu.addAction(action)
        
        menu.exec(self.summary_edit.mapToGlobal(pos))
    
    def text_process_function(self, action_type):
        cursor = self.summary_edit.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            QMessageBox.information(self, "提示", "请先选择文本")
            return
            
        # 占位实现
        if action_type == 'upper':
            new_text = selected_text.upper()
        elif action_type == 'lower':
            new_text = selected_text.lower()
        elif action_type == 'highlight':
            new_text = f"<strong>{selected_text}</strong>"
        else:  # summarize
            new_text = f"[AI摘要] {selected_text[:50]}..."
        
        cursor.insertText(new_text)
        
        # 实际应用中替换为真正的处理逻辑
        QMessageBox.information(self, "文本处理", f"已应用: {action_type} 函数\n\n实际开发中需添加处理逻辑")

    def add_note(self, filename):
        """
        添加笔记到笔记列表
        参数:
            filename: 笔记文件名 (如 "2023-10-15_会议记录.txt")
        """
        # 从文件名中提取笔记标题 (去掉日期和扩展名)
        note_title = os.path.splitext(filename)[0]  # 去掉扩展名
        # 20250714_diary_add_note_test_2_#test_#note_#diary.md
        if '_' in note_title:
            note_title = note_title.split('_', 1)[1]  # 去掉日期部分
        
        # 获取当前时间
        current_time = QTime.currentTime().toString("HH:mm")
        
        # 创建列表项
        item = QListWidgetItem(f"{current_time} - {note_title}")
        
        # 存储完整文件名作为用户数据
        item.setData(Qt.ItemDataRole.UserRole, filename)
        # 添加到笔记列表
        self.note_list.addItem(item)
        
        # 自动滚动到新添加的笔记
        self.note_list.scrollToItem(item)
        
        # 保存日记更新
        self.save_diary()

    def save_diary(self):
        # 构建Markdown内容
        content = "## TODO\n"
        for i in range(self.todo_list.count()):
            item = self.todo_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            # 根据完成状态添加不同标记
            mark = "[x]" if data['completed'] else "[ ]"
            
            # 重建标签/优先级部分
            tag_parts = []
            if data.get('priority'):
                tag_parts.append(f"priority:{data['priority']}")
            if data.get('tags'):
                tag_parts.extend(data['tags'])
            
            # 构建行
            line = f"- {mark} "
            if tag_parts:
                line += "{" + f" {', '.join(tag_parts)}" + "}"
            line += data['text']
            content += line + "\n"
        
        content += "\n## Notes\n"
        for i in range(self.note_list.count()):
            item = self.note_list.item(i)
            note_title = item.text().split(' - ', 1)[1]
            time_part = item.text().split(' - ', 1)[0]
            content += f"- [{time_part}] [[{note_title}]]\n"
        
        content += "\n## Summary\n"
        content += self.summary_edit.toPlainText()
        
        # 保存文件
        self.file_manager.save_diary(self.current_date, content)
        self.diary_saved.emit(QDateTime.currentDateTime())
        # QMessageBox.information(self, "保存成功", "日记已保存")

class TodayTODOView(QWidget):
    diary_saved = pyqtSignal(QDateTime) 
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.today = QDate.currentDate()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        todo_label = QLabel("今日待办事项")
        todo_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        todo_label.setStyleSheet("color: #5D3FD3; padding: 10px;")
        todo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.todo_list = QListWidget()
        self.todo_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #EEEEEE;
            }
            QListWidget::item:selected {
                background-color: #EDE7F6;
            }
        """)
        self.todo_list.itemDoubleClicked.connect(self.toggle_task_completion)
        self.todo_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.todo_list.customContextMenuRequested.connect(self.show_todo_context_menu)
        # 添加新任务区域
        add_task_layout = QHBoxLayout()
        self.new_task_input = QLineEdit()
        self.new_task_input.setPlaceholderText("添加新任务...")
        self.new_task_input.setStyleSheet("padding: 10px; font-size: 16px; border-radius: 6px;")
        
        # 回车键添加任务
        self.new_task_input.returnPressed.connect(self.add_task)

        add_btn = QPushButton("添加")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #5D3FD3;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 80px;
            }
        """)
        add_btn.clicked.connect(self.add_task)
        
        add_task_layout.addWidget(self.new_task_input)
        add_task_layout.addWidget(add_btn)
        
        layout.addWidget(todo_label)
        layout.addWidget(self.todo_list)
        layout.addLayout(add_task_layout)
        
        self.setLayout(layout)
        self.load_today()
    
    def refresh(self):
        """刷新今日待办列表"""
        self.todo_list.clear()
        self.load_today()

    def add_task_to_list(self, task_text, completed=False, priority=None, tags=None):
        # 创建列表项
        item = QListWidgetItem()
        # 创建自定义小部件来显示任务
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)  # 设置控件间距
        
        # 状态图标
        status_label = QLabel("✓" if completed else "◌")
        status_label.setFont(QFont("Arial", 26))
        status_label.setStyleSheet(f"color: {'#757575' if completed else '#5D3FD3'}; min-width: 20px;")
        layout.addWidget(status_label)
        
        # 任务文本
        task_label = QLabel(task_text if task_text.strip() else "(无标题任务)")
        # task_label = QLabel(task_text)
        task_label.setFont(QFont("Arial", 18))
        task_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        if completed:
            task_label.setStyleSheet("color: #757575; text-decoration: line-through;")
        layout.addWidget(task_label, 1)  # 添加伸缩因子1
        
        # 优先级标签
        if priority:
            priority_label = QLabel(priority)
            priority_label.setFont(QFont("Arial", 18,))
            priority_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 根据优先级设置颜色
            priority = priority.lower()
            if priority == 'high':
                bg_color = "#FF6B6B"
            elif priority == 'medium':
                bg_color = "#FFD166"
            elif priority == 'low':
                bg_color = "#06D6A0"
            else:
                bg_color = "#5D3FD3"
            
            priority_label.setStyleSheet(f"""
                background-color: {bg_color};
                color: {'white' if priority != 'medium' else 'black'};
                border-radius: 10px;
                min-width: 50px;
            """)
            layout.addWidget(priority_label)
        
        # 标签徽章
        if tags:
            tags_widget = QWidget()
            tags_layout = QHBoxLayout(tags_widget)
            tags_layout.setContentsMargins(0, 0, 0, 0)
            tags_layout.setSpacing(2)
            
            # 标签颜色映射
            tag_colors = {
                "工作": "#5D3FD3",
                "学习": "#06D6A0",
                "生活": "#FFD166",
                "重要": "#FF6B6B",
                "紧急": "#EF476F",
                "个人": "#118AB2"
            }
            
            for tag in tags:
                tag_label = QLabel(f"#{tag}")
                tag_label.setFont(QFont("Arial", 18))
                tag_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                tag_label.setStyleSheet(f"""
                    background-color: {tag_colors.get(tag, '#6C757D')};
                    color: white;
                    border-radius: 10px;
                    min-width: 50px;
                """)
                tags_layout.addWidget(tag_label)
            
            layout.addWidget(tags_widget)
        
        # 设置小部件
        # widget.setLayout(layout)
        widget.adjustSize()  # 关键：确保计算正确尺寸
        min_height = max(widget.sizeHint().height(), 50)  # 最小高度40px
        item.setSizeHint(QSize(widget.sizeHint().width(), min_height))
        # 添加到列表
        self.todo_list.addItem(item)
        self.todo_list.setItemWidget(item, widget)
        
        # 存储原始数据
        item.setData(Qt.ItemDataRole.UserRole, {
            'text': task_text,
            'completed': completed,
            'priority': priority,
            'tags': tags
        })

    def get_tags_and_priority(self, task_text):
        """从任务文本中提取标签和优先级"""
        tags = []
        priority = None
        
        # 查找标签部分
        if '{' in task_text and '}' in task_text:
            # print(f"Found tags in task: {task_text}")
            tag_start = task_text.find('{')
            tag_end = task_text.find('}', tag_start)
            if tag_end != -1:
                tag_content = task_text[tag_start+1:tag_end]
                task_text = task_text[tag_end+1:].strip()
                
                # 解析标签和优先级
                parts = [p.strip() for p in tag_content.split(',')]
                for part in parts:
                    if ':' in part:
                        key, value = map(str.strip, part.split(':', 1))
                        if key.lower() == 'priority':
                            priority = value
                    else:
                        tags.append(part)
        return task_text, tags, priority
    
    def load_today(self):
        today = QDate.currentDate()
        self.today = today
        self.todo_list.clear() 
        # 加载今天的日记
        diary_content = self.file_manager.load_diary(today)
        
        # 提取TODO部分
        in_todo = False
        for line in diary_content.splitlines():
            if line.startswith("## TODO"):
                in_todo = True
                continue
            elif line.startswith("## ") and in_todo:
                break
            
            if in_todo and line.strip() and line.startswith('- '):
                # 改进的任务解析逻辑
                if line.startswith('- [x]') or line.startswith('- [X]'):
                    # 已完成任务
                    task_text = line[5:].strip()  # 移除 "- [x]"
                    completed = True
                elif line.startswith('- [ ]'):
                    # 未完成任务
                    task_text = line[5:].strip()  # 移除 "- [ ]"
                    completed = False
                else:
                    # 处理不规范的格式
                    task_text = line.lstrip('- []').strip()
                    # 检查是否包含完成标记
                    completed = '[x]' in line or '[X]' in line
                task_text, tags, priority = self.get_tags_and_priority(task_text)
                self.add_task_to_list(task_text, completed, priority, tags)
                
    def add_task(self):
        task_text = self.new_task_input.text().strip()
        if not task_text:
            return
        # 清空输入框
        self.new_task_input.clear()
        task_text, tags, priority = self.get_tags_and_priority(task_text)
        self.add_task_to_list(task_text, completed=False, priority=priority, tags=tags)
        # 更新日记文件
        self.update_diary_tasks()

    def show_todo_context_menu(self, pos):
        item = self.todo_list.itemAt(pos)
        if not item:
            return
            
        menu = QMenu(self)
        
        # 获取任务数据
        task_data = item.data(Qt.ItemDataRole.UserRole)
        completed = task_data['completed']
        
        # 切换完成状态
        status_action = menu.addAction("标记为已完成" if not completed else "标记为未完成")
        status_action.triggered.connect(lambda: self.toggle_task_completion(item))
        
        # 编辑任务
        edit_action = menu.addAction("编辑任务")
        edit_action.triggered.connect(lambda: self.edit_task(item))
        
        # 删除任务
        delete_action = menu.addAction("删除任务")
        delete_action.triggered.connect(lambda: self.delete_task(item))
        
        menu.exec(self.todo_list.mapToGlobal(pos))

    def toggle_task_completion(self, item):
        """切换任务完成状态"""
        # 获取当前任务数据
        task_data = item.data(Qt.ItemDataRole.UserRole)
        task_data['completed'] = not task_data['completed']
        item.setData(Qt.ItemDataRole.UserRole, task_data)
        
        # 直接更新显示
        widget = self.todo_list.itemWidget(item)
        # layout, status, text, priority, tags
        
        if widget:
            # 找到状态标签并更新
            status_label = widget.children()[1]
            if status_label:
                status_label.setText("✓" if task_data['completed'] else "◌")
                status_label.setStyleSheet(f"color: {'#757575' if task_data['completed'] else '#5D3FD3'};")
            
            text_label = widget.children()[2]
            if text_label:
                if task_data['completed']:
                    text_label.setStyleSheet("color: #757575; text-decoration: line-through;")
                else:
                    text_label.setStyleSheet("text-decoration: none;")

        # 更新日记文件
        self.update_diary_tasks()

    def edit_task(self, item):
        """编辑任务"""
        task_data = item.data(Qt.ItemDataRole.UserRole)
        
        # 弹出编辑对话框
        new_text, ok = QInputDialog.getText(self, "编辑任务", "任务内容:", 
                                       text=task_data['text'])
        if not ok or not new_text.strip():
            return
            # 更新数据
        task_data['text'] = new_text.strip()
        item.setData(Qt.ItemDataRole.UserRole, task_data)
        
        # 直接更新显示，避免重新加载整个列表
        widget = self.todo_list.itemWidget(item)
        # layout, status, text, priority, tags

        if widget:
            # 找到任务文本标签
            text_label = widget.children()[2]
            if text_label:
                text_label.setText(new_text.strip())
        # 保存日记
        self.update_diary_tasks()
            
    def delete_task(self, item):
        row = self.todo_list.row(item)
        self.todo_list.takeItem(row)  # 这会删除项
        
        # 不需要重新加载列表
        self.update_diary_tasks()

    def update_diary_tasks(self):
        diary_content = self.file_manager.load_diary(self.today)
        if self.today != QDate.currentDate():
            QMessageBox(text="警告: 更新的日期不是今天，可能导致数据不一致！")
        # 重建TODO部分
        new_todo = "## TODO\n"
        for i in range(self.todo_list.count()):
            item = self.todo_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            # 根据完成状态添加不同标记
            mark = "[x]" if data['completed'] else "[ ]"
            
            # 重建标签/优先级部分
            tag_parts = []
            if data.get('priority'):
                tag_parts.append(f"priority:{data['priority']}")
            if data.get('tags'):
                tag_parts.extend(data['tags'])
            
            # 构建行
            line = f"- {mark} "
            if tag_parts:
                line += "{" + f" {', '.join(tag_parts)}" + "}"
            line += data['text']
            new_todo += line + "\n"
        # 更新日记内容
        if "## TODO" in diary_content:
            # 替换现有的TODO部分
            start_index = diary_content.index("## TODO")
            end_index = diary_content.find("## ", start_index + 1)
            if end_index == -1:
                diary_content = diary_content[:start_index] + new_todo
            else:
                diary_content = diary_content[:start_index] + new_todo + diary_content[end_index:]
        else:
            # 如果不存在TODO部分，添加到开头
            diary_content = new_todo + "\n" + diary_content
        
        # 保存更新
        self.file_manager.save_diary(self.today, diary_content)
        self.diary_saved.emit(QDateTime.currentDateTime())

class QuickNoteView(QWidget):
    note_saved = pyqtSignal(QDateTime)
    note_created = pyqtSignal(str)
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.filter_tag = None
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)
        
        # 标题和操作栏
        title_layout = QHBoxLayout()
        
        title = QLabel("快速笔记")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #5D3FD3; margin-bottom: 5px;")
        
        # 搜索框
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索笔记...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                font-size: 14px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                background-color: #FFFFFF;
            }
        """)
        self.search_input.textChanged.connect(self.refresh)
        
        title_layout.addWidget(title)
        title_layout.addStretch(1)
        title_layout.addWidget(self.search_input, 1)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        # 新建笔记按钮
        new_note_btn = QPushButton("新建笔记")
        new_note_btn.setIcon(QIcon.fromTheme("document-new"))
        new_note_btn.setStyleSheet("""
            QPushButton {
                background-color: #5D3FD3;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #4A2FB8;
            }
        """)
        new_note_btn.clicked.connect(self.create_new_note)
        
        # 标签过滤按钮
        self.tag_filter_combo = QComboBox()
        self.tag_filter_combo.addItem("所有标签", None)
        self.tag_filter_combo.setPlaceholderText("按标签过滤")
        self.tag_filter_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                font-size: 14px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
            }
        """)
        self.tag_filter_combo.currentIndexChanged.connect(self.filter_by_tag)
        
        # 排序方式
        self.sort_combo = QComboBox()
        self.sort_combo.addItem("最近修改", "modified")
        self.sort_combo.addItem("标题 A-Z", "title_asc")
        self.sort_combo.addItem("标题 Z-A", "title_desc")
        self.sort_combo.setStyleSheet("""
            QComboBox {
                padding: 6px;
                font-size: 14px;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
            }
        """)
        self.sort_combo.currentIndexChanged.connect(self.refresh)
        
        btn_layout.addWidget(new_note_btn)
        btn_layout.addWidget(QLabel("标签过滤:"))
        btn_layout.addWidget(self.tag_filter_combo, 1)
        btn_layout.addWidget(QLabel("排序方式:"))
        btn_layout.addWidget(self.sort_combo, 1)
        
        # 笔记列表容器
        self.notes_list = QListWidget()
        self.notes_list.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 0px;
                border-bottom: 1px solid #EEEEEE;
            }
            QListWidget::item:selected {
                background-color: #EDE7F6;
            }
        """)
        self.notes_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.notes_list.itemClicked.connect(self.open_note)
        self.notes_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.notes_list.customContextMenuRequested.connect(self.show_note_context_menu)
        
        # 加载笔记
        self.refresh()
        
        main_layout.addLayout(title_layout)
        main_layout.addLayout(btn_layout)
        main_layout.addWidget(self.notes_list, 1)
        
        self.setLayout(main_layout)
    
    def refresh(self):
        """刷新笔记列表"""
        # 保存滚动位置
        scrollbar = self.notes_list.verticalScrollBar()
        scroll_pos = scrollbar.value() if scrollbar else 0
        
        self.notes_list.clear()
        
        # 获取笔记数据
        notes = self.file_manager.list_notes()
        
        # 应用过滤和排序
        search_text = self.search_input.text().lower()
        current_tag = self.tag_filter_combo.currentData()
        
        # 根据排序选项排序
        sort_mode = self.sort_combo.currentData()
        if sort_mode == "modified":
            # 按修改时间排序（从新到旧）
            notes.sort(key=lambda f: os.path.getmtime(f), reverse=True)
        else:
            # 按标题排序
            notes.sort(key=lambda f: os.path.basename(f).split('_', 1)[-1].lower())
            if sort_mode == "title_desc":
                notes.reverse()
        
        # 获取所有标签用于过滤下拉框
        all_tags = set()
        
        for note_path in notes:
            # 从文件名提取元数据
            filename = os.path.basename(note_path)
            
            # 尝试解析文件名格式
            note_date = ""
            note_title = ""
            tags = []
            
            if '_' in filename and len(filename.split('_')[0]) == 8:
                # 标准格式：20230714_Title_Tag1_Tag2.md
                parts = filename[:-3].split('_')  # 去掉扩展名
                date_part = parts[0]
                note_date = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                note_title = ' '.join(p for p in parts[1:] if not p.startswith('#'))
                tags = [p[1:] for p in parts if p.startswith('#')]
            else:
                # 非标准格式笔记
                note_title = filename[:-3].replace('_', ' ')
            
            # 添加到标签集合
            all_tags.update(tags)
            
            # 应用搜索过滤
            if search_text and not (search_text in note_title.lower() or any(search_text in tag.lower() for tag in tags)):
                continue
            
            # 应用标签过滤
            if current_tag and current_tag not in tags:
                continue
            
            # 创建自定义列表项
            item = QListWidgetItem()
            
            # 创建自定义小部件
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setContentsMargins(12, 10, 12, 10)
            layout.setSpacing(5)
            
            # 标题行
            title_layout = QHBoxLayout()
            title_layout.setContentsMargins(0, 0, 0, 0)
            
            title_label = QLabel(note_title if note_title else "未命名笔记")
            title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
            title_label.setStyleSheet("color: #212121;")
            title_layout.addWidget(title_label)
            
            title_layout.addStretch()
            
            # 日期
            date_label = QLabel(note_date)
            date_label.setFont(QFont("Arial", 10))
            date_label.setStyleSheet("color: #757575;")
            title_layout.addWidget(date_label)
            
            layout.addLayout(title_layout)
            
            # 标签行
            if tags:
                tags_layout = QHBoxLayout()
                tags_layout.setContentsMargins(0, 0, 0, 0)
                tags_layout.setSpacing(5)
                
                for tag in tags:
                    tag_label = QLabel(f"#{tag}")
                    tag_label.setFont(QFont("Arial", 9))
                    tag_label.setStyleSheet("""
                        background-color: #E0E0E0;
                        color: #424242;
                        border-radius: 10px;
                        padding: 2px 8px;
                    """)
                    tags_layout.addWidget(tag_label)
                
                tags_layout.addStretch()
                layout.addLayout(tags_layout)
            
            # 预览文本（如果文件支持）
            preview_text = ""
            if note_path.endswith('.md'):
                # 仅加载前几行作为预览
                try:
                    with open(note_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[:3]
                        # 组合文本（去掉标题和空行）
                        preview_text = ''.join([line for line in lines if not line.startswith('#')]).strip()
                        if len(preview_text) > 100:
                            preview_text = preview_text[:100] + "..."
                except:
                    preview_text = "[无法加载预览]"
            
            if preview_text:
                preview_label = QLabel(preview_text)
                preview_label.setFont(QFont("Arial", 10))
                preview_label.setStyleSheet("color: #616161;")
                preview_label.setWordWrap(True)
                layout.addWidget(preview_label)
            
            # 设置小部件
            widget.adjustSize()
            item.setSizeHint(widget.sizeHint())
            
            # 添加到列表
            self.notes_list.addItem(item)
            self.notes_list.setItemWidget(item, widget)
            item.setData(Qt.ItemDataRole.UserRole, note_path)
        
        # 恢复滚动位置
        if scrollbar:
            scrollbar.setValue(scroll_pos)
        
        # 更新标签过滤下拉框
        self.update_tag_filter(all_tags)
    
    def update_tag_filter(self, tags):
        """更新标签过滤下拉框"""
        # 暂时断开信号连接
        self.tag_filter_combo.blockSignals(True)
        # 保存当前选择
        current_tag = self.tag_filter_combo.currentData()
        
        self.tag_filter_combo.clear()
        self.tag_filter_combo.addItem("所有标签", None)
        
        # 添加标签选项
        for tag in sorted(tags):
            self.tag_filter_combo.addItem(f"#{tag}", tag)
        
        # 恢复之前的选择
        if current_tag:
            index = self.tag_filter_combo.findData(current_tag)
            if index >= 0:
                self.tag_filter_combo.setCurrentIndex(index)
        # 恢复信号连接
        self.tag_filter_combo.blockSignals(False)
    
    def filter_by_tag(self):
        """按标签过滤笔记"""
        # print(f"Filtering by tag: {self.tag_filter_combo.currentData()}")
        self.refresh()
    
    def create_new_note(self):
        """创建新笔记"""
        dialog = QDialog(self)
        dialog.setWindowTitle("新建笔记")
        dialog.setFixedSize(400, 250)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        title_label = QLabel("笔记标题:")
        title_label.setStyleSheet("font-weight: bold;")
        self.new_note_title = QLineEdit()
        self.new_note_title.setPlaceholderText("输入笔记标题")
        
        tags_label = QLabel("标签 (可选, 用逗号分隔):")
        tags_label.setStyleSheet("font-weight: bold;")
        self.new_note_tags = QLineEdit()
        self.new_note_tags.setPlaceholderText("例如: 工作,项目")
        
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("创建")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #5D3FD3;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #4A2FB8;
            }
        """)
        create_btn.clicked.connect(lambda: self.do_create_note(dialog))
        
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #EEEEEE;
                color: #424242;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 6px;
            }
        """)
        cancel_btn.clicked.connect(dialog.reject)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(create_btn)
        
        layout.addWidget(title_label)
        layout.addWidget(self.new_note_title)
        layout.addWidget(tags_label)
        layout.addWidget(self.new_note_tags)
        layout.addStretch(1)
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def do_create_note(self, dialog):
        """执行笔记创建"""
        title = self.new_note_title.text().strip()
        if not title:
            QMessageBox.warning(self, "输入错误", "笔记标题不能为空")
            return
            
        # 格式化标题
        clean_title = title.replace(' ', '_').replace('#', '')
        
        # 处理标签
        tags_input = self.new_note_tags.text().strip()
        tags = []
        if tags_input:
            # 分割标签并清理
            tags = ['#' + tag.strip().replace(' ', '_') for tag in tags_input.split(',') if tag.strip()]
        
        # 创建文件名（日期_标题_标签.md）
        today = QDate.currentDate().toString("yyyyMMdd")
        filename = today + '_' + clean_title
        if tags:
            filename += '_' + '_'.join(tags)
        filename += '.md'
        
        # 创建笔记文件
        try:
            note_path = self.file_manager.save_note(filename, "", title)
            if note_path is not None:
                print(f"新笔记已创建: {note_path}")
                self.note_created.emit(filename)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法创建笔记: {str(e)}")
            return
        dialog.accept()
        self.refresh()
        
        # 自动打开新笔记
        self.open_note_editor(filename)
    
    def open_note(self, item):
        """打开选中的笔记"""
        note_path = item.data(Qt.ItemDataRole.UserRole)
        filename = os.path.basename(note_path)
        # note_title = os.path.basename(note_path)[9:-3].replace('_', ' ') if '_' in note_path else os.path.basename(note_path)[:-3]
        self.open_note_editor(filename)
    
    def open_note_editor(self, filename):
        """打开笔记编辑器"""
        print(f"打开笔记编辑器: {filename}")
        editor_dialog = QDialog(self)
        editor_dialog.setWindowTitle(f"编辑笔记: {filename}")
        editor_dialog.resize(600, 400)
        
        layout = QVBoxLayout(editor_dialog)
        editor = QTextEdit()


        content = self.file_manager.load_note(filename)  # 确保文件存在
        editor.setPlainText(content)

        layout.addWidget(editor)
        
        # 保存按钮
        save_btn = QPushButton("保存")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #5D3FD3;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 6px;
            }
        """)
        save_btn.clicked.connect(editor_dialog.accept)
        
        layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        if editor_dialog.exec() == QDialog.DialogCode.Accepted:
            # 保存笔记
            return_path = self.file_manager.save_note(filename, editor.toPlainText())
            if return_path is None:
                QMessageBox.warning(self, "保存失败", "无法保存笔记内容")
    
    def show_note_context_menu(self, pos):
        """显示笔记上下文菜单"""
        item = self.notes_list.itemAt(pos)
        if not item:
            return
            
        menu = QMenu(self)
        
        # 获取笔记数据
        note_path = item.data(Qt.ItemDataRole.UserRole)
        
        # 打开笔记
        open_action = menu.addAction("打开笔记")
        open_action.triggered.connect(lambda: self.open_note(item))
        
        # 重命名笔记
        rename_action = menu.addAction("重命名笔记")
        rename_action.triggered.connect(lambda: self.rename_note(item))
        
        # 删除笔记
        delete_action = menu.addAction("删除笔记")
        delete_action.triggered.connect(lambda: self.delete_note(item))
        
        menu.addSeparator()
        
        # 添加标签
        tag_action = menu.addAction("管理标签")
        tag_action.triggered.connect(lambda: self.manage_tags(item))
        
        menu.exec(self.notes_list.mapToGlobal(pos))
    
    def rename_note(self, item):
        """重命名笔记"""
        note_path = item.data(Qt.ItemDataRole.UserRole)
        filename = os.path.basename(note_path)
        
        # 提取原始标题（不含扩展名）
        old_title = filename[:-3]
        
        # 弹出重命名对话框
        new_title, ok = QInputDialog.getText(
            self, 
            "重命名笔记", 
            "请输入新标题:", 
            text=old_title
        )
        
        if ok and new_title.strip() and new_title != old_title:
            new_filename = new_title.strip() + '.md'
            new_path = os.path.join(os.path.dirname(note_path), new_filename)
            
            try:
                os.rename(note_path, new_path)
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, "重命名失败", f"无法重命名笔记: {str(e)}")
    
    def delete_note(self, item):
        """删除笔记"""
        note_path = item.data(Qt.ItemDataRole.UserRole)
        
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除笔记 '{os.path.basename(note_path)}' 吗?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(note_path)
                self.refresh()
            except:
                QMessageBox.warning(self, "删除失败", "无法删除笔记")
    
    def manage_tags(self, item):
        """管理笔记标签"""
        note_path = item.data(Qt.ItemDataRole.UserRole)
        filename = os.path.basename(note_path)
        
        # 获取当前标签
        current_tags = []
        parts = filename[:-3].split('_')
        if len(parts) > 1:
            # 从文件名中提取标签（以#开头）
            current_tags = [p[1:] for p in parts if p.startswith('#')]
        
        dialog = QDialog(self)
        dialog.setWindowTitle("管理笔记标签")
        dialog.setFixedSize(300, 300)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # 标签标题
        title = QLabel(f"标签: {filename.split('_', 1)[-1].replace('#', '')}")
        title.setWordWrap(True)
        title.setStyleSheet("font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # 添加新标签区域
        add_tag_layout = QHBoxLayout()
        self.new_tag_input = QLineEdit()
        self.new_tag_input.setPlaceholderText("输入新标签...")
        add_tag_btn = QPushButton("添加")
        add_tag_btn.clicked.connect(lambda: self.add_note_tag(dialog, note_path, item))
        
        add_tag_layout.addWidget(self.new_tag_input)
        add_tag_layout.addWidget(add_tag_btn)
        layout.addLayout(add_tag_layout)
        
        # 标签列表
        tags_list_label = QLabel("已有标签:")
        tags_list_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(tags_list_label)
        
        self.tags_list = QListWidget()
        self.tags_list.addItems(current_tags)
        self.tags_list.setStyleSheet("""
            QListWidget::item {
                padding: 4px 8px;
                margin: 2px;
            }
        """)
        layout.addWidget(self.tags_list)
        
        # 移除按钮
        remove_btn = QPushButton("移除选中标签")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8d7da;
                color: #721c24;
                padding: 6px 12px;
                margin-top: 10px;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_selected_tag(item))
        
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(remove_btn)
        btn_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        btn_layout.addWidget(close_btn)
        
        layout.addLayout(btn_layout)
        dialog.exec()
    
    def add_note_tag(self, dialog, note_path, item):
        """添加新标签到笔记"""
        new_tag = self.new_tag_input.text().strip()
        if not new_tag:
            return
            
        # 更新文件名（添加新标签）
        old_filename = os.path.basename(note_path)
        new_filename = old_filename[:-3] + '_#' + new_tag.replace(' ', '_') + '.md'
        new_path = os.path.join(os.path.dirname(note_path), new_filename)
        
        try:
            os.rename(note_path, new_path)
            self.refresh()
            item.setSelected(True)  # 重新选中同一项目
            self.new_tag_input.clear()
        except:
            QMessageBox.warning(self, "操作失败", "无法添加标签")
    
    def remove_selected_tag(self, item):
        """移除选中的标签"""
        selected_item = self.tags_list.currentItem()
        if not selected_item:
            return
            
        tag_to_remove = selected_item.text()
        note_path = item.data(Qt.ItemDataRole.UserRole)
        
        # 构建新文件名（移除该标签）
        old_filename = os.path.basename(note_path)
        
        # 将文件名分解为部分
        parts = old_filename[:-3].split('_')
        
        # 创建一个不包含要移除标签的新列表
        new_parts = [part for part in parts if not (part.startswith('#') and part[1:] == tag_to_remove)]
        
        # 避免文件名以"_"结尾
        new_filename = '_'.join(new_parts) + '.md'
        new_path = os.path.join(os.path.dirname(note_path), new_filename)
        
        try:
            os.rename(note_path, new_path)
            self.refresh()
            item.setSelected(True)  # 重新选中同一项目
        except:
            QMessageBox.warning(self, "操作失败", "无法移除标签")
# ======================
# 应用入口
# ======================
def main():
    # 设置应用配置
    QApplication.setApplicationName("KairoDiary")
    QApplication.setOrganizationName("KairoSoft")
    
    app = QApplication(sys.argv)

    # 设置应用程序图标（会显示在任务栏等位置）
    app.setApplicationDisplayName("Kairo Diary")
    # 获取当前用户的文档目录
    documents_path = os.path.join(os.path.expanduser("~"), "MyDocuments")
    base_path = os.path.join(documents_path, "KairoDiaryData")
    
    login_win = None


    def app_loggin():
        """处理登出请求"""
        
        account_manager = AccountManager(base_path)
        nonlocal login_win
        if login_win is not None:
            print("用户请求登出")
        else:
            print("用户未登录，显示登录窗口")
        
        login_win = LoginWindow(account_manager)
        login_win.login_success.connect(on_login_success)
        login_win.show()

    def on_login_success(username):
            login_win.close()
            file_manager = FileManager(base_path, username)
            main_win = MainWindow(username, file_manager)
            main_win.logout_requested.connect(app_loggin)
            main_win.showFullScreen()

    app_loggin()
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()