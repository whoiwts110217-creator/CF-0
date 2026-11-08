"""Read-only CF-0 main branch protection check; no admin token or HP access.

Run: python -m automation_200.branch_rules_audit
Exit 0 = destructive-operation baseline observed. Does not establish owner
review, pull-request approval, unattended HP operation, or writeback.
"""
import json
import sys
import urllib.error
import urllib.request

REPO = "whoiwts110217-creator/CF-0"
RULESET_ID = 26799223
URL = f"https://api.github.com/repos/{REPO}/rulesets/{RULESET_ID}"


def classify(ruleset):
    if not isinstance(ruleset, dict):
        return {"state": "invalid", "reason": "response_not_object"}
    conditions = ruleset.get("conditions")
    refs = conditions.get("ref_name") if isinstance(conditions, dict) else None
    includes = refs.get("include") if isinstance(refs, dict) else None
    rules = ruleset.get("rules")
    types = {rule["type"] for rule in rules if isinstance(rule, dict) and type(rule.get("type")) is str} if isinstance(rules, list) else set()
    targets_main = isinstance(includes, list) and "refs/heads/main" in includes
    good = (ruleset.get("id") == RULESET_ID and ruleset.get("source") == REPO
            and ruleset.get("target") == "branch" and ruleset.get("enforcement") == "active"
            and targets_main and {"deletion", "non_fast_forward"}.issubset(types))
    extra = bool(types.intersection({"update", "pull_request", "required_status_checks"}))
    return {
        "state": "baseline_verified" if good and not extra else "review_required",
        "active": ruleset.get("enforcement") == "active",
        "targets_main": bool(targets_main),
        "blocks_deletion": "deletion" in types,
        "blocks_force_push": "non_fast_forward" in types,
        "automation_write_restriction_detected": extra,
        "owner_review_enforced": "not_established_by_this_check",
    }


def main():
    request = urllib.request.Request(URL, headers={
        "Accept": "application/vnd.github+json",
        "User-Agent": "CF-0-public-rules-audit",
    })
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.load(response)
    except (urllib.error.URLError, OSError, ValueError) as exc:
        print(json.dumps({"state": "unavailable", "reason": type(exc).__name__}, sort_keys=True))
        return 1
    result = classify(data)
    print(json.dumps(result, sort_keys=True))
    return 0 if result["state"] == "baseline_verified" else 1


if __name__ == "__main__":
    sys.exit(main())
