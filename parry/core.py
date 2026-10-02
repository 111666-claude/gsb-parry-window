"""弹反：多来源台账、窗口状态机、单次消耗、冷却与返还。"""


class _SourceState:
    """单个来源的窗口与冷却状态。"""

    __slots__ = ("window_until", "cooldown_until")

    def __init__(self):
        self.window_until = None
        self.cooldown_until = None


class Parry:
    """弹反状态机。"""

    def __init__(self, window_ms, cooldown_ms, refund_pct):
        self.window_ms = window_ms
        self.cooldown_ms = cooldown_ms
        self.refund_pct = refund_pct
        self.sources = {}
        self.events = []
        self._settled = {}
        self.work = 0

    def _state(self, source):
        state = self.sources.get(source)
        if state is None:
            state = _SourceState()
            self.sources[source] = state
        return state

    def press(self, now_ms, source="default"):
        """按下某个来源的弹反键。"""
        self.work += 1
        state = self._state(source)
        if state.cooldown_until is not None:
            if now_ms < state.cooldown_until:
                return False
            state.cooldown_until = None
        if state.window_until is not None:
            if now_ms <= state.window_until:
                return False
            state.window_until = None
        state.window_until = now_ms + self.window_ms
        return True

    def active(self, now_ms, source="default"):
        """当前是否在弹反窗口内。"""
        state = self.sources.get(source)
        if state is None or state.window_until is None:
            return False
        return now_ms <= state.window_until

    def incoming(self, damage, now_ms, source="default", event_id=None):
        """承受一次攻击，返回 (实际承受, 返还伤害)。"""
        self.work += 1
        self.events.append((event_id, source, now_ms, damage))
        if event_id is not None and event_id in self._settled:
            return self._settled[event_id]
        state = self.sources.get(source)
        result = self._resolve(state, damage, now_ms)
        if event_id is not None:
            self._settled[event_id] = result
        return result

    def _resolve(self, state, damage, now_ms):
        if state is None or state.window_until is None:
            return damage, 0
        window_end = state.window_until
        state.window_until = None
        state.cooldown_until = now_ms + self.cooldown_ms
        if now_ms <= window_end:
            return 0, damage * self.refund_pct // 100
        return damage, 0

    def work_count(self):
        return self.work
