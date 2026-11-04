#!/usr/bin/env python3
"""AGQ overflow probe runner (grid 71ec4ccc, Max 18:4x). Stdlib only.

Runs probe/test_probe.py, writes out/junit.xml and out/evidence.json, prints the environment it saw
(cpu, memory limit), and ends with one closing line:
  ovf-evidence: result=<pass|failure|error> sha=<sha> tests=<n> failures=<f> rc=<rc>
The sha is `git rev-parse HEAD` when a .git is present, else $PROBE_SHA. Without either, result=error.
"""
import json
import os
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET


def source_sha():
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=30)
        if r.returncode == 0 and len(r.stdout.strip()) == 40:
            return r.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return os.environ.get("PROBE_SHA", "")


def mem_limit():
    for p in ("/sys/fs/cgroup/memory.max", "/sys/fs/cgroup/memory/memory.limit_in_bytes"):
        try:
            return open(p).read().strip()
        except OSError:
            continue
    return "unknown"


def _ids(s):
    for x in s:
        if isinstance(x, unittest.TestSuite):
            yield from _ids(x)
        else:
            yield x.id()


def main():
    os.makedirs("out", exist_ok=True)
    print("probe env: python %s cpu_count %s mem_limit %s" % (sys.version.split()[0], os.cpu_count(), mem_limit()))
    suite = unittest.defaultTestLoader.discover("probe", pattern="test_*.py")
    ids = sorted(_ids(suite))
    res = unittest.TextTestRunner(verbosity=2, stream=sys.stdout).run(suite)
    n, f, e = res.testsRun, len(res.failures), len(res.errors)
    ts = ET.Element("testsuites")
    su = ET.SubElement(ts, "testsuite", name="agq-probe", tests=str(n), failures=str(f), errors=str(e), skipped="0")
    bad = {t.id(): "failure" for t, _ in res.failures}
    bad.update({t.id(): "error" for t, _ in res.errors})
    sha = source_sha()
    ET.SubElement(ET.SubElement(su, "properties"), "property", name="ovf.sha", value=sha)
    for t in ids:
        tc = ET.SubElement(su, "testcase", classname="agq-probe", name=t)
        if t in bad:
            ET.SubElement(tc, bad[t])
    ET.ElementTree(ts).write("out/junit.xml", encoding="utf-8", xml_declaration=True)
    rc = 0 if (n > 0 and f == 0 and e == 0) else 1
    result = "error" if (not sha or n == 0 or e) else ("pass" if rc == 0 else "failure")
    with open("out/evidence.json", "w") as fh:
        json.dump({"v": 1, "kind": "tests", "count": n, "failures": f, "errors": e, "sha": sha, "rc": rc}, fh)
    print("ovf-evidence: result=%s sha=%s tests=%d failures=%d rc=%d" % (result, sha or "none", n, f + e, rc))
    return 0 if result == "pass" else 1


if __name__ == "__main__":
    sys.exit(main())
