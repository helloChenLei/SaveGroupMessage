import os
import json
from datetime import datetime
from plugins.plugin import Plugin

class GroupMessageLogger(Plugin):
    def __init__(self):
        super().__init__()
        # 动态设置日志文件路径
        self.log_file = os.getenv("LOG_FILE_PATH", "group_messages.json")
        # 从环境变量或配置加载管理员用户
        self.admin_users = os.getenv("ADMIN_USERS", "admin_user_1,admin_user_2").split(",")

    def _load_logs(self):
        """加载日志文件，如果不存在则创建一个空文件。"""
        try:
            if not os.path.exists(self.log_file):
                with open(self.log_file, "w") as f:
                    json.dump([], f)
            with open(self.log_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载日志失败: {e}")
            return []

    def _save_logs(self, logs):
        """保存日志到文件。"""
        try:
            with open(self.log_file, "w") as f:
                json.dump(logs, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存日志失败: {e}")

    def on_receive_message(self, message, sender, group_name):
        """处理接收到的消息。"""
        # 检查用户权限
        if sender not in self.admin_users:
            return "仅管理员可操作"  # 提示用户权限不足

        # 检查是否包含触发关键词
        if not message.startswith("问："):
            return None  # 不处理

        # 提取并记录消息内容
        content = message[2:].strip()
        log_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "group": group_name,
            "content": content
        }

        try:
            logs = self._load_logs()
            logs.append(log_entry)
            # 限制日志文件大小，最多存储1000条
            if len(logs) > 1000:
                logs = logs[-1000:]
            self._save_logs(logs)
            return "记录成功"
        except Exception as e:
            return f"记录失败：{str(e)}"

    def on_generate_response(self, message, sender, group_name):
        """该方法用于处理回复生成逻辑（如果需要）。"""
        return None  # 此插件不干预回复生成
