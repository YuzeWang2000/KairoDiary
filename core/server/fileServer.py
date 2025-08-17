import os
import json
from datetime import datetime
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QDate
# ======================
# 文件管理器
# ======================
class FileManager:
    def __init__(self, base_path, username):
        self.username = username
        self.user_base_path = os.path.join(base_path, username)
        os.makedirs(self.user_base_path, exist_ok=True)
        
        # 创建用户专属目录结构
        self.user_note_dir = os.path.join(self.user_base_path, "QuickNote")
        self.user_diary_dir = os.path.join(self.user_base_path, "Diary")
        os.makedirs(self.user_note_dir, exist_ok=True)
        os.makedirs(self.user_diary_dir, exist_ok=True)
        
        self.config_path = os.path.join(self.user_base_path, "config.json")
        self.init_config()
        
    def init_config(self):
        """初始化用户的配置文件"""
        if not os.path.exists(self.config_path):
            default_config = {
                "tags": ["工作", "学习", "生活", "重要"],
                "default_view": "Diary",
                "last_access": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "theme": "system"  # 添加用户主题偏好
            }
            self.save_config(default_config)
    
    def load_config(self):
        """加载用户配置"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # 更新上次访问时间
                config["last_access"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self.save_config(config)
                return config
        except Exception as e:
            print(f"加载配置失败: {e}")
            return self.init_config() or {}
    
    def save_config(self, config):
        """保存用户配置"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False
    
    def get_diary_dir(self):
        """获取用户日记目录"""
        return self.user_diary_dir
    
    def get_diary_path(self, date=None):
        """获取指定日期的日记文件路径"""
        if date is None:
            date = QDate.currentDate()
        year = str(date.year())
        month = str(date.month()).zfill(2)
        diary_dir = os.path.join(self.user_diary_dir, year, month)
        os.makedirs(diary_dir, exist_ok=True)
        return os.path.join(diary_dir, f"{date.toString('yyyy-MM-dd')}.md")
    
    def save_diary(self, date, content):
        """保存日记内容"""
        path = self.get_diary_path(date)
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"保存日记失败: {e}")
            return False
    
    def load_diary(self, date):
        """加载日记内容"""
        path = self.get_diary_path(date)
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            return ""
        except Exception as e:
            print(f"加载日记失败: {e}")
            return ""

    def get_note_dir(self):
        """获取快速笔记目录"""
        return self.user_note_dir
    
    def get_note_path(self, filename):
        """获取笔记文件路径"""
        return os.path.join(self.user_note_dir, filename)
    
    def save_note(self, filename, content, title=None):
        """保存快速笔记"""
        note_path = self.get_note_path(filename)
        if not os.path.exists(note_path):
            try:
                with open(note_path, 'w', encoding='utf-8') as f:
                    # 第一次需要写入标题和创建时间
                    f.write(f"# {title}\n\n")
                    f.write(f"Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(content)
                return note_path
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法创建笔记: {str(e)}")
                return None
        else:
            try:
                with open(note_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return note_path
            except Exception as e:
                print(f"保存笔记失败: {e}")
                return None
    
    def load_note(self, filename):
        """加载笔记内容"""
        path = self.get_note_path(filename)
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            return "无法加载笔记内容"
        except Exception as e:
            print(f"加载笔记失败: {e}")
            return "无法加载笔记内容"
    
    def list_notes(self):
        """列出所有笔记文件"""
        notes_dir = os.path.join(self.user_base_path, "QuickNote")
        try:
            return [os.path.join(notes_dir, f) for f in os.listdir(notes_dir) 
                    if f.endswith('.md') and os.path.isfile(os.path.join(notes_dir, f))]
        except FileNotFoundError:
            # 目录不存在时创建
            os.makedirs(notes_dir, exist_ok=True)
            return []
    
    def migrate_old_data(self):
        """迁移旧版数据（如果需要）"""
        # 如果有旧版本数据迁移逻辑可在此实现
        pass

    def get_diary_dates_for_month(self, year, month):
        """获取指定月份有日记的日期列表"""
        diary_dir = os.path.join(self.user_base_path, "Diary", str(year), f"{month:02d}")
        dates = []
        
        if os.path.exists(diary_dir):
            for file in os.listdir(diary_dir):
                if file.endswith('.md'):
                    try:
                        # 从文件名提取日期
                        date_str = file.split('.')[0]
                        date = QDate.fromString(date_str, "yyyy-MM-dd")
                        if date.isValid():
                            dates.append(date)
                    except:
                        continue
        
        return dates