"""快捷话术管理"""
import json
import os
from typing import List, Dict


class QuickReplyGroup:
    def __init__(self, name: str, replies: List[str] = None):
        self.name = name
        self.replies: List[str] = replies or []

    def to_dict(self):
        return {"name": self.name, "replies": self.replies}

    @classmethod
    def from_dict(cls, d: dict):
        return cls(d["name"], d.get("replies", []))


class QuickReplyManager:
    def __init__(self, save_path: str = "quick_replies.json"):
        self._path = save_path
        self._groups: List[QuickReplyGroup] = []
        self.load()

    def load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._groups = [QuickReplyGroup.from_dict(g) for g in data]
            except Exception:
                self._groups = []
        else:
            self._groups = [
                QuickReplyGroup("常用回复", ["您好，感谢关注！", "稍等，马上为您处理。", "感谢您的购买，祝您使用愉快！"]),
                QuickReplyGroup("促销话术", ["今天活动最后一天！", "限时优惠，先到先得！"]),
            ]
            self.save()

    def save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump([g.to_dict() for g in self._groups], f, ensure_ascii=False, indent=2)

    def get_groups(self) -> List[QuickReplyGroup]:
        return self._groups

    def add_group(self, name: str) -> QuickReplyGroup:
        g = QuickReplyGroup(name)
        self._groups.append(g)
        self.save()
        return g

    def remove_group(self, name: str):
        self._groups = [g for g in self._groups if g.name != name]
        self.save()

    def add_reply(self, group_name: str, text: str):
        for g in self._groups:
            if g.name == group_name:
                g.replies.append(text)
                self.save()
                return

    def remove_reply(self, group_name: str, text: str):
        for g in self._groups:
            if g.name == group_name:
                g.replies = [r for r in g.replies if r != text]
                self.save()
                return

    def export_json(self, path: str):
        with open(path, "w", encoding="utf-8") as f:
            json.dump([g.to_dict() for g in self._groups], f, ensure_ascii=False, indent=2)

    def import_json(self, path: str):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self._groups = [QuickReplyGroup.from_dict(g) for g in data]
        self.save()
