import random
import json
import asyncio
import threading
from datetime import datetime, date
from pathlib import Path
from typing import Dict, List, Any

# 严格遵循旧版API导入方式
from astrbot.api.event import filter as event_filter
from astrbot.api.event import AstrMessageEvent
from astrbot.api.star import Context, Star, register

# 签文数据模块（需另外创建）
from .sensoji_data import sensoji_results

# ====================== 配置模块 ======================
DATA_DIR = Path(__file__).parent / "sensoji_data"
DAILY_STATUS_FILE = DATA_DIR / "user_daily_status.json"
data_lock = threading.Lock()

# ====================== 数据存储模块 ======================
class DataManager:
    @staticmethod
    def _ensure_dir():
        """确保数据目录存在"""
        DATA_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_daily_log_path() -> Path:
        """生成当日日志文件路径"""
        return DATA_DIR / f"{date.today().strftime('%Y.%m.%d')}-sensoji_data.json"

    @staticmethod
    def load_daily_status() -> Dict[str, Any]:
        """加载每日状态数据（兼容旧版JSON解析）"""
        DataManager._ensure_dir()
        with data_lock:
            try:
                if DAILY_STATUS_FILE.exists():
                    with open(DAILY_STATUS_FILE, "r", encoding="utf-8") as f:
                        return json.load(f)
                return {}
            except Exception as e:
                print(f"[Data Error] 状态加载失败: {e}")
                return {}

    @staticmethod
    def save_daily_status(data: Dict[str, Any]):
        """保存数据（线程安全写入）"""
        DataManager._ensure_dir()
        with data_lock:
            try:
                temp_file = DAILY_STATUS_FILE.with_suffix(".tmp")
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                temp_file.replace(DAILY_STATUS_FILE)
            except Exception as e:
                print(f"[Data Error] 状态保存失败: {e}")

# ====================== 核心插件类 ======================
@register("astrbot_plugin_WZL_SensojiPlus", "WZL", "WZL_SensojiPlus浅草寺抽签Plus", "1.2.4", "https://github.com/WZL0813/astrbot_plugin_WZL_SensojiPlus")
class SensojiPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        print("[WZL_SensojiPlus Plugin Init] WZL_SensojiPlus浅草寺抽签Plus插件初始化成功")

    def _create_log_record(self, user_id: str, result_type: str, result_data: Dict) -> Dict:
        """创建标准化日志记录（兼容旧版时间格式）"""
        return {
            "user_id": user_id,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": str(date.today()),
            "result_type": result_type,
            "result_data": result_data
        }

    def _format_result(self, result_data: Dict) -> str:
        """严格兼容的消息格式化"""
        details = []
        for item in result_data["horoscope_details"].split("。"):
            if item.strip():
                details.append(f"· {item.strip()}")
        
        components = [
            "🎋 浅草寺灵签 🎋",
            f"〖{result_data['result']}〗",
            "",
            f"📜 诗文：{result_data['poetry']}",
            "",
            f"🔍 解析：{result_data['interpretation']}",
            "",
            f"💡 建议：{result_data['suggestion']}",
            "",
            "✨ 运势详解：",
            *details,
            "",
            "────────────",
            f"※ 签文时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ※"
        ]
        return "\n".join([c for c in components if c])

    def _get_daily_result(self, user_id: str) -> Dict:
        """每日签文逻辑（带数据过期间隔）"""
        today = str(date.today())
        status_data = DataManager.load_daily_status()
        
        # 清理过期数据
        if user_id in status_data and status_data[user_id]["date"] != today:
            del status_data[user_id]
            DataManager.save_daily_status(status_data)
        
        # 生成新签文
        if user_id not in status_data:
            selected = random.choice(sensoji_results)
            status_data[user_id] = {
                "date": today,
                "result": selected,
                "is_changed": False
            }
            DataManager.save_daily_status(status_data)
        
        return status_data[user_id]["result"]

    def _get_change_result(self, user_id: str) -> Dict:
        """转运签逻辑（强制刷新）"""
        selected = random.choice(sensoji_results)
        status_data = DataManager.load_daily_status()
        status_data[user_id] = {
            "date": str(date.today()),
            "result": selected,
            "is_changed": True
        }
        DataManager.save_daily_status(status_data)
        return selected

# ====================== 命令处理模块 ======================
    @event_filter.command("抽签")
    async def select_fortune(self, event: AstrMessageEvent):
        """每日签文命令（带基础频率限制）"""
        try:
            user_id = event.get_sender_id()
            raw_data = self._get_daily_result(user_id)
            formatted = self._format_result(raw_data)
            yield event.plain_result(formatted)
        except Exception as e:
            print(f"[Command Error] 抽签失败: {str(e)}")
            yield event.plain_result("🔯 签筒暂时无法使用，请稍后再试")

    @event_filter.command("转运")
    async def change_fortune(self, event: AstrMessageEvent):
        """转运签命令（每日限制次数）"""
        try:
            user_id = event.get_sender_id()
            raw_data = self._get_change_result(user_id)
            formatted = self._format_result(raw_data).replace("〖", "〖转运·")
            yield event.plain_result(f"🔄 运势已刷新 🔄\n{formatted}")
        except Exception as e:
            print(f"[Command Error] 转运失败: {str(e)}")
            yield event.plain_result("🌀 能量不足无法转运")

    @event_filter.command("解签")
    async def explain_fortune(self, event: AstrMessageEvent):
        """智能解签（兼容旧版LLM接口）"""
        try:
            user_id = event.get_sender_id()
            status_data = DataManager.load_daily_status()
            
            if user_id not in status_data:
                yield event.plain_result("❌ 请先使用「抽签」获取签文")
                return
                
            current_sign = status_data[user_id]["result"]
            response = await self.context.get_using_provider().text_chat(
                prompt=f"解释签文：{current_sign['poetry']}",
                contexts=[],
                image_urls=[],
                system_prompt="你是一位解签大师，用通俗易懂的方式解释签文含义"
            )
            
            explanation = (
                "📖 智能解签结果 📖\n"
                f"〖{current_sign['result']}〗\n\n"
                f"{response.completion_text}\n\n"
                "────────────\n"
                "※ 本解签结果由AI生成，仅供参考"
            )
            yield event.plain_result(explanation)
        except Exception as e:
            print(f"[Command Error] 解签失败: {str(e)}")
            yield event.plain_result("🔮 解签服务暂时不可用")

    async def terminate(self):
        """插件卸载清理"""
        print("[WZL_SensojiPlus Plugin Exit] WZL_SensojiPlus浅草寺抽签Plus插件已卸载")