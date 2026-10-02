"""命令行入口：跑弹反样例。"""

import argparse

from .core import Parry


def build_parser():
    parser = argparse.ArgumentParser(prog="parry-window", description="弹反窗口")
    parser.add_argument("--sample", default="edge",
                        help="edge / double / cooldown / refund")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    if args.sample == "edge":
        parry = Parry(window_ms=200, cooldown_ms=1000, refund_pct=30)
        parry.press(0)
        taken, _ = parry.incoming(100, 200)
        print("taken=%d" % taken)
    elif args.sample == "double":
        parry = Parry(window_ms=200, cooldown_ms=1000, refund_pct=30)
        parry.press(0)
        parry.incoming(100, 50)
        taken, _ = parry.incoming(100, 100)
        print("second_taken=%d" % taken)
    elif args.sample == "cooldown":
        parry = Parry(window_ms=200, cooldown_ms=1000, refund_pct=30)
        parry.press(0)
        parry.incoming(100, 50)
        ok = parry.press(60)
        print("press=%s" % str(ok).lower())
    elif args.sample == "refund":
        parry = Parry(window_ms=200, cooldown_ms=1000, refund_pct=30)
        parry.press(0)
        _, refund = parry.incoming(250, 50)
        print("refund=%d" % refund)
    else:
        raise SystemExit("需要 --sample edge|double|cooldown|refund")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
