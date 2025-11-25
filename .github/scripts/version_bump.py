#!/usr/bin/env python3
import argparse, pathlib, re, sys, datetime

def bump(v, level):
    major, minor, patch = map(int, v.strip().split("."))
    if level == "major":
        return f"{major+1}.0.0"
    if level == "minor":
        return f"{major}.{minor+1}.0"
    return f"{major}.{minor}.{patch+1}"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", choices=["major","minor","patch"], default="patch")
    ap.add_argument("--file", default="swarm/VERSION")
    ap.add_argument("--changelog", default="swarm/CHANGELOG.md")
    args = ap.parse_args()

    vf = pathlib.Path(args.file)
    if not vf.exists(): print("VERSION file missing", file=sys.stderr); sys.exit(2)
    cur = vf.read_text(encoding="utf-8").strip()
    new = bump(cur, args.level)
    vf.write_text(new + "\n", encoding="utf-8")

    ch = pathlib.Path(args.changelog)
    if ch.exists():
        s = ch.read_text(encoding="utf-8")
        today = datetime.date.today().isoformat()
        header = f"## [{new}] - {today}"
        if header not in s:
            s = s.replace("## [Unreleased]", f"## [Unreleased]\n\n{header}\n### Changed\n- Bump version to {new}\n")
            ch.write_text(s, encoding="utf-8")
    print(new)

if __name__ == "__main__":
    main()
