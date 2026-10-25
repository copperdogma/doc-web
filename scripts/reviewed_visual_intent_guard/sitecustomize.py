"""Fail-closed Python process-tree guard for the opt-in offline crop replay.

No SDK shim or model response is installed. This is a scoped test boundary,
not an operating-system sandbox for arbitrary native code.
"""
import json
import hashlib
import os
from pathlib import Path
import sys
import traceback
import socket


def record(event, **details):
    with open(os.environ["REVIEWED_REPLAY_AUDIT"], "a", encoding="utf-8") as out:
        out.write(json.dumps({"event": event, "pid": os.getpid(), **details}) + "\n")


def audit(event, args):
    if event == "socket.bind" and args[1] == ("::1", 0):
        caller = sys._getframe(1)
        source = os.environ["REVIEWED_REPLAY_PROBE_SOURCE"]
        if (caller.f_code.co_name == "_has_ipv6"
                and Path(caller.f_code.co_filename).resolve() == Path(source).resolve()
                and caller.f_locals.get("host") == "::1"
                and hashlib.sha256(Path(source).read_bytes()).hexdigest()
                == os.environ["REVIEWED_REPLAY_PROBE_SHA256"]):
            record("blocked-local-capability-probe", address="::1", port=0,
                   source=source, source_sha256=os.environ["REVIEWED_REPLAY_PROBE_SHA256"])
            raise RuntimeError("Offline urllib3 IPv6 capability probe blocked")
    if event in {"socket.connect", "socket.getaddrinfo", "socket.sendto",
                 "socket.sendmsg", "socket.bind"}:
        record("denied", operation=event, stack=traceback.format_stack(limit=9))
        raise RuntimeError("Reviewed replay forbids network operations")
    if event == "open" and isinstance(args[0], (str, bytes, os.PathLike)):
        name = os.fsdecode(args[0])
        if (Path(name).name == ".env" or Path(name).name.startswith(".env.")
                or Path(name).suffix == ".env"):
            record("denied", operation="environment-file-read")
            raise RuntimeError("Reviewed replay forbids environment files")
    if event in {"os.system", "os.exec", "os.posix_spawn", "os.posix_spawnp"}:
        record("denied", operation=event)
        raise RuntimeError("Reviewed replay forbids unguarded process execution")
    if event == "subprocess.Popen":
        executable, argv, _, env = args
        inherited = os.environ if env is None else env
        if (Path(executable).resolve() != Path(sys.executable).resolve()
                or any(arg in {"-E", "-I", "-S"} for arg in argv)
                or inherited.get("REVIEWED_REPLAY_AUDIT") != os.environ["REVIEWED_REPLAY_AUDIT"]
                or inherited.get("PYTHONPATH") != os.environ["PYTHONPATH"]):
            record("denied", operation="unguarded-subprocess")
            raise RuntimeError("Reviewed replay child must inherit the Python guard")
        record("python-child", entrypoint=str(argv[1]))


if "REVIEWED_REPLAY_AUDIT" not in os.environ:
    os._exit(78)  # A sitecustomize exception alone would let Python continue.
sys.addaudithook(audit)
def deny_listener(*args, **kwargs):
    record("denied", operation="socket-listen-or-accept")
    raise RuntimeError("Reviewed replay forbids listening or accepting sockets")


socket.socket.listen = deny_listener
socket.socket.accept = deny_listener
try:
    record("guard-installed", interpreter=sys.executable)
except Exception:
    os._exit(78)
