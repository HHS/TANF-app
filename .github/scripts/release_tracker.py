#!/usr/bin/env python3
"""Create a Release Tracker issue for a release and copy its pull requests in.

Run by .github/workflows/release-tracker.yml. All inputs arrive as environment
variables and are treated as data. Release notes and PR titles are untrusted.

Environment:
  TAG                  Release tag, e.g. v4.27.0 (required)
  DRY_RUN              "true" prints the issue body and changes nothing
  NOTIFY_EXISTING      "true" also sends the webhook when the tracker already exists
  GITHUB_REPOSITORY    owner/name (set by Actions)
  GH_TOKEN             Token for the gh CLI (set by the workflow)
  AGENT_WEBHOOK_URL    Optional. Where to POST the "tracker created" event
  AGENT_WEBHOOK_KEY    Optional. Sender key for that webhook
  AGENT_WEBHOOK_KEY_HEADER  Optional. Header name for the key (default Authorization)
"""
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

REPO = os.environ.get("GITHUB_REPOSITORY", "raft-tech/TANF-app")
TEMPLATE = os.environ.get(
    "TEMPLATE_PATH", ".github/ISSUE_TEMPLATE/release-tracker-issue-template.md"
)
TAG_RE = re.compile(r"^v\d+\.\d+\.\d+(?:[-.][0-9A-Za-z.-]+)?$")
PR_LINE_RE = re.compile(
    r"^\s*[*-]\s+(?P<title>.+?)\s+by\s+@(?P<author>[\w.-]+(?:\[bot\])?)"
    r"\s+in\s+(?P<url>https://github\.com/" + re.escape(REPO) + r"/pull/(?P<num>\d+))\s*$",
    re.IGNORECASE,
)
CHANGELOG_RE = re.compile(r"/compare/(?P<prev>[^\s/]+?)\.\.\.(?P<cur>[^\s/]+)")
SORT_HEADINGS = [
    "External users will see a change:",
    "Internal users will see a change:",
    "No visible change for end users:",
]
UNSORTED_HEADING = "Uncategorized (to be sorted)"


def log(msg):
    print(msg, flush=True)


def gh_api(path, method="GET", payload=None, fields=None):
    cmd = ["gh", "api", "-X", method, path]
    for key, value in (fields or {}).items():
        cmd += ["-f", f"{key}={value}"]
    if payload is not None:
        cmd += ["--input", "-"]
    res = subprocess.run(
        cmd,
        input=json.dumps(payload) if payload is not None else None,
        capture_output=True,
        text=True,
    )
    if res.returncode != 0:
        raise RuntimeError(f"gh api {method} {path} failed: {res.stderr.strip()}")
    return json.loads(res.stdout) if res.stdout.strip() else {}


def clean(text):
    """Make untrusted text safe for a single checklist line."""
    return " ".join(str(text).split())


def parse_pr_lines(notes):
    prs, seen = [], set()
    for line in (notes or "").splitlines():
        m = PR_LINE_RE.match(line)
        if m and m["num"] not in seen:
            seen.add(m["num"])
            prs.append((clean(m["title"]), m["author"], m["url"]))
    return prs


def previous_tag(*bodies):
    for body in bodies:
        m = CHANGELOG_RE.search(body or "")
        if m:
            return m["prev"]
    return None


def prs_from_commits(prev, tag):
    """Last resort (cherry-picked hotfixes): find PR numbers in commit subjects."""
    data = gh_api(f"repos/{REPO}/compare/{prev}...{tag}")
    prs, seen = [], set()
    for c in data.get("commits", []):
        subject = c["commit"]["message"].splitlines()[0]
        m = re.search(r"\(#(\d+)\)\s*$", subject) or re.search(r"pull request #(\d+)", subject)
        if not m or m[1] in seen:
            continue
        seen.add(m[1])
        pr = gh_api(f"repos/{REPO}/pulls/{m[1]}")
        prs.append((clean(pr["title"]), pr["user"]["login"], pr["html_url"]))
    return prs


def collect_prs(tag, release_body):
    prs = parse_pr_lines(release_body)
    if prs:
        log(f"Found {len(prs)} PRs in the release notes.")
        return prs
    log("Release notes list no PRs. Trying generated notes.")
    prev = previous_tag(release_body)
    fields = {"tag_name": tag}
    if prev:
        fields["previous_tag_name"] = prev
    generated = ""
    try:
        generated = gh_api(f"repos/{REPO}/releases/generate-notes", "POST", fields=fields).get("body", "")
    except RuntimeError as err:
        log(f"Generate-notes failed: {err}")
    prs = parse_pr_lines(generated)
    if prs:
        log(f"Found {len(prs)} PRs in generated notes.")
        return prs
    prev = prev or previous_tag(generated)
    if prev:
        log(f"Generated notes list no PRs. Reading commits {prev}...{tag}.")
        prs = prs_from_commits(prev, tag)
        log(f"Found {len(prs)} PRs in commit subjects.")
    else:
        log("No previous tag found. The PR list will be empty.")
    return prs


def read_template():
    with open(TEMPLATE, encoding="utf-8") as f:
        raw = f.read()
    m = re.match(r"^---\n(.*?)\n---\n", raw, re.DOTALL)
    if not m:
        raise SystemExit("Template has no front matter.")
    meta = {}
    for line in m[1].splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            meta[key.strip()] = value.strip().strip("'\"")
    return meta, raw[m.end():].lstrip("\n")


def split_list(value):
    return [v.strip() for v in (value or "").split(",") if v.strip()]


def build_body(template_body, tag, prs):
    """Fill section 1 of the template. Everything else stays as written."""
    start = template_body.find("## 🔗 1.")
    end = template_body.find("\n---", start)
    if start < 0 or end < 0:
        raise SystemExit("Template section 1 not found. Update release_tracker.py.")
    section = template_body[start:end]
    head = section[: section.find("###")] if "###" in section else section + "\n"
    head = head.replace("vX.X.X", tag)
    lines = [f"### {UNSORTED_HEADING}",
             "_Temporary list. Move each item under one of the headings below, then delete this heading._"]
    if prs:
        lines += [f"- [ ] {t} by @{a} in {u}" for t, a, u in prs]
    else:
        lines.append("_No pull requests were found in the release notes. Add them by hand._")
    for heading in SORT_HEADINGS:
        lines += ["", f"### {heading}"]
    new_section = head + "\n".join(lines) + "\n"
    return template_body[:start] + new_section + template_body[end:]


def find_existing(title):
    q = f'repo:{REPO} is:issue in:title "{title}"'
    res = gh_api("search/issues", fields={"q": q, "per_page": "100"})
    for item in res.get("items", []):
        if item["title"].strip() == title:
            return item["number"]
    return None


def notify_agent(tag, number):
    """Best effort. Never raises, never fails the job."""
    url = os.environ.get("AGENT_WEBHOOK_URL", "").strip()
    if not url:
        log("RELEASE_TRACKER_AGENT_WEBHOOK_URL is not set. Skipping webhook.")
        return
    if not url.startswith("https://"):
        log("Webhook URL is not https. Skipping webhook.")
        return
    headers = {"Content-Type": "application/json"}
    key = os.environ.get("AGENT_WEBHOOK_KEY", "").strip()
    name = os.environ.get("AGENT_WEBHOOK_KEY_HEADER", "").strip() or "Authorization"
    if key:
        headers[name] = f"Bearer {key}" if name.lower() == "authorization" else key
    else:
        log("RELEASE_TRACKER_AGENT_WEBHOOK_KEY is not set. Sending without a key.")
    data = json.dumps(
        {"event": "release_tracker_created", "tag": tag, "tracker_issue": number, "repo": REPO}
    ).encode()
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=15) as resp:
                log(f"Webhook sent (HTTP {resp.status}).")
                return
        except urllib.error.HTTPError as err:
            log(f"Webhook attempt {attempt} failed (HTTP {err.code}).")
        except Exception as err:  # noqa: BLE001 - must never fail the job
            log(f"Webhook attempt {attempt} failed ({type(err).__name__}).")
        if attempt < 3:
            time.sleep(2 * attempt)
    log("Webhook failed after 3 attempts. The tracker issue was still handled.")


def set_output(number):
    path = os.environ.get("GITHUB_OUTPUT")
    if path:
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"tracker_issue={number}\n")


def main():
    tag = os.environ.get("TAG", "").strip()
    dry_run = os.environ.get("DRY_RUN", "").lower() == "true"
    if not TAG_RE.match(tag):
        log(f"'{tag}' is not a version tag like v1.2.3. Nothing to do.")
        return 0

    meta, template_body = read_template()
    title = meta.get("title", "Release Tracker vX.X.X").replace("vX.X.X", tag)

    existing = find_existing(title)
    if existing:
        log(f"Tracker already exists: #{existing} ({title}).")
        set_output(existing)
        if not dry_run:
            if os.environ.get("NOTIFY_EXISTING", "").lower() == "true":
                notify_agent(tag, existing)
            return 0

    release = gh_api(f"repos/{REPO}/releases/tags/{tag}")
    body = build_body(template_body, tag, collect_prs(tag, release.get("body")))

    if dry_run:
        if existing:
            log(f"DRY RUN. Would NOT create an issue (#{existing} exists). Body it would use:")
        else:
            log(f"DRY RUN. Would create issue: {title}")
        log(f"Labels: {split_list(meta.get('labels'))}  Assignees: {split_list(meta.get('assignees'))}")
        log("----- BODY START -----")
        log(body)
        log("----- BODY END -----")
        log("Would send webhook: " + json.dumps(
            {"event": "release_tracker_created", "tag": tag, "tracker_issue": existing or "<new>", "repo": REPO}))
        return 0

    payload = {"title": title, "body": body}
    if split_list(meta.get("labels")):
        payload["labels"] = split_list(meta["labels"])
    if split_list(meta.get("assignees")):
        payload["assignees"] = split_list(meta["assignees"])
    issue = gh_api(f"repos/{REPO}/issues", "POST", payload=payload)
    log(f"Created tracker #{issue['number']}: {issue['html_url']}")
    set_output(issue["number"])
    notify_agent(tag, issue["number"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
