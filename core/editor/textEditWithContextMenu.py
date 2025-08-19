from PyQt6.QtWidgets import QTextEdit, QMenu, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QTextBrowser
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QTextCursor


class TextComparisonDialog(QDialog):
    """
    文本对比预览对话框
    用于显示原文本和处理后文本的对比
    """
    
    def __init__(self, original_text, processed_text, method, action_type, parent=None):
        super().__init__(parent)
        self.original_text = original_text
        self.processed_text = processed_text
        self.accepted_replacement = False
        
        self.setWindowTitle(f"文本处理预览 - {action_type}")
        self.setModal(True)
        self.resize(600, 400)
        
        # 设置窗口标志，防止模态会话问题
        self.setWindowFlags(
            Qt.WindowType.Dialog | 
            Qt.WindowType.WindowTitleHint | 
            Qt.WindowType.WindowCloseButtonHint
        )
        
        layout = QVBoxLayout(self)
        
        # 处理方法信息
        method_label = QLabel(f"处理方法: {method}")
        method_label.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(method_label)
        
        # 原文本显示
        layout.addWidget(QLabel("原文本:"))
        original_browser = QTextBrowser()
        original_browser.setPlainText(original_text)
        original_browser.setMaximumHeight(150)
        layout.addWidget(original_browser)
        
        # 处理后文本显示
        layout.addWidget(QLabel("处理后文本:"))
        processed_browser = QTextBrowser()
        processed_browser.setPlainText(processed_text)
        processed_browser.setMaximumHeight(150)
        layout.addWidget(processed_browser)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        accept_btn = QPushButton("应用更改")
        accept_btn.clicked.connect(self.accept_replacement)
        accept_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; padding: 8px; }")
        
        reject_btn = QPushButton("取消")
        reject_btn.clicked.connect(self.reject_replacement)
        reject_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; padding: 8px; }")
        
        button_layout.addWidget(reject_btn)
        button_layout.addWidget(accept_btn)
        layout.addLayout(button_layout)
    
    def accept_replacement(self):
        """用户确认替换"""
        self.accepted_replacement = True
        self.accept()
    
    def reject_replacement(self):
        """用户取消替换"""
        self.accepted_replacement = False
        self.reject()
    
    def closeEvent(self, event):
        """处理窗口关闭事件"""
        self.accepted_replacement = False
        event.accept()


class TextEditWithContextMenu(QTextEdit):
    """
    带有右键菜单的文本编辑器组件
    集成了文本处理功能
    """
    
    def __init__(self, text_processor=None, parent=None):
        super().__init__(parent)
        self.text_processor = text_processor
        
        # 设置右键菜单
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def set_text_processor(self, text_processor):
        """设置文本处理器"""
        self.text_processor = text_processor
    
    def show_context_menu(self, pos):
        """
        显示右键菜单
        """
        menu = QMenu(self)
        
        # 逐步添加标准菜单
        standard_menu = self.createStandardContextMenu()
        standard_menu.setTitle("编辑操作")
        # 添加到主菜单
        menu.addMenu(standard_menu)
        menu.addSeparator()
        
        # 文本处理菜单
        process_menu = menu.addMenu("文本处理")
        
                # 基本文字处理
        basic_process_menu = process_menu.addMenu("基本处理")
        basic_actions = [
            ("大小写转换", lambda: self.text_process_function('upper_lower', is_basic=True)),
            ("首字母大写", lambda: self.text_process_function('capitalize', is_basic=True)),
            ("标记重点", lambda: self.text_process_function('highlight', is_basic=True))
        ]
        
        for name, func in basic_actions:
            action = QAction(name, self)
            action.triggered.connect(func)
            basic_process_menu.addAction(action)
        
        # 高级文字处理
        advanced_process_menu = process_menu.addMenu("高级处理")
        advanced_actions = [
            ("拼写检查", lambda: self.text_process_function('spell_check', is_basic=False)),
            ("翻译", lambda: self.text_process_function('translate', is_basic=False)),
            ("润色", lambda: self.text_process_function('polish', is_basic=False)),
            ("总结", lambda: self.text_process_function('summarize', is_basic=False))
        ]
        
        for name, func in advanced_actions:
            action = QAction(name, self)
            action.triggered.connect(func)
            advanced_process_menu.addAction(action)
        
        menu.exec(self.mapToGlobal(pos))
    
    def text_process_function(self, action_type, is_basic=True):
        """
        文本处理功能
        is_basic: True为基本处理(直接替换), False为高级处理(需要用户确认)
        """
        cursor = self.textCursor()
        selected_text = cursor.selectedText()
        
        if not selected_text:
            QMessageBox.information(self, "提示", "请先选择文本")
            return
        
        try:
            # 使用 TextProcessor 处理文本
            if action_type == 'upper_lower':
                new_text = selected_text.swapcase()
                method = "基本方法"
            elif action_type == 'capitalize':
                new_text = selected_text.capitalize()
                method = "基本方法"
            elif action_type == 'highlight':
                if "<strong>" in selected_text and "</strong>" in selected_text:
                    new_text = selected_text.replace("<strong>", "").replace("</strong>", "")
                else:
                    new_text = f"<strong>{selected_text}</strong>"
                method = "基本方法"
            elif action_type == 'spell_check':
                if hasattr(self, 'text_processor') and self.text_processor:
                    new_text, method = self.text_processor.spell_check(selected_text)
                else:
                    new_text = selected_text
                    method = "TextProcessor 不可用"
            elif action_type == 'translate':
                if hasattr(self, 'text_processor') and self.text_processor:
                    new_text, method = self.text_processor.translate(selected_text)
                else:
                    new_text = selected_text
                    method = "TextProcessor 不可用"
            elif action_type == 'polish':
                if hasattr(self, 'text_processor') and self.text_processor:
                    new_text, method = self.text_processor.polish(selected_text)
                else:
                    new_text = selected_text
                    method = "TextProcessor 不可用"
            elif action_type == 'summarize':
                if hasattr(self, 'text_processor') and self.text_processor:
                    new_text, method = self.text_processor.summarize(selected_text)
                else:
                    new_text = selected_text
                    method = "TextProcessor 不可用"
            else:
                raise ValueError(f"未知操作类型: {action_type}")
            
            # 根据处理类型决定是否需要用户确认
            if is_basic:
                # 基本处理：直接替换
                cursor.insertText(new_text)
                QMessageBox.information(
                    self, 
                    "文本处理完成", 
                    f"处理类型: {action_type}\n使用方法: {method}\n\n已直接应用更改"
                )
            else:
                # 高级处理：显示预览对话框
                dialog = TextComparisonDialog(
                    selected_text, 
                    new_text, 
                    method, 
                    action_type, 
                    self
                )
                
                # 使用 exec() 而不是 exec_() 来避免模态会话问题
                result = dialog.exec()
                
                if result == QDialog.DialogCode.Accepted and dialog.accepted_replacement:
                    # 用户确认替换
                    cursor.insertText(new_text)
                    QMessageBox.information(self, "处理完成", "文本已成功替换")
                
                # 确保对话框被正确清理
                dialog.deleteLater()
                # 如果用户取消，则不做任何操作
            
        except Exception as e:
            QMessageBox.critical(self, "处理错误", f"文本处理时发生错误:\n{str(e)}")
            print(f"TextProcessor 错误: {e}")
