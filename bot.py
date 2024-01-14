#!/usr/bin/env python3

from __future__ import print_function
import os
import queue
import sys
import traceback
import time


class Bot:
    def __init__(self):
        self.conns = {}
        self.persist_dir = os.path.abspath("persist")
        if not os.path.exists(self.persist_dir):
            os.mkdir(self.persist_dir)


bot = Bot()


def main():
    sys.path += ["plugins"]  # so 'import hook' works without duplication
    sys.path += ["lib"]
    os.chdir(
        os.path.dirname(__file__) or "."
    )  # do stuff relative to the install directory

    print("Loading plugins")

    # bootstrap the reloader
    eval(
        compile(
            open(os.path.join("core", "reload.py"), "r").read(),
            os.path.join("core", "reload.py"),
            "exec",
        ),
        globals(),
    )
    reload(init=True)

    print("Connecting to IRC")

    try:
        config()
        if not hasattr(bot, "config"):
            exit()
    except Exception as e:
        print("ERROR: malformed config file:", e)
        traceback.print_exc()
        sys.exit()

    print("Running main loop")

    while True:
        reload()  # these functions only do things
        config()  # if changes have occurred

        for conn in bot.conns.values():
            try:
                out = conn.out.get_nowait()
                main(conn, out)
            except queue.Empty:
                pass
        while all(conn.out.empty() for conn in iter(bot.conns.values())):
            time.sleep(0.1)


if __name__ == "__main__":
    main()
