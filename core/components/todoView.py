
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QLineEdit, QListWidgetItem,
    QMessageBox, QInputDialog, QLabel, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QSize, QDateTime
from PyQt6.QtGui import QFont


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
