# parry-window

弹反：窗口判定、单次消耗、冷却与伤害返还，只用 Python 标准库。

```
python3 -m parry.cli --sample edge
python3 -m parry.cli --sample double
python3 -m parry.cli --sample cooldown
python3 -m parry.cli --sample refund
python3 -m unittest discover -s tests -v
```

## 口径（README 为准）

- **窗口**：按下后 `window_ms` 内有效，正好等于窗口时长的那一帧仍然算有效；
  窗口外受到攻击按全额承受。
- **单次消耗**：一个窗口只能成功弹反一次，第二次攻击按全额承受。
- **返还**：成功弹反时承受 0 伤害，并返还 `damage * refund_pct // 100`。
- **冷却**：成功弹反后进入 `cooldown_ms`，冷却期内按弹反键返回 False；
  窗口落空同样进入冷却。
- **不变量**：同一串按键与受击序列重复执行结果相同；`incoming` 返回的两个数
  非负，弹反成功时承受为 0。
- **规模**：每次受击 O(1)，10 万次受击单遍处理，内存 O(1)。

## 输出契约（不改格式）

```
taken=..
second_taken=..
press=..
refund=..
```

## 目录

```
parry/core.py   窗口、消耗、冷却与返还
parry/cli.py    命令行入口
tests/          unittest 用例
```
