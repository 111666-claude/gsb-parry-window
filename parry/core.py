"""弹反：多来源台账、窗口状态机、单次消耗、冷却与返还。

每个来源独立维护窗口与冷却；窗口为闭区间 [now, now + window_ms]；
窗口开启期间重复按键不刷新；一个窗口只生效一次，成功或落空后进入冷却；
同一 event_id 的受击只结算一次；每次受击摊还 O(1)。
"""


class _SourceState:
    """单个来源的窗口与冷却状态。"""

    __slots__ = ("window_until", "ready_at")

    def __init__(self):
        self.window_until = None
        self.ready_at = None


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

    def _window_open(self, state, now_ms):
        return state.window_until is not None and now_ms <= state.window_until

    def _in_cooldown(self, state, now_ms):
        return state.ready_at is not None and now_ms < state.ready_at

    def press(self, now_ms, source="default"):
        """按下某个来源的弹反键。"""
        self.work += 1
        state = self._state(source)
        if self._in_cooldown(state, now_ms):
            return False
        if self._window_open(state, now_ms):
            return False
        state.window_until = now_ms + self.window_ms
        return True

    def active(self, now_ms, source="default"):
        """当前是否在弹反窗口内。"""
        state = self.sources.get(source)
        if state is None:
            return False
        return self._window_open(state, now_ms)

    def incoming(self, damage, now_ms, source="default", event_id=None):
        """承受一次攻击，返回 (实际承受, 返还伤害)。"""
        self.work += 1
        if event_id is not None and event_id in self._settled:
            return self._settled[event_id]
        state = self._state(source)
        if self._window_open(state, now_ms):
            taken, refund = 0, damage * self.refund_pct // 100
            state.window_until = None
            state.ready_at = now_ms + self.cooldown_ms
        else:
            taken, refund = damage, 0
            if state.window_until is not None:
                state.window_until = None
                state.ready_at = now_ms + self.cooldown_ms
        self.events.append((event_id, source, now_ms, damage))
        if event_id is not None:
            self._settled[event_id] = (taken, refund)
        return taken, refund

    def work_count(self):
        return self.work
