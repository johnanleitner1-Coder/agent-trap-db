#!/usr/bin/env python3
"""
agent-trap preflight — a free, zero-dependency check an autonomous agent runs
BEFORE spending effort on any GitHub bounty/task repo.

It answers one question a human asks instinctively but an agent often does not:
"Is this 'paid bounty' actually a trap built to harvest my labor?"

It combines (a) a known-trap list (traps.json, first-hand verified) with
(b) genre-level heuristics that catch re-skinned traps the static list misses.

Usage:
    python preflight.py https://github.com/<owner>/<repo>
    python preflight.py <owner>/<repo>

Exit code 0 = looks ok / unknown, 2 = TRAP signals found (so `&& do_work` is safe in a shell).
Network: read-only GitHub API + raw file fetch. No auth required for public repos.
"""
import json, sys, os, re, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
GH_API = "https://api.github.com"
RAW = "https://raw.githubusercontent.com"
UA = {"User-Agent": "agent-trap-preflight/0.2"}

def _get(url, raw=False):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as r:
            body = r.read().decode("utf-8", "replace")
            return body if raw else json.loads(body)
    except urllib.error.HTTPError as e:
        return None
    except Exception:
        return None

def load_known():
    try:
        with open(os.path.join(HERE, "traps.json"), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"entries": [], "threat_cluster": {}, "excluded_entries": []}

def parse_repo(arg):
    m = re.search(r"github\.com[:/]+([^/\s]+)/([^/\s#?]+)", arg)
    if m:
        return m.group(1), m.group(2).removesuffix(".git")
    if "/" in arg and " " not in arg:
        o, r = arg.split("/", 1)
        return o, r.split("/")[0]
    return None, None

def check(owner, repo):
    findings = []   # (heuristic_id, weight, detail)
    full = f"{owner}/{repo}"

    # 0) known-trap list (first-hand verified)
    known = load_known()
    for e in known.get("entries", []):
        if e.get("target", "").lower().endswith(full.lower()):
            findings.append(("KNOWN", "decisive",
                f"On the first-hand-verified trap list: {e['type']} (severity {e.get('severity')}). {e['mechanism'][:160]}"))
    cluster = known.get("threat_cluster", {})
    for m in cluster.get("members", []):
        if m.lower().endswith(full.lower()):
            findings.append(("H6", "high",
                f"Member of known shared-operator cluster '{cluster.get('id')}': re-skinned harvest template."))

    meta = _get(f"{GH_API}/repos/{full}")
    if meta is None:
        return {"target": full, "verdict": "UNKNOWN", "reason": "repo not found or API unreachable", "findings": findings}

    desc = (meta.get("description") or "")
    open_issues = meta.get("open_issues_count", 0)
    forks = meta.get("forks_count", 0)

    # H4 self-described fixture
    if re.search(r"\b(sandbox|test fixture|live[- ]?fire|fixture for testing)\b", desc, re.I):
        findings.append(("H4", "decisive", f"Description self-describes as a fixture/sandbox: '{desc[:120]}'"))

    # org age + thin history (H2)
    owner_meta = _get(f"{GH_API}/users/{owner}")
    if owner_meta:
        created = owner_meta.get("created_at", "")
        repos = owner_meta.get("public_repos", 99)
        if created >= "2026-04" and repos <= 6:
            findings.append(("H2", "high",
                f"Throwaway-style identity: created {created[:10]}, only {repos} public repos."))
        if re.search(r"(labs|hunter|playground|livefire)$", owner, re.I):
            findings.append(("H2", "medium", f"Owner name matches trap-genre pattern: '{owner}'."))

    # H5 name/content mismatch + H3 merge-gated + H1 injection: read README + CONTRIBUTING
    blob = ""
    for branch in ("main", "master"):
        for fn in ("README.md", "CONTRIBUTING.md"):
            txt = _get(f"{RAW}/{full}/{branch}/{fn}", raw=True)
            if txt and "404: Not Found" not in txt:
                blob += "\n" + txt
        if blob:
            break

    if blob:
        low = blob.lower()
        # H1 ignore-notice injection (decisive)
        if re.search(r"(automated systems?|ai agents?|bots?)[^.\n]{0,60}(ignore|disregard|skip|proceed)", low):
            findings.append(("H1", "decisive",
                "Contains an instruction telling automated systems/AI agents to IGNORE or proceed past a notice meant for humans. The human-readable notice is the truth; this override is the attack."))
        # human warning that bounties are symbolic/unpaid/research-only
        if re.search(r"(symbolic|will not be merged|research[- ]only|not the right repo|do(es)? not guarantee payment|not part of)", low):
            findings.append(("H1b", "high",
                "Contains a human-readable warning that bounties are symbolic / unpaid / research-only / not guaranteed. Believe it."))
        # H3 merge-gated payout
        if re.search(r"paid only when.*merged|bounty is paid.*merged|payout.*upon merge|paid upon merge", low):
            findings.append(("H3", "high",
                f"Payout gated behind merge, with {open_issues} open issues / {forks} forks and no verifiable payout rail."))
        # H5 name/content mismatch
        bounty_named = re.search(r"(bounty|bug-bounty|agent|playground|hunter)", repo, re.I)
        content_generic = re.search(r"(freelanceflow|taskflow|monorepo|next\.js 14|prisma schema)", low)
        if bounty_named and content_generic:
            findings.append(("H5", "high",
                f"Repo name ('{repo}') promises bounties/agent tasks but content is a generic SaaS monorepo — re-skinned harvest template."))
        # H6 shared template asset
        if "1a920eb5-e581-44ce-bcef-2ebf0566777f" in blob:
            findings.append(("H6", "high",
                "Embeds the known shared-operator template image asset (1a920eb5-...). Same operator as a known trap repo."))
        # H7 impossible / trivial high payout
        if re.search(r"exact value of pi|compute .*\bpi\b exactly|pixel art.*creative", low):
            findings.append(("H7", "high", "Impossible or trivial task attached to a high payout."))

    # decide verdict
    weights = [f[1] for f in findings]
    if "decisive" in weights or "KNOWN" in [f[0] for f in findings]:
        verdict = "TRAP"
    elif weights.count("high") >= 2:
        verdict = "TRAP"
    elif "high" in weights:
        verdict = "SUSPICIOUS"
    else:
        verdict = "NO_KNOWN_SIGNALS"

    return {"target": full, "verdict": verdict,
            "open_issues": open_issues, "forks": forks,
            "findings": [{"heuristic": h, "weight": w, "detail": d} for (h, w, d) in findings]}

def main():
    if len(sys.argv) < 2:
        print("usage: python preflight.py <github repo url or owner/repo>", file=sys.stderr)
        sys.exit(64)
    owner, repo = parse_repo(sys.argv[1])
    if not owner:
        print("could not parse a github owner/repo from:", sys.argv[1], file=sys.stderr)
        sys.exit(64)
    result = check(owner, repo)
    print(json.dumps(result, indent=2))
    sys.exit(2 if result["verdict"] in ("TRAP", "SUSPICIOUS") else 0)

if __name__ == "__main__":
    main()
