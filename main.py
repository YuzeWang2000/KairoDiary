import sys
import os
import json
import hashlib
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QStackedWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QCalendarWidget, QListWidget, QTextEdit, QLineEdit, QListWidgetItem,
    QMessageBox, QInputDialog, QFileDialog, QLabel, QMenu
)
from PyQt6.QtCore import Qt, QDate, QSettings, pyqtSignal
from PyQt6.QtGui import QFont, QAction, QIcon, QTextCursor, QColor
from PyQt6.QtCore import QFileSystemWatcher

# ======================
# 文件管理器
# ======================
class FileManager:
    def __init__(self, base_path):
        self.base_path = base_path
        os.makedirs(os.path.join(base_path, "Diary"), exist_ok=True)
        os.makedirs(os.path.join(base_path, "QuickNote"), exist_ok=True)
        
        self.config_path = os.path.join(base_path, "config.json")
        self.init_config()
        
    def init_config(self):
        if not os.path.exists(self.config_path):
            default_config = {
                "tags": ["工作", "学习", "生活", "重要"],
                "default_view": "Diary",
                "last_login": None
            }
            self.save_config(default_config)
    
    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def save_config(self, config):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    
    def get_diary_path(self, date=None):
        if date is None:
            date = QDate.currentDate()
        year = str(date.year())
        month = str(date.month()).zfill(2)
        diary_dir = os.path.join(self.base_path, "Diary", year, month)
        os.makedirs(diary_dir, exist_ok=True)
        return os.path.join(diary_dir, f"{date.toString('yyyy-MM-dd')}.md")
    
    def get_note_path(self, title, date=None):
        if date is None:
            date = datetime.now()
        filename = f"{date.strftime('%Y%m%d')}_{title.replace(' ', '_')}.md"
        return os.path.join(self.base_path, "QuickNote", filename)
    
    def save_diary(self, date, content):
        path = self.get_diary_path(date)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def load_diary(self, date):
        path = self.get_diary_path(date)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def save_note(self, title, content):
        path = self.get_note_path(title)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write(content)
        return path
    
    def load_note(self, path):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    def list_notes(self):
        notes_dir = os.path.join(self.base_path, "QuickNote")
        return [os.path.join(notes_dir, f) for f in os.listdir(notes_dir) 
                if f.endswith('.md')]

# ======================
# 账户管理器
# ======================
class AccountManager:
    def __init__(self, file_manager):
        self.file_manager = file_manager
        self.config = self.file_manager.load_config()
        self.users = self.config.get("users", {})
        
    def register(self, username, password):
        if username in self.users:
            return False, "用户名已存在"
        
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        self.users[username] = {
            'salt': salt.hex(),
            'key': key.hex()
        }
        self.config["users"] = self.users
        self.file_manager.save_config(self.config)
        return True, "注册成功"
    
    def login(self, username, password):
        if username not in self.users:
            return False, "用户不存在"
        
        user = self.users[username]
        salt = bytes.fromhex(user['salt'])
        key = bytes.fromhex(user['key'])
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        
        if key == new_key:
            self.config["last_login"] = username
            self.file_manager.save_config(self.config)
            return True, "登录成功"
        return False, "密码错误"

# ======================
# 界面组件
# ======================
class LoginWindow(QWidget):
    login_success = pyqtSignal()
    
    def __init__(self, account_manager):
        super().__init__()
        self.account_manager = account_manager
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("KairoDiary - 登录")
        self.setFixedSize(400, 300)
        
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
        layout.addWidget(login_btn)
        layout.addWidget(register_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(layout)
    
    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        
        if not username or not password:
            QMessageBox.warning(self, "输入错误", "用户名和密码不能为空")
            return
            
        success, message = self.account_manager.login(username, password)
        if success:
            self.login_success.emit()
        else:
            QMessageBox.critical(self, "登录失败", message)
    
    def show_register_dialog(self):
        username, ok1 = QInputDialog.getText(self, "注册新用户", "用户名:")
        password, ok2 = QInputDialog.getText(self, "注册新用户", "密码:", QLineEdit.EchoMode.Password)
        
        if ok1 and ok2 and username and password:
            success, message = self.account_manager.register(username, password)
            if success:
                QMessageBox.information(self, "注册成功", "账户已创建，请登录")
            else:
                QMessageBox.critical(self, "注册失败", message)

class MainWindow(QMainWindow):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.current_date = QDate.currentDate()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("KairoDiary")
        self.setGeometry(100, 100, 1000, 700)
        
        # 主布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # 顶部导航
        nav_layout = QHBoxLayout()
        nav_layout.setContentsMargins(10, 10, 10, 10)
        
        self.diary_btn = QPushButton("日记")
        self.today_btn = QPushButton("今日待办")
        self.note_btn = QPushButton("快速笔记")
        
        nav_buttons = [self.diary_btn, self.today_btn, self.note_btn]
        for btn in nav_buttons:
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #F0F0F0;
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
        
        nav_layout.addWidget(self.diary_btn)
        nav_layout.addWidget(self.today_btn)
        nav_layout.addWidget(self.note_btn)
        
        # 视图切换区域
        self.stacked_widget = QStackedWidget()
        self.diary_view = DiaryView(self.file_manager)
        self.today_view = TodayTODOView(self.file_manager)
        self.notes_view = QuickNoteView(self.file_manager)
        
        self.stacked_widget.addWidget(self.diary_view)
        self.stacked_widget.addWidget(self.today_view)
        self.stacked_widget.addWidget(self.notes_view)
        
        # 信号连接
        self.diary_btn.clicked.connect(lambda: self.switch_view(0))
        self.today_btn.clicked.connect(lambda: self.switch_view(1))
        self.note_btn.clicked.connect(lambda: self.switch_view(2))
        
        # 添加布局
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.stacked_widget)
        
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
        
        # 默认选中日记视图
        self.switch_view(0)
        
    def switch_view(self, index):
        self.stacked_widget.setCurrentIndex(index)
        
        # 更新按钮状态
        self.diary_btn.setChecked(index == 0)
        self.today_btn.setChecked(index == 1)
        self.note_btn.setChecked(index == 2)
        
        # 视图更新
        if index == 0:
            self.diary_view.refresh()
        elif index == 1:
            self.today_view.refresh()
        elif index == 2:
            self.notes_view.refresh()

class DiaryView(QWidget):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.current_date = QDate.currentDate()
        self.init_ui()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # 左侧 - 日历
        calendar_layout = QVBoxLayout()
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border-radius: 8px;
            }
            QCalendarWidget QWidget {
                alternate-background-color: white;
            }
            QToolButton::menu-indicator {
                width: 0px;
            }
        """)
        self.calendar.clicked.connect(self.on_date_selected)
        
        self.date_label = QLabel(self.current_date.toString("yyyy年MM月dd日"))
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.date_label.setStyleSheet("color: #5D3FD3; padding: 10px;")
        
        calendar_layout.addWidget(self.date_label)
        calendar_layout.addWidget(self.calendar)
        
        # 右侧 - 日记编辑器
        self.editor = DiaryEditor(self.file_manager)
        
        layout.addLayout(calendar_layout, 1)
        layout.addWidget(self.editor, 2)
        
        self.setLayout(layout)
        
    def on_date_selected(self, date):
        self.current_date = date
        self.date_label.setText(date.toString("yyyy年MM月dd日"))
        self.refresh()
        
    def refresh(self):
        self.editor.load_date(self.current_date)

class DiaryEditor(QWidget):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.current_date = QDate.currentDate()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # TODO部分
        todo_layout = QVBoxLayout()
        todo_label = QLabel("今日待办")
        todo_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        
        self.todo_list = QListWidget()
        self.todo_list.setStyleSheet("""
            QListWidget {
                background-color: #F8F9FA;
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
        self.summary_edit.setStyleSheet("""
            QTextEdit {
                background-color: #F8F9FA;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
            }
        """)
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
        layout.addLayout(todo_layout, 1)
        layout.addLayout(note_layout, 1)
        layout.addLayout(summary_layout, 2)
        
        self.setLayout(layout)
        
    def load_date(self, date):
        self.current_date = date
        
        # 加载日记内容
        content = self.file_manager.load_diary(date)
        
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
                task_text = line.lstrip('- []').strip()
                # 尝试从任务文本中提取标签和优先级
                tags = []
                priority = None
                
                # 查找标签部分
                if '[' in task_text and ']' in task_text:
                    tag_start = task_text.find('[')
                    tag_end = task_text.find(']', tag_start)
                    if tag_end != -1:
                        tag_content = task_text[tag_start+1:tag_end]
                        task_text = task_text[:tag_start].strip()
                        
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
                item_text = task_text
                if priority:
                    item_text += f" ({priority})"
                if tags:
                    item_text += f" {' '.join(['#' + t for t in tags])}"
                
                # 如果行中有 [x] 则表示已完成
                if '[x]' in line or '[X]' in line:
                    completed = True
                    item = QListWidgetItem("✓ " + item_text)
                    item.setForeground(QColor('#757575'))
                    font = QFont()
                    font.setStrikeOut(True)
                    item.setFont(font)
                else:
                    completed = False
                    item = QListWidgetItem("◌ " + item_text)
                
                item.setData(Qt.ItemDataRole.UserRole, {
                    'text': task_text,
                    'completed': completed,
                    'priority': priority,
                    'tags': tags
                })
                self.todo_list.addItem(item)
            elif in_notes and line.strip():
                # 解析笔记条目
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
                            
                            item = QListWidgetItem(f"{time_str} - {note_title}")
                            item.setData(Qt.ItemDataRole.UserRole, note_text)
                            self.note_list.addItem(item)
            elif in_summary:
                self.summary_edit.append(line)
        
        # 将光标移到开始位置
        self.summary_edit.moveCursor(QTextCursor.MoveOperation.Start)
    
    def open_note(self, item):
        note_title = item.text().split(' - ', 1)[1]
        # 在实际项目中，这里应该打开笔记
        QMessageBox.information(self, "打开笔记", f"将打开笔记: {note_title}")
    
    def show_context_menu(self, pos):
        menu = QMenu(self)
        
        # 预定义的文本处理操作
        process_menu = menu.addMenu("文本处理")
        
        # 占位函数
        placeholder_actions = [
            ("大写转换", lambda: self.text_process_function('upper')),
            ("小写转换", lambda: self.text_process_function('lower')),
            ("标记重点", lambda: self.text_process_function('highlight')),
            ("AI摘要", lambda: self.text_process_function('summarize'))
        ]
        
        for name, func in placeholder_actions:
            action = QAction(name, self)
            action.triggered.connect(func)
            process_menu.addAction(action)
        
        # 添加默认文本操作
        menu.addSeparator()
        menu.addAction(self.summary_edit.createStandardContextMenu().actions())
        
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
            line = f"- {mark} {data['text']}"
            if tag_parts:
                line += f" [{', '.join(tag_parts)}]"
            
            content += line + "\n"
        
        content += "\n## Notes\n"
        for i in range(self.note_list.count()):
            item = self.note_list.item(i)
            note_title = item.text().split(' - ', 1)[1]
            time_part = item.text().split(' - ', 1)[0]
            content += f"- {time_part} [[{note_title}]]\n"
        
        content += "\n## Summary\n"
        content += self.summary_edit.toPlainText()
        
        # 保存文件
        self.file_manager.save_diary(self.current_date, content)
        QMessageBox.information(self, "保存成功", "日记已保存")

class TodayTODOView(QWidget):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        title = QLabel("今日待办事项")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #5D3FD3; padding: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 任务列表
        self.task_list = QListWidget()
        self.task_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #EEEEEE;
                font-size: 14px;
            }
            QListWidget::item:selected {
                background-color: #EDE7F6;
            }
        """)
        
        # 添加新任务区域
        add_task_layout = QHBoxLayout()
        self.new_task_input = QLineEdit()
        self.new_task_input.setPlaceholderText("添加新任务...")
        self.new_task_input.setStyleSheet("padding: 10px; font-size: 14px; border-radius: 6px;")
        
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
        
        layout.addWidget(title)
        layout.addWidget(self.task_list)
        layout.addLayout(add_task_layout)
        
        self.setLayout(layout)
        self.refresh()
        
    def refresh(self):
        today = QDate.currentDate()
        
        # 加载今天的日记
        diary_content = self.file_manager.load_diary(today)
        tasks = []
        
        # 提取TODO部分
        in_todo = False
        for line in diary_content.splitlines():
            if line.startswith("## TODO"):
                in_todo = True
                continue
            elif line.startswith("## ") and in_todo:
                break
                
            if in_todo and line.strip() and line.startswith('- '):
                # 提取任务文本
                task_text = line.lstrip('- []').strip()
                # 尝试从任务文本中提取标签
                if '[' in task_text and ']' in task_text:
                    task_text = task_text[:task_text.find('[')].strip()
                
                completed = '[x]' in line or '[X]' in line
                tasks.append((task_text, completed))
        
        # 显示任务
        self.task_list.clear()
        for task_text, completed in tasks:
            item = QListWidgetItem(task_text)
            item.setData(Qt.ItemDataRole.UserRole, {"completed": completed, "text": task_text})
            
            if completed:
                item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                item.setForeground(QColor('#757575'))
                font = QFont()
                font.setStrikeOut(True)
                item.setFont(font)
            else:
                font = QFont()
                font.setBold(True)
                item.setFont(font)
            
            self.task_list.addItem(item)
    
    def add_task(self):
        task_text = self.new_task_input.text().strip()
        if not task_text:
            return
            
        # 添加到列表
        item = QListWidgetItem(task_text)
        item.setData(Qt.ItemDataRole.UserRole, {"completed": False, "text": task_text})
        font = QFont()
        font.setBold(True)
        item.setFont(font)
        self.task_list.addItem(item)
        
        # 清空输入框
        self.new_task_input.clear()
        
        # 更新日记文件
        self.update_diary_tasks()
    
    def update_diary_tasks(self):
        today = QDate.currentDate()
        diary_content = self.file_manager.load_diary(today)
        
        # 重建TODO部分
        new_todo = "## TODO\n"
        for i in range(self.task_list.count()):
            item = self.task_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            
            # 根据完成状态添加不同标记
            mark = "[x]" if data['completed'] else "[ ]"
            
            # 添加任务
            new_todo += f"- {mark} {data['text']}\n"
        
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
        self.file_manager.save_diary(today, diary_content)
        QMessageBox.information(self, "更新成功", "待办事项已更新到日记")

class QuickNoteView(QWidget):
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 标题
        title_layout = QHBoxLayout()
        title = QLabel("快速笔记")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #5D3FD3;")
        
        new_note_btn = QPushButton("新建笔记")
        new_note_btn.setStyleSheet("""
            QPushButton {
                background-color: #5D3FD3;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 6px;
            }
        """)
        new_note_btn.clicked.connect(self.create_new_note)
        
        title_layout.addWidget(title)
        title_layout.addStretch()
        title_layout.addWidget(new_note_btn)
        
        # 笔记列表
        self.notes_list = QListWidget()
        self.notes_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 15px;
                border-bottom: 1px solid #EEEEEE;
            }
            QListWidget::item:selected {
                background-color: #EDE7F6;
            }
        """)
        self.notes_list.itemClicked.connect(self.open_note)
        
        # 设置全局快捷键（在实际应用中需绑定系统快捷键）
        shortcut_hint = QLabel("提示: 按 Cmd+Shift+N 快速新建笔记")
        shortcut_hint.setStyleSheet("color: #757575; font-style: italic;")
        shortcut_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addLayout(title_layout)
        layout.addWidget(self.notes_list)
        layout.addWidget(shortcut_hint)
        
        self.setLayout(layout)
        self.refresh()
    
    def refresh(self):
        self.notes_list.clear()
        notes = self.file_manager.list_notes()
        
        for note_path in notes:
            # 从文件名提取标题和日期
            filename = os.path.basename(note_path)
            if '_' in filename:
                date_part = filename[:8]
                title_part = filename[9:-3]
                date_str = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                
                item = QListWidgetItem(f"{date_str} - {title_part.replace('_', ' ')}")
                item.setData(Qt.ItemDataRole.UserRole, note_path)
                self.notes_list.addItem(item)
    
    def create_new_note(self):
        note_title, ok = QInputDialog.getText(self, "新建笔记", "笔记标题:")
        if ok and note_title.strip():
            self.open_note_editor(note_title.strip())
    
    def open_note(self, item):
        note_path = item.data(Qt.ItemDataRole.UserRole)
        # 提取标题
        filename = os.path.basename(note_path)
        title = filename[9:-3].replace('_', ' ') if '_' in filename else filename[:-3]
        
        self.open_note_editor(title)
    
    def open_note_editor(self, title):
        # 在实际应用中打开笔记编辑窗口
        QMessageBox.information(self, "笔记编辑", f"将编辑笔记: {title}")

# ======================
# 应用入口
# ======================
def main():
    # 设置应用配置
    QApplication.setApplicationName("KairoDiary")
    QApplication.setOrganizationName("KairoSoft")
    
    app = QApplication(sys.argv)
    
    # 获取当前用户的文档目录
    documents_path = os.path.join(os.path.expanduser("~"), "MyDocuments")
    base_path = os.path.join(documents_path, "KairoDiaryData")
    
    file_manager = FileManager(base_path)
    account_manager = AccountManager(file_manager)
    
    # 检查上次登录用户
    config = file_manager.load_config()
    last_login = config.get("last_login")
    
    if last_login:
        # 如果存在上次登录用户，直接进入主界面
        main_win = MainWindow(file_manager)
        main_win.show()
    else:
        # 否则显示登录窗口
        login_win = LoginWindow(account_manager)
        
        def on_login_success():
            login_win.close()
            main_win = MainWindow(file_manager)
            main_win.show()
        
        login_win.login_success.connect(on_login_success)
        login_win.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()