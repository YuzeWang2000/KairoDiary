import os
from PyQt6.QtWidgets import QWidget, QDialog, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt6.QtCore import pyqtSignal
from .textEditWithContextMenu import TextEditWithContextMenu


class BaseEditor(QWidget):
    """
    编辑器基类
    提供通用的编辑器功能和文本处理器支持
    """
    def __init__(self, text_processor=None):
        super().__init__()
        self.text_processor = text_processor
    
    def create_text_editor(self):
        """
        创建带有右键菜单的文本编辑器
        """
        return TextEditWithContextMenu(self.text_processor, self)


class BaseEditorDialog(QDialog):
    """
    编辑器对话框包装器
    将 BaseEditor 包装成对话框形式
    """
    def __init__(self, editor_widget, title="编辑器", parent=None):
        super().__init__(parent)
        self.editor_widget = editor_widget
        self.setWindowTitle(title)
        self.resize(700, 500)
        
        # 将编辑器信号转发
        if hasattr(editor_widget, 'content_saved'):
            editor_widget.content_saved.connect(self.accept)
        
        self._init_ui()
    
    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # 添加编辑器组件
        layout.addWidget(self.editor_widget)
        
        # 添加按钮
        btn_layout = QHBoxLayout()
        
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
        cancel_btn.clicked.connect(self.reject)
        
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
        save_btn.clicked.connect(self._on_save)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
    
    def _on_save(self):
        """保存并关闭对话框"""
        if hasattr(self.editor_widget, 'save_content'):
            if self.editor_widget.save_content():
                self.accept()
        else:
            self.accept()
