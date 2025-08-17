import os
import json
import hashlib
from datetime import datetime
# ======================
# 账户管理器
# ======================
class AccountManager:
    def __init__(self, base_path):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        self.global_config_path = os.path.join(base_path, "global_config.json")
        self.init_global_config()
    
    def init_global_config(self):
        """初始化全局配置文件"""
        if not os.path.exists(self.global_config_path):
            default_config = {
                "users": {},
                "last_login": None,
                "system_settings": {}
            }
            self.save_global_config(default_config)
    
    def load_global_config(self):
        """加载全局配置"""
        try:
            with open(self.global_config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            # 文件损坏或不存在时重新初始化
            return self.init_global_config() or {}
    
    def save_global_config(self, config):
        """保存全局配置"""
        try:
            with open(self.global_config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存全局配置失败: {e}")
            return False
    
    def register(self, username, password):
        """注册新用户"""
        config = self.load_global_config()
        
        # 验证用户名唯一性
        if username in config.get("users", {}):
            return False, "用户名已存在"
        
        # 验证用户名有效性
        if not username or any(char in username for char in ' \\/:'):
            return False, "用户名包含非法字符"
        
        # 验证密码强度
        if len(password) < 6:
            return False, "密码长度至少需要6个字符"
        
        # 安全存储密码
        salt = os.urandom(16)
        iterations = 150000  # 适当增加迭代次数增强安全性
        key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
        
        # 更新配置
        config.setdefault("users", {})[username] = {
            'salt': salt.hex(),
            'key': key.hex(),
            'iterations': iterations,
            'created_at': datetime.now().strftime("%Y-%m-%d %H:%M"),
            'diary_count': 0,
            'note_count': 0
        }
        
        # 设置为新用户
        config["last_login"] = username
        
        # 保存配置
        if self.save_global_config(config):
            return True, "注册成功"
        return False, "注册失败，无法保存配置"
    
    def login(self, username, password):
        """用户登录"""
        config = self.load_global_config()
        
        # 验证用户是否存在
        if username not in config.get("users", {}):
            return False, "用户不存在"
        
        user_data = config["users"][username]
        
        # 获取密码相关参数
        salt = bytes.fromhex(user_data['salt'])
        stored_key = bytes.fromhex(user_data['key'])
        iterations = user_data.get('iterations', 100000)  # 兼容旧版本
        
        # 计算输入密码的哈希
        new_key = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, iterations)
        
        # 安全比较密码哈希
        if self.safe_compare(stored_key, new_key):
            # 更新登录时间和次数
            user_data.setdefault('login_count', 0)
            user_data['login_count'] += 1
            user_data['last_login'] = datetime.now().strftime("%Y-%m-%d %H:%M")
            
            
            # 保存更新
            self.save_global_config(config)
            
            # # 检查用户数据目录是否存在
            # user_dir = os.path.join(self.base_path, "users", username)
            # os.makedirs(user_dir, exist_ok=True)
            
            return True, "登录成功"
            
        return False, "密码错误"
    
    def safe_compare(self, a, b):
        """安全比较两个字节序列 (防御时序攻击)"""
        if len(a) != len(b):
            return False
            
        result = 0
        for x, y in zip(a, b):
            result |= x ^ y
        return result == 0
    
    def list_users(self):
        """获取所有用户列表"""
        config = self.load_global_config()
        return list(config.get("users", {}).keys())
    
    def get_user_info(self, username):
        """获取用户信息"""
        config = self.load_global_config()
        user = config.get("users", {}).get(username)
        if user:
            return {
                'username': username,
                'created_at': user.get('created_at'),
                'last_login': user.get('last_login'),
                'login_count': user.get('login_count', 0),
                'diary_count': user.get('diary_count', 0),
                'note_count': user.get('note_count', 0)
            }
        return None
    
    def change_password(self, username, old_password, new_password):
        """更改用户密码"""
        success, message = self.login(username, old_password)
        if not success:
            return False, message
            
        config = self.load_global_config()
        user_data = config["users"][username]
        
        # 更新密码哈希
        salt = bytes.fromhex(user_data['salt'])
        iterations = user_data.get('iterations', 150000)
        key = hashlib.pbkdf2_hmac('sha256', new_password.encode(), salt, iterations)
        
        user_data['key'] = key.hex()
        
        if self.save_global_config(config):
            return True, "密码更改成功"
        return False, "密码更改失败，无法保存配置"
    
    def get_last_login(self):
        """获取上次登录的用户名"""
        config = self.load_global_config()
        return config.get("last_login")
    
    def set_last_login(self, username):
        """设置最后登录的用户名"""
        config = self.load_global_config()
        config["last_login"] = username
        self.save_global_config(config)