"""
Mock 规则存储模块
使用 JSON 文件持久化存储
"""
import json
import os
from typing import Optional
from pydantic import BaseModel

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "mock_rules.json")


class MockRule(BaseModel):
    """Mock 规则模型"""
    id: str
    path: str
    method: str = "GET"
    description: str = ""
    response_body: dict = {}
    status_code: int = 200
    delay: float = 0  # 响应延迟（秒）


class RuleStore:
    """规则存储管理器"""

    def __init__(self):
        self.rules: dict[str, MockRule] = {}
        self._ensure_data_dir()
        self._load()

    def _ensure_data_dir(self):
        """确保数据目录存在"""
        data_dir = os.path.dirname(DATA_FILE)
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def _load(self):
        """从文件加载规则"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        rule = MockRule(**item)
                        self.rules[rule.id] = rule
            except (json.JSONDecodeError, Exception):
                self.rules = {}

    def _save(self):
        """保存规则到文件"""
        data = [rule.model_dump() for rule in self.rules.values()]
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add(self, rule: MockRule) -> MockRule:
        """添加规则"""
        self.rules[rule.id] = rule
        self._save()
        return rule

    def get(self, rule_id: str) -> Optional[MockRule]:
        """获取单个规则"""
        return self.rules.get(rule_id)

    def get_all(self) -> list[MockRule]:
        """获取所有规则"""
        return list(self.rules.values())

    def update(self, rule_id: str, rule: MockRule) -> Optional[MockRule]:
        """更新规则"""
        if rule_id in self.rules:
            rule.id = rule_id
            self.rules[rule_id] = rule
            self._save()
            return rule
        return None

    def delete(self, rule_id: str) -> bool:
        """删除规则"""
        if rule_id in self.rules:
            del self.rules[rule_id]
            self._save()
            return True
        return False

    def match(self, path: str, method: str) -> Optional[MockRule]:
        """匹配规则"""
        for rule in self.rules.values():
            if rule.path == path and rule.method.upper() == method.upper():
                return rule
        return None


# 全局存储实例
rule_store = RuleStore()
