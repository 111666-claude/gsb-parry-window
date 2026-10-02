"""弹反：多来源台账、窗口状态机、单次消耗、冷却与返还。

缺陷：窗口边界用严格小于、一次窗口能无限弹反、冷却不生效、返还整除顺序算错、
所有来源共用一份窗口与冷却、窗口能被重复按键刷新、每次受击都重扫全部历史。
"""


class Parry:
    """弹反状态机。"""

    def __init__(self, window_ms, cooldown_ms, refund_pct):
        self.window_ms = window_ms
        self.cooldown_ms = cooldown_ms
        self.refund_pct = refund_pct
        self.window_until = None
        self.ready_at = None
        self.used = False
        self.sources = {}
        self.events = []
        self.work = 0

    def press(self, now_ms, source="default"):
        """按下某个来源的弹反键。"""
        self.work += 1
        self.sources[source] = True
        self.window_until = now_ms + self.window_ms
        self.used = False
        return True

    def active(self, now_ms, source="default"):
        """当前是否在弹反窗口内。"""
        if self.window_until is None:
            return False
        return now_ms < self.window_until

    def incoming(self, damage, now_ms, source="default", event_id=None):
        """承受一次攻击，返回 (实际承受, 返还伤害)。"""
        self.work += len(self.events)
        self.events.append((event_id, source, now_ms, damage))
        if not self.active(now_ms, source):
            return damage, 0
        if self.used:
            return damage, 0
        refund = damage // 100 * self.refund_pct
        return 0, refund

    def work_count(self):
        return self.work
