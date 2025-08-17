import sys
import os
from PyQt6.QtWidgets import QApplication

from core.server import AccountManager, FileManager
from core.window import LoginWindow, MainWindow
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
    main_win = None


    def app_loggin():
        """处理登出请求"""
        
        account_manager = AccountManager(base_path)
        nonlocal login_win, main_win
        
        # 如果有主窗口正在运行，先关闭它
        if main_win is not None:
            print("用户请求登出，关闭主窗口")
            main_win.close()
            main_win = None
        else:
            print("用户未登录，显示登录窗口")
        
        login_win = LoginWindow(account_manager)
        login_win.login_success.connect(on_login_success)
        
        # 使用 exec() 方法显示模态对话框
        result = login_win.exec()
        if result == LoginWindow.DialogCode.Rejected:
            # 用户取消登录，彻底退出应用
            sys.exit(0)

    def on_login_success(username):
            # 不需要手动关闭，accept() 已经处理了
            nonlocal main_win
            file_manager = FileManager(base_path, username)
            main_win = MainWindow(username, file_manager)
            main_win.logout_requested.connect(app_loggin)
            main_win.showFullScreen()

    app_loggin()
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()