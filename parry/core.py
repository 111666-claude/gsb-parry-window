"""弹反：窗口判定、单次消耗、冷却与伤害返还。

缺陷：窗口边界用严格小于、一次窗口能无限弹反、冷却不生效、
返还比例的整除顺序算错。
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
        self.work = 0

    def press(self, now_ms):
        """按下弹反键。"""
        self.work += 1
        self.window_until = now_ms + self.window_ms
        self.used = False
        return True

    def active(self, now_ms):
        """当前是否在弹反窗口内。"""
        if self.window_until is None:
            return False
        return now_ms < self.window_until

    def incoming(self, damage, now_ms):
        """承受一次攻击，返回 (实际承受, 返还伤害)。"""
        if not self.active(now_ms):
            return damage, 0
        if self.used:
            return damage, 0
        refund = damage // 100 * self.refund_pct
        return 0, refund

    def work_count(self):
        return self.work
