from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, 
    QPushButton, QLineEdit, 
    QMessageBox, QInputDialog, QLabel, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
    
# ======================
# 界面组件
# ======================
class LoginWindow(QDialog):
    login_success = pyqtSignal(str)
    def __init__(self, account_manager):
        super().__init__()
        self.account_manager = account_manager
        self.setModal(True)  # 设置为模态对话框
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
            
            # 发射信号，传递用户名
            self.login_success.emit(username)
            # 使用 Dialog 的 accept 方法
            self.accept()
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
    
    def keyPressEvent(self, event):
        """处理键盘事件"""
        from PyQt6.QtCore import Qt
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # 回车键触发登录
            self.handle_login()
        elif event.key() == Qt.Key.Key_Escape:
            # ESC 键关闭对话框
            self.reject()
        else:
            super().keyPressEvent(event)