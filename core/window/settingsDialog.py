from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, 
    QPushButton, QInputDialog, QMessageBox, QTabWidget, QWidget,
)


class SettingsDialog(QDialog):
    def __init__(self, file_manager, parent=None):
        super().__init__(parent)
        self.file_manager = file_manager
        self.setWindowTitle("账户设置")
        self.setGeometry(200, 200, 500, 400)
        self.setModal(True)
        
        self.init_ui()
        self.load_tags()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout()
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 笔记标签页
        self.note_tags_tab = QWidget()
        self.init_note_tags_tab()
        self.tab_widget.addTab(self.note_tags_tab, "笔记标签")
        
        # 待办标签页
        self.todo_tags_tab = QWidget()
        self.init_todo_tags_tab()
        self.tab_widget.addTab(self.todo_tags_tab, "待办标签")
        
        layout.addWidget(self.tab_widget)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.save_btn = QPushButton("保存")
        self.cancel_btn = QPushButton("取消")
        
        self.save_btn.clicked.connect(self.save_settings)
        self.cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def init_note_tags_tab(self):
        """初始化笔记标签页"""
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("笔记标签管理")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 说明文字
        desc_label = QLabel("管理您的笔记分类标签，可以添加、修改或删除标签。")
        desc_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(desc_label)
        
        # 标签列表
        self.note_tags_list = QListWidget()
        self.note_tags_list.setMaximumHeight(200)
        layout.addWidget(self.note_tags_list)
        
        # 按钮
        note_button_layout = QHBoxLayout()
        self.add_note_tag_btn = QPushButton("添加标签")
        self.edit_note_tag_btn = QPushButton("修改标签")
        self.delete_note_tag_btn = QPushButton("删除标签")
        
        self.add_note_tag_btn.clicked.connect(lambda: self.add_tag("note"))
        self.edit_note_tag_btn.clicked.connect(lambda: self.edit_tag("note"))
        self.delete_note_tag_btn.clicked.connect(lambda: self.delete_tag("note"))
        
        note_button_layout.addWidget(self.add_note_tag_btn)
        note_button_layout.addWidget(self.edit_note_tag_btn)
        note_button_layout.addWidget(self.delete_note_tag_btn)
        note_button_layout.addStretch()
        
        layout.addLayout(note_button_layout)
        self.note_tags_tab.setLayout(layout)
    
    def init_todo_tags_tab(self):
        """初始化待办标签页"""
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("待办事项标签管理")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # 说明文字
        desc_label = QLabel("管理您的待办事项分类标签，可以添加、修改或删除标签。")
        desc_label.setStyleSheet("color: #666; margin-bottom: 15px;")
        layout.addWidget(desc_label)
        
        # 标签列表
        self.todo_tags_list = QListWidget()
        self.todo_tags_list.setMaximumHeight(200)
        layout.addWidget(self.todo_tags_list)
        
        # 按钮
        todo_button_layout = QHBoxLayout()
        self.add_todo_tag_btn = QPushButton("添加标签")
        self.edit_todo_tag_btn = QPushButton("修改标签")
        self.delete_todo_tag_btn = QPushButton("删除标签")
        
        self.add_todo_tag_btn.clicked.connect(lambda: self.add_tag("todo"))
        self.edit_todo_tag_btn.clicked.connect(lambda: self.edit_tag("todo"))
        self.delete_todo_tag_btn.clicked.connect(lambda: self.delete_tag("todo"))
        
        todo_button_layout.addWidget(self.add_todo_tag_btn)
        todo_button_layout.addWidget(self.edit_todo_tag_btn)
        todo_button_layout.addWidget(self.delete_todo_tag_btn)
        todo_button_layout.addStretch()
        
        layout.addLayout(todo_button_layout)
        self.todo_tags_tab.setLayout(layout)
    
    def load_tags(self):
        """加载标签数据"""
        # 加载笔记标签
        note_tags = self.file_manager.get_note_tags()
        self.note_tags_list.clear()
        for tag in note_tags:
            self.note_tags_list.addItem(tag)
        
        # 加载待办标签
        todo_tags = self.file_manager.get_todo_tags()
        self.todo_tags_list.clear()
        for tag in todo_tags:
            self.todo_tags_list.addItem(tag)
    
    def add_tag(self, tag_type):
        """添加标签"""
        tag_name, ok = QInputDialog.getText(
            self, 
            f"添加{'笔记' if tag_type == 'note' else '待办'}标签", 
            "请输入标签名称:"
        )
        
        if ok and tag_name.strip():
            tag_name = tag_name.strip()
            
            # 检查是否已存在
            list_widget = self.note_tags_list if tag_type == "note" else self.todo_tags_list
            existing_tags = [list_widget.item(i).text() for i in range(list_widget.count())]
            
            if tag_name in existing_tags:
                QMessageBox.warning(self, "警告", "该标签已存在！")
                return
            
            # 添加到列表
            list_widget.addItem(tag_name)
    
    def edit_tag(self, tag_type):
        """修改标签"""
        list_widget = self.note_tags_list if tag_type == "note" else self.todo_tags_list
        current_item = list_widget.currentItem()
        
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要修改的标签！")
            return
        
        old_name = current_item.text()
        new_name, ok = QInputDialog.getText(
            self, 
            f"修改{'笔记' if tag_type == 'note' else '待办'}标签", 
            "请输入新的标签名称:", 
            text=old_name
        )
        
        if ok and new_name.strip():
            new_name = new_name.strip()
            
            # 检查是否已存在（除了当前项）
            existing_tags = [list_widget.item(i).text() for i in range(list_widget.count()) 
                           if list_widget.item(i) != current_item]
            
            if new_name in existing_tags:
                QMessageBox.warning(self, "警告", "该标签已存在！")
                return
            
            # 更新标签名称
            current_item.setText(new_name)
    
    def delete_tag(self, tag_type):
        """删除标签"""
        list_widget = self.note_tags_list if tag_type == "note" else self.todo_tags_list
        current_item = list_widget.currentItem()
        
        if not current_item:
            QMessageBox.warning(self, "警告", "请先选择要删除的标签！")
            return
        
        tag_name = current_item.text()
        
        # 确认删除
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除标签 '{tag_name}' 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 删除选中的项
            row = list_widget.row(current_item)
            list_widget.takeItem(row)
    
    def save_settings(self):
        """保存设置"""
        try:
            # 获取笔记标签
            note_tags = [self.note_tags_list.item(i).text() 
                        for i in range(self.note_tags_list.count())]
            
            # 获取待办标签
            todo_tags = [self.todo_tags_list.item(i).text() 
                        for i in range(self.todo_tags_list.count())]
            
            # 验证不能为空
            if not note_tags:
                QMessageBox.warning(self, "警告", "笔记标签不能为空！")
                return
            
            if not todo_tags:
                QMessageBox.warning(self, "警告", "待办标签不能为空！")
                return
            
            # 保存到文件管理器
            note_success = self.file_manager.set_note_tags(note_tags)
            todo_success = self.file_manager.set_todo_tags(todo_tags)
            
            if note_success and todo_success:
                QMessageBox.information(self, "成功", "设置已保存！")
                self.accept()
            else:
                QMessageBox.critical(self, "错误", "保存设置失败！")
                
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存设置时发生错误: {str(e)}")
