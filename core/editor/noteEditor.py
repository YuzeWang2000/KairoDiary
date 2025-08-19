from PyQt6.QtWidgets import QVBoxLayout, QMessageBox
from PyQt6.QtCore import pyqtSignal
from .baseEditor import BaseEditor


class NoteEditor(BaseEditor):
    """
    笔记编辑器组件
    继承自 BaseEditor，提供笔记编辑功能
    """

    note_saved = pyqtSignal(str)  # filename
    content_changed = pyqtSignal(str)
    content_saved = pyqtSignal()  # 用于对话框包装器

    def __init__(self, file_manager, filename, content="", text_processor=None, parent=None):
        super().__init__(text_processor)
        self.file_manager = file_manager
        self.filename = filename
        self.setParent(parent)
        
        self._init_ui(content)

    def _init_ui(self, content: str):
        layout = QVBoxLayout(self)

        self.editor = self.create_text_editor()
        self.editor.setPlainText(content)
        self.editor.textChanged.connect(self._on_text_changed)
        layout.addWidget(self.editor)

    def _on_text_changed(self):
        self.content_changed.emit(self.editor.toPlainText())

    def save_content(self):
        """保存内容，返回是否成功"""
        content = self.editor.toPlainText()
        return_path = self.file_manager.save_note(self.filename, content)
        if return_path is None:
            QMessageBox.warning(self, "保存失败", "无法保存笔记内容")
            return False
        self.note_saved.emit(self.filename)
        self.content_saved.emit()
        return True

    # 对外扩展接口
    def get_content(self) -> str:
        return self.editor.toPlainText()

    def set_content(self, text: str):
        self.editor.setPlainText(text)

