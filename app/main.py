from __future__ import annotations

import argparse
import time

from app.config import load_config
from app.logger import setup_logger
from app.pipeline import run_once


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    args = parser.parse_args()

    cfg = load_config()
    setup_logger(cfg.log_level)

    if args.once:
        run_once(cfg)
        return

    while True:
        run_once(cfg)
        time.sleep(cfg.poll_interval_seconds)


if __name__ == "__main__":
    main()
