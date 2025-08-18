import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QTextEdit, QListWidgetItem,
    QMessageBox, QInputDialog, QLabel, QMenu, QSizePolicy
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QSize, QDateTime, QTime
from PyQt6.QtGui import QFont, QAction, QTextCursor
from core.server import textServer
class DiaryEditor(QWidget):
    diary_saved = pyqtSignal(QDateTime) 
    open_note_signal = pyqtSignal(str)  # 新增信号用于打开笔记
    def __init__(self, file_manager):
        super().__init__()
        self.text_processor = textServer.TextProcessor()
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
        # 占位函数
        placeholder_actions = [
            ("大小写转换", lambda: self.text_process_function('upper_lower')),
            ("首字母大写", lambda: self.text_process_function('capitalize')),
            ("标记重点", lambda: self.text_process_function('highlight')),
            ("拼写检查", lambda: self.text_process_function('spell_check')),
            ("翻译", lambda: self.text_process_function('translate')),
            ("润色", lambda: self.text_process_function('polish')),
            ("总结", lambda: self.text_process_function('summarize'))
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
        
        try:
            # 使用 TextProcessor 处理文本
            if action_type == 'upper_lower':
                new_text = selected_text.swapcase()
                method = "Traditional Method"
            elif action_type == 'capitalize':
                new_text = selected_text.capitalize()
                method = "Traditional Method"
            elif action_type == 'highlight':
                if "<strong>" in selected_text and "</strong>" in selected_text:
                    new_text = selected_text.replace("<strong>", "").replace("</strong>", "")
                else:
                    new_text = f"<strong>{selected_text}</strong>"
                method = "Traditional Method"
            elif action_type == 'spell_check':
                new_text, method = self.text_processor.spell_check(selected_text)
            elif action_type == 'translate':
                new_text, method = self.text_processor.translate(selected_text)
            elif action_type == 'polish':
                new_text, method = self.text_processor.polish(selected_text)
            elif action_type == 'summarize':
                new_text, method = self.text_processor.summarize(selected_text)
            else:
                raise ValueError(f"未知操作类型: {action_type}")
            
            # 替换选中的文本
            cursor.insertText(new_text)
            
            # 显示处理结果
            QMessageBox.information(
                self, 
                "文本处理完成", 
                f"处理类型: {action_type}\n使用方法: {method}\n\n原文: {selected_text[:50]}{'...' if len(selected_text) > 50 else ''}\n\n结果: {new_text[:50]}{'...' if len(new_text) > 50 else ''}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "处理错误", f"文本处理时发生错误:\n{str(e)}")
            print(f"TextProcessor 错误: {e}")

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

    def remove_note(self, filename):
        """
        从笔记列表中移除指定的笔记
        参数:
            filename: 要移除的笔记文件名
        """
        for i in range(self.note_list.count()):
            item = self.note_list.item(i)
            stored_filename = item.data(Qt.ItemDataRole.UserRole)
            
            if stored_filename == filename:
                # 找到匹配的项，删除它
                self.note_list.takeItem(i)
                print(f"已从日记中移除笔记: {filename}")
                
                # 保存日记更新
                self.save_diary()
                break
        else:
            print(f"未在当前日记中找到笔记: {filename}")

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
