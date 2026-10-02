# parry-window

弹反：多来源台账、窗口状态机、单次消耗、冷却与返还，只用 Python 标准库。

```
python3 -m parry.cli --sample edge
python3 -m parry.cli --sample double
python3 -m parry.cli --sample cooldown
python3 -m parry.cli --sample refund
python3 -m parry.cli --sample sources
python3 -m parry.cli --sample refresh
python3 -m parry.cli --sample work
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **多来源台账**：每个来源（`source`）各自维护窗口、消耗标记与冷却；
  一个来源的弹反结果不改动另一个来源的任何状态。
- **窗口**：`press` 打开 `window_ms` 的窗口，时间落在 `[now, now + window_ms]`
  之内都算有效（正好等于窗口时长的那一帧仍有效）；窗口开启期间再次 `press`
  返回 False 且不刷新窗口。
- **单次消耗**：一个窗口只能成功弹反一次；成功后立刻结束窗口并进入
  `cooldown_ms` 冷却。
- **落空**：窗口过期后第一次受到攻击按全额承受，并进入 `cooldown_ms` 冷却。
- **冷却**：冷却期内 `press` 返回 False，也不改变窗口状态。
- **返还**：成功弹反时承受 0 伤害，返还 `damage * refund_pct // 100`。
- **幂等**：同一个 `event_id` 的受击只结算一次，重复传入返回上次的
  `(承受, 返还)` 结果。
- **代价**：每次受击 O(1)，`work_count` 不随历史受击数线性增长。
- **规模**：10 万次受击单遍处理，内存 O(来源数 + 未结算窗口数)。

## 输出契约（不改格式）

```
taken=..
second_taken=..
press=..
refund=..
gear_taken=..
late_taken=..
work=..
```

## 目录

```
parry/core.py   多来源台账、窗口、冷却与返还
parry/cli.py    命令行入口
tests/          unittest 用例
```
