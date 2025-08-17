import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon

from core.server import AccountManager, FileManager
from core.window import LoginWindow, MainWindow


def get_resource_path(relative_path):
    """获取资源文件的正确路径，适用于开发和打包后的环境"""
    try:
        # PyInstaller 创建的临时文件夹
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发环境
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


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
    
    # 设置应用程序图标，根据操作系统选择合适的格式
    if sys.platform == "darwin":  # macOS
        icon_path = get_resource_path("assets/KairoDiary.icns")
    elif sys.platform == "win32":  # Windows
        icon_path = get_resource_path("assets/KairoDiary.ico")
    else:  # Linux 和其他系统
        # 优先尝试 .ico 文件，如果不存在则尝试 .png
        icon_path = get_resource_path("assets/KairoDiary.ico")
        if not os.path.exists(icon_path):
            icon_path = get_resource_path("assets/KairoDiary.png")
    
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        print(f"应用程序图标已设置: {icon_path}")
    else:
        print(f"图标文件未找到: {icon_path}")
    
    # 获取当前用户的文档目录
    documents_path = os.path.join(os.path.expanduser("~"), "MyDocuments")
    base_path = os.path.join(documents_path, "KairoDiaryData")
    
    # 如果目录不存在，自动创建
    try:
        os.makedirs(base_path, exist_ok=True)
        print(f"数据目录已确保存在: {base_path}")
    except OSError as e:
        print(f"无法创建数据目录 {base_path}: {e}")
        # 使用当前目录作为备用方案
        base_path = os.path.join(os.getcwd(), "KairoDiaryData")
        os.makedirs(base_path, exist_ok=True)
        print(f"使用备用数据目录: {base_path}")
    
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
            main_win.showMaximized()  # 使用最大化模式，保留标题栏

    app_loggin()
        
    sys.exit(app.exec())

if __name__ == "__main__":
    main()