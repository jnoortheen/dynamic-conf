"""Configuration file for sniffer."""

import time
import subprocess

from sniffer.api import select_runnable, file_validator, runnable

try:
    from pync import Notifier
except ImportError:
    notify = None
else:
    notify = Notifier.notify


watch_paths = ["dynamic_conf", "tests"]


class Options:
    group = int(time.time())  # unique per run
    show_coverage = False
    rerun_args = None

    targets = [
        (("pytest", "-x", "--cov", "dynamic_conf"), "Unit Tests", True),
    ]


@select_runnable("run_targets")
@file_validator
def python_files(filename):
    return filename.endswith(".py") and ".py." not in filename


@select_runnable("run_targets")
@file_validator
def html_files(filename):
    return filename.split(".")[-1] in ["html", "css", "js"]


@runnable
def run_targets(*_):
    """Run targets for Python."""
    count = 0
    for count, (command, title, retry) in enumerate(Options.targets, start=1):
        success = call(command, title, retry)
        if not success:
            message = "✅ " * (count - 1) + "❌"
            show_notification(message, title)

            return False

    message = "✅ " * count
    title = "All Targets"
    show_notification(message, title)

    return True


def call(command, title, retry):
    """Run a command-line program and display the result."""
    if Options.rerun_args:
        command, title, retry = Options.rerun_args
        Options.rerun_args = None
        success = call(command, title, retry)
        if not success:
            return False

    print("")
    print("$ %s" % " ".join(command))
    failure = subprocess.call(command)

    if failure and retry:
        Options.rerun_args = command, title, retry

    return not failure


def show_notification(message, title):
    """Show a user notification."""
    if notify and title:
        notify(message, title=title, group=Options.group)
