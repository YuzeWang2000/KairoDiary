import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QTextEdit, QLineEdit, QListWidgetItem,
    QMessageBox, QInputDialog, QLabel, QMenu, QComboBox, QDialog,
    QScrollArea
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QDateTime
from PyQt6.QtGui import QFont, QIcon

class QuickNoteView(QWidget):
    notename_changed = pyqtSignal(str, str) # old_filename, new_filename
    note_deleted = pyqtSignal(str)
    note_created = pyqtSignal(str)
    def __init__(self, file_manager):
        super().__init__()
        self.file_manager = file_manager
        self.filter_tag = None
        self.init_ui()
    
    def format_time_human_readable(self, timestamp):
        """将时间戳转换为人类可读的格式"""
        try:
            modified_time = datetime.fromtimestamp(timestamp)
            now = datetime.now()
            
            # 计算时间差
            time_diff = now - modified_time
            
            if time_diff.days == 0:
                # 今天
                if time_diff.seconds < 3600:  # 1小时内
                    minutes = time_diff.seconds // 60
                    if minutes == 0:
                        return "刚刚"
                    elif minutes < 60:
                        return f"{minutes}分钟前"
                else:  # 1小时以上
                    hours = time_diff.seconds // 3600
                    return f"{hours}小时前"
            elif time_diff.days == 1:
                return "昨天"
            elif time_diff.days < 7:
                return f"{time_diff.days}天前"
            elif time_diff.days < 30:
                weeks = time_diff.days // 7
                return f"{weeks}周前"
            elif time_diff.days < 365:
                months = time_diff.days // 30
                return f"{months}个月前"
            else:
                return modified_time.strftime("%Y年%m月%d日")
        except:
            return "未知时间"
        
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
            
            # 获取文件修改时间
            try:
                file_modified_time = os.path.getmtime(note_path)
                human_time = self.format_time_human_readable(file_modified_time)
            except:
                human_time = "未知时间"
            
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
            # title_label.setStyleSheet("color: #212121;")
            title_layout.addWidget(title_label)
            
            title_layout.addStretch()
            
            # 修改时间（人类可读格式）
            time_label = QLabel(human_time)
            time_label.setFont(QFont("Arial", 10))
            time_label.setStyleSheet("color: #757575;")
            title_layout.addWidget(time_label)
            
            # 如果有创建日期，也显示
            if note_date:
                date_label = QLabel(f"创建: {note_date}")
                date_label.setFont(QFont("Arial", 9))
                date_label.setStyleSheet("color: #9E9E9E;")
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
        dialog.setFixedSize(500, 450)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)
        
        # 笔记标题
        title_label = QLabel("笔记标题:")
        title_label.setStyleSheet("font-weight: bold;")
        self.new_note_title = QLineEdit()
        self.new_note_title.setPlaceholderText("输入笔记标题")
        
        # 标签输入
        tags_label = QLabel("标签 (可选, 用逗号分隔):")
        tags_label.setStyleSheet("font-weight: bold;")
        self.new_note_tags = QLineEdit()
        self.new_note_tags.setPlaceholderText("例如: 工作,项目")
        
        # 已有标签区域
        existing_tags_label = QLabel("已有标签 (点击添加):")
        existing_tags_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        
        # 标签按钮滚动区域
        tags_scroll = QScrollArea()
        tags_scroll.setMaximumHeight(120)
        tags_scroll.setWidgetResizable(True)
        tags_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        tags_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        tags_widget = QWidget()
        self.tags_flow_layout = QVBoxLayout(tags_widget)
        self.tags_flow_layout.setContentsMargins(5, 5, 5, 5)
        self.tags_flow_layout.setSpacing(5)
        
        # 创建标签按钮的水平布局容器
        self.tags_button_container = QWidget()
        self.tags_button_layout = QHBoxLayout(self.tags_button_container)
        self.tags_button_layout.setSpacing(5)
        
        # 获取现有标签并创建按钮
        existing_tags = self.file_manager.get_note_tags()
        self.update_tag_buttons(existing_tags)
        
        self.tags_flow_layout.addWidget(self.tags_button_container)
        self.tags_flow_layout.addStretch()
        
        tags_scroll.setWidget(tags_widget)
        
        # 新标签管理
        new_tag_layout = QHBoxLayout()
        new_tag_layout.setContentsMargins(0, 10, 0, 0)
        
        self.new_tag_input = QLineEdit()
        self.new_tag_input.setPlaceholderText("添加新标签...")
        self.new_tag_input.setStyleSheet("""
            QLineEdit {
                padding: 6px 10px;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
        """)
        
        add_tag_btn = QPushButton("添加到标签库")
        add_tag_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 6px 12px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_tag_btn.clicked.connect(self.add_new_tag_to_library)
        
        new_tag_layout.addWidget(QLabel("新标签:"))
        new_tag_layout.addWidget(self.new_tag_input, 1)
        new_tag_layout.addWidget(add_tag_btn)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        btn_layout.setContentsMargins(0, 15, 0, 0)
        
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
        
        # 添加所有组件到主布局
        layout.addWidget(title_label)
        layout.addWidget(self.new_note_title)
        layout.addWidget(tags_label)
        layout.addWidget(self.new_note_tags)
        layout.addWidget(existing_tags_label)
        layout.addWidget(tags_scroll, 1)  # 给标签区域更多空间
        layout.addLayout(new_tag_layout)
        layout.addLayout(btn_layout)
        
        dialog.exec()
    
    def update_tag_buttons(self, tags):
        """更新标签按钮显示"""
        # 清除现有按钮
        while self.tags_button_layout.count():
            child = self.tags_button_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # 创建标签按钮
        for tag in tags:
            tag_btn = QPushButton(f"#{tag}")
            tag_btn.setStyleSheet("""
                QPushButton {
                    background-color: #E8EAF6;
                    color: #3F51B5;
                    border: 1px solid #C5CAE9;
                    border-radius: 15px;
                    padding: 5px 12px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #C5CAE9;
                }
                QPushButton:pressed {
                    background-color: #9FA8DA;
                }
            """)
            tag_btn.clicked.connect(lambda checked, t=tag: self.add_tag_to_input(t))
            self.tags_button_layout.addWidget(tag_btn)
        
        # 添加弹性空间
        self.tags_button_layout.addStretch()

    def add_tag_to_input(self, tag):
        """将标签添加到输入框"""
        current_text = self.new_note_tags.text().strip()
        
        # 获取当前已输入的标签
        existing_tags = []
        if current_text:
            existing_tags = [t.strip() for t in current_text.split(',') if t.strip()]
        
        # 检查是否已存在该标签
        if tag not in existing_tags:
            if existing_tags:
                new_text = ', '.join(existing_tags + [tag])
            else:
                new_text = tag
            self.new_note_tags.setText(new_text)

    def add_new_tag_to_library(self):
        """添加新标签到标签库"""
        new_tag = self.new_tag_input.text().strip()
        if not new_tag:
            QMessageBox.warning(self, "输入错误", "请输入标签名称")
            return
        
        # 获取现有标签
        existing_tags = self.file_manager.get_note_tags()
        
        # 检查是否已存在
        if new_tag in existing_tags:
            QMessageBox.information(self, "提示", f"标签 '{new_tag}' 已存在")
            return
        
        # 添加新标签并保存
        new_tags_list = existing_tags + [new_tag]
        if self.file_manager.set_note_tags(new_tags_list):
            QMessageBox.information(self, "成功", f"标签 '{new_tag}' 已添加到标签库")
            # 更新按钮显示
            self.update_tag_buttons(new_tags_list)
            # 清空输入框
            self.new_tag_input.clear()
            # 同时添加到当前笔记的标签输入框
            self.add_tag_to_input(new_tag)
        else:
            QMessageBox.critical(self, "错误", "保存标签失败")
    
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
            else:
                QMessageBox.critical(self, "错误", "无法创建笔记")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法创建笔记: {str(e)}")
            return
            
        dialog.accept()
        
        # 自动打开新笔记
        self.open_note_editor(filename)
    
    def open_note(self, item):
        """打开选中的笔记"""
        note_path = item.data(Qt.ItemDataRole.UserRole)
        filename = os.path.basename(note_path)
        self.open_note_editor(filename)
    
    def open_note_editor(self, filename):
        """打开笔记编辑器"""
        print(f"打开笔记编辑器: {filename}")
        success, result = self.file_manager.load_note(filename)
        if success:
            content = result  # 正常内容
        else:
            error = result   # 异常对象
            if isinstance(error, FileNotFoundError):
                content = f"文件不存在，{error}"
                self.note_deleted.emit(filename)  # 如果文件不存在，发出删除信号
            else:
                content = f"加载失败，{error}"
        editor_dialog = QDialog(self)
        editor_dialog.setWindowTitle(f"编辑笔记: {filename}")
        editor_dialog.resize(600, 400)
        
        layout = QVBoxLayout(editor_dialog)
        editor = QTextEdit()
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
        
        # 对话框关闭后再刷新列表，避免竞态条件
        self.refresh()

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
                self.notename_changed.emit(filename, new_filename)
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
                self.note_deleted.emit(os.path.basename(note_path))
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
            self.notename_changed.emit(old_filename, new_filename)
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
            self.notename_changed.emit(old_filename, new_filename)
        except:
            QMessageBox.warning(self, "操作失败", "无法移除标签")
