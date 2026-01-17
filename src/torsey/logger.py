import sys


def useColor() -> bool:
    return sys.stdout.isatty()


def error(message: str):
    if useColor():
        print(f"[\033[31mERROR\033[0m] {message}")
    else:
        print(f"[ERROR] {message}")


def info(message: str):
    if useColor():
        print(f"[\033[34mINFO\033[0m] {message}")
    else:
        print(f"[INFO] {message}")
