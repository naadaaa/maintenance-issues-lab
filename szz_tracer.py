import argparse
import json
import re
import subprocess
import sys
from collections import Counter

from pydriller import Repository

COMMENT_RE = re.compile(r"^\s*(//|#|/\*|\*|<!--|-->|\*/)")


def is_meaningful(text: str) -> bool:
    s = text.strip()
    return bool(s) and not COMMENT_RE.match(s)


def extract_deleted_lines(repo_path, bfc_hash):
    result, added = {}, 0
    commit = None
    for commit in Repository(repo_path, single=bfc_hash).traverse_commits():
        for mod in commit.modified_files:
            added += mod.added_lines
            if mod.old_path is None:
                continue
            parsed = mod.diff_parsed
            lines = [(n, t) for n, t in parsed["deleted"] if is_meaningful(t)]
            if lines:
                result[mod.old_path] = lines
    return commit, result, added


_CACHE = {}


def blame_file(repo_path, parent, path, copy_detect=False):
    key = (parent, path, copy_detect)
    if key in _CACHE:
        return _CACHE[key]
    cmd = ["git", "-C", repo_path, "blame", "--porcelain"]
    if copy_detect:
        cmd += ["-C", "-C"]
    cmd += [parent, "--", path]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True).stdout
    result, meta, cur = {}, {}, None
    for line in out.splitlines():
        m = re.match(r"^([0-9a-f]{40}) (\d+) (\d+)", line)
        if m:
            cur = (m.group(1), int(m.group(2)), int(m.group(3)))
        elif line.startswith("filename "):
            meta[cur[0]] = line[9:]
        elif line.startswith("\t"):
            h, orig_line, final_line = cur
            result[final_line] = (h[:7], meta.get(h, path), orig_line)
    _CACHE[key] = result
    return result


def blame_line(repo_path, parent, path, line_no, copy_detect=False):
    return blame_file(repo_path, parent, path, copy_detect)[line_no]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("bfc")
    ap.add_argument("--out", default="szz_results.json")
    a = ap.parse_args()

    commit, deleted, added = extract_deleted_lines(a.repo, a.bfc)
    if commit is None:
        sys.exit(f"Commit {a.bfc} not found in {a.repo}")
    if not commit.parents:
        sys.exit("BFC has no parent (root commit) - cannot blame.")
    parent = commit.parents[0]
    print(f"BFC: {commit.hash[:7]}  {commit.msg.splitlines()[0]}")
    print(f"Parent: {parent[:7]}\n")

    if not deleted:
        print("GHOST COMMIT: the fix only ADDED code "
              f"({added} added lines, 0 deleted/modified).")
        print("Deleted-line SZZ has nothing to trace. Inspect issue history,")
        print("surrounding code and semantics instead.")
        json.dump({"bfc": commit.hash, "ghost": True, "added_lines": added},
                  open(a.out, "w"), indent=2)
        return

    rows = []
    for path, lines in deleted.items():
        for n, text in lines:
            normal = blame_line(a.repo, parent, path, n, False)
            cc = blame_line(a.repo, parent, path, n, True)
            rows.append({"file": path, "line": n, "text": text.strip(),
                         "normal_bic": normal[0], "cc_bic": cc[0],
                         "cc_origin_file": cc[1], "cc_origin_line": cc[2]})

    print("| File | Line | Code | git blame | blame -C -C | Origin (-C -C) |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        code = r["text"][:40].replace("|", "\\|")
        print(f"| {r['file']} | {r['line']} | `{code}` | {r['normal_bic']} "
              f"| {r['cc_bic']} | {r['cc_origin_file']}:{r['cc_origin_line']} |")

    votes = Counter(r["normal_bic"] for r in rows)
    top, cnt = votes.most_common(1)[0]
    print(f"\nScript BIC (normal blame, most-blamed): {top} ({cnt}/{len(rows)} lines)")
    diffs = [r for r in rows if r["normal_bic"] != r["cc_bic"]]
    print(f"Lines where -C -C differs from normal blame: {len(diffs)}/{len(rows)}")

    json.dump({"bfc": commit.hash, "ghost": False, "script_bic": top,
               "rows": rows}, open(a.out, "w"), indent=2)


if __name__ == "__main__":
    main()