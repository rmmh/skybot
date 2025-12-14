import json
import re
import time

from util import hook, http


API_BASE = "https://api.github.com"
DEFAULT_POLL_INTERVAL = 60
MAX_EVENTS_PER_POLL = 3

_repo_re = re.compile(r"^(?P<owner>[A-Za-z0-9_.-]+)/(?P<repo>[A-Za-z0-9_.-]+)$")

_last_poll_by_conn = {}


def _now():
    return int(time.time())


def _normalize_repo(repo):
    repo = (repo or "").strip()
    m = _repo_re.match(repo)
    if not m:
        raise ValueError("expected owner/repo")
    return f"{m.group('owner')}/{m.group('repo')}"


def _db_init(db):
    db.execute(
        "create table if not exists github_watches ("
        "chan text not null, "
        "repo text not null, "
        "last_id text, "
        "etag text, "
        "primary key (chan, repo)"
        ")"
    )
    db.commit()


def _github_token(bot):
    # Optional: set in config.json under api_keys.github
    bot_keys = (bot.config or {}).get("api_keys", {})
    return bot_keys.get("github")


def _github_headers(token=None, etag=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "skybot-github-plugin",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if etag:
        headers["If-None-Match"] = etag
    return headers


def _github_get_json(url, token=None, etag=None):
    try:
        resp = http.open(url, headers=_github_headers(token=token, etag=etag))
        body = resp.read().decode("utf-8", "replace")
        new_etag = None
        try:
            new_etag = resp.headers.get("ETag")
        except Exception:
            pass
        return json.loads(body), new_etag
    except http.HTTPError as e:
        if getattr(e, "code", None) == 304:
            return None, etag
        raise


def _repo_short(repo_full):
    if not repo_full:
        return "unknown"
    return repo_full.split("/", 1)[-1]


def _compare_url(repo_full, before, head):
    if not (repo_full and before and head):
        return None
    return f"https://github.com/{repo_full}/compare/{before}...{head}"


def _compare_stats(repo_full, before, head, token=None):
    """Return (additions, deletions, files_changed, commit_count) using GitHub compare API."""

    if not (repo_full and before and head):
        return None
    url = f"{API_BASE}/repos/{repo_full}/compare/{before}...{head}"
    data, _ = _github_get_json(url, token=token)
    if not data:
        return None
    files = data.get("files") or []
    additions = 0
    deletions = 0
    for f in files:
        try:
            additions += int(f.get("additions") or 0)
            deletions += int(f.get("deletions") or 0)
        except Exception:
            continue
    commit_count = data.get("total_commits")
    if not isinstance(commit_count, int):
        commit_count = len(data.get("commits") or [])
    return additions, deletions, len(files), commit_count


def _short_sha(sha):
    if not sha:
        return ""
    return sha[:7]


def format_event(event, token=None):
    """Format a GitHub Events API item into a short IRC-friendly line."""

    etype = event.get("type")
    actor = (event.get("actor") or {}).get("login") or "someone"
    repo = (event.get("repo") or {}).get("name") or "unknown/repo"
    payload = event.get("payload") or {}

    if etype == "PushEvent":
        ref = (payload.get("ref") or "").replace("refs/heads/", "")
        size = payload.get("size")
        commits = payload.get("commits") or []
        head = payload.get("head")
        before = payload.get("before")
        verb = "pushed"
        count = size if isinstance(size, int) else len(commits)
        repo_tag = _repo_short(repo)

        compare_base = before
        compare_head = head
        stats = None
        try:
            stats = _compare_stats(repo, compare_base, compare_head, token=token)
        except Exception:
            stats = None

        # If the forward compare shows no changes, try the reverse direction.
        # This happens with force-pushes / rewrites where the public Events API
        # sometimes yields a "before/head" pair that produces an empty compare.
        if stats:
            additions, deletions, files_changed, compare_commit_count = stats
            if isinstance(compare_commit_count, int) and compare_commit_count > 0:
                count = compare_commit_count

            if (
                (not isinstance(compare_commit_count, int) or compare_commit_count <= 0)
                and additions == 0
                and deletions == 0
                and files_changed == 0
                and before
                and head
            ):
                try:
                    rev = _compare_stats(repo, head, before, token=token)
                except Exception:
                    rev = None

                if rev:
                    r_add, r_del, r_files, r_commits = rev
                    if (
                        (isinstance(r_commits, int) and r_commits > 0)
                        or r_add
                        or r_del
                        or r_files
                    ):
                        compare_base = head
                        compare_head = before
                        stats = rev
                        if isinstance(r_commits, int) and r_commits > 0:
                            count = r_commits

        compare = _compare_url(repo, compare_base, compare_head)

        bits = [f"[{repo_tag}] {actor} {verb} {count} commit(s)"]
        if ref:
            bits.append(f"to {ref}")
        else:
            bits.append(f"to {repo_tag}")

        if stats:
            additions, deletions, files_changed, _compare_commit_count = stats
            bits.append(f"[+{additions}/-{deletions}/\u00b1{files_changed}]")

        if compare:
            bits.append(compare)
        elif head:
            bits.append(_short_sha(head))

        return " ".join(bits)

    if etype == "PullRequestEvent":
        action = payload.get("action") or "updated"
        pr = payload.get("pull_request") or {}
        number = pr.get("number") or payload.get("number")
        title = (pr.get("title") or "").strip()
        url = pr.get("html_url")
        bits = [f"[{_repo_short(repo)}] {actor} {action} PR"]
        if number is not None:
            bits[-1] += f" #{number}"
        if title:
            bits.append(f"\"{title}\"")
        bits.append(f"in {repo}")
        if url:
            bits.append(url)
        return " ".join(bits)

    if etype == "IssuesEvent":
        action = payload.get("action") or "updated"
        issue = payload.get("issue") or {}
        number = issue.get("number")
        title = (issue.get("title") or "").strip()
        url = issue.get("html_url")
        bits = [f"[{_repo_short(repo)}] {actor} {action} issue"]
        if number is not None:
            bits[-1] += f" #{number}"
        if title:
            bits.append(f"\"{title}\"")
        bits.append(f"in {repo}")
        if url:
            bits.append(url)
        return " ".join(bits)

    if etype == "IssueCommentEvent":
        action = payload.get("action") or "commented"
        issue = payload.get("issue") or {}
        number = issue.get("number")
        url = (payload.get("comment") or {}).get("html_url") or issue.get("html_url")
        bits = [f"[{_repo_short(repo)}] {actor} {action} on issue"]
        if number is not None:
            bits[-1] += f" #{number}"
        bits.append(f"in {repo}")
        if url:
            bits.append(url)
        return " ".join(bits)

    if etype == "ReleaseEvent":
        action = payload.get("action") or "published"
        release = payload.get("release") or {}
        tag = release.get("tag_name")
        url = release.get("html_url")
        bits = [f"[{_repo_short(repo)}] {actor} {action} release"]
        if tag:
            bits[-1] += f" {tag}"
        bits.append(f"in {repo}")
        if url:
            bits.append(url)
        return " ".join(bits)

    if etype == "CreateEvent":
        ref_type = payload.get("ref_type") or "ref"
        ref = payload.get("ref")
        bits = [f"[{_repo_short(repo)}] {actor} created {ref_type}"]
        if ref:
            bits[-1] += f" {ref}"
        bits.append(f"in {repo}")
        return " ".join(bits)

    if etype == "DeleteEvent":
        ref_type = payload.get("ref_type") or "ref"
        ref = payload.get("ref")
        bits = [f"[{_repo_short(repo)}] {actor} deleted {ref_type}"]
        if ref:
            bits[-1] += f" {ref}"
        bits.append(f"in {repo}")
        return " ".join(bits)

    if etype == "ForkEvent":
        forkee = payload.get("forkee") or {}
        full_name = forkee.get("full_name")
        url = forkee.get("html_url")
        bits = [f"[{_repo_short(repo)}] {actor} forked {repo}"]
        if full_name:
            bits.append(f"to {full_name}")
        if url:
            bits.append(url)
        return " ".join(bits)

    if etype == "WatchEvent":
        action = payload.get("action") or "starred"
        return f"[{_repo_short(repo)}] {actor} {action} {repo}"

    # Fallback
    return f"[{_repo_short(repo)}] {actor} did {etype or 'something'} in {repo}"


def _poll_interval(bot):
    cfg = (bot.config or {}).get("github", {})
    try:
        interval = int(cfg.get("poll_interval", DEFAULT_POLL_INTERVAL))
    except Exception:
        interval = DEFAULT_POLL_INTERVAL
    # GitHub unauthenticated API rate limit is very low; avoid hammering.
    if not _github_token(bot):
        interval = max(interval, 300)
    return max(15, interval)


def _poll_due(conn, bot):
    key = (id(conn), getattr(conn, "server_host", None), getattr(conn, "nick", None))
    now = time.time()
    last = _last_poll_by_conn.get(key, 0)
    interval = _poll_interval(bot)
    if now - last < interval:
        return False
    _last_poll_by_conn[key] = now
    return True


def _fetch_repo_events(repo, token=None, etag=None):
    url = f"{API_BASE}/repos/{repo}/events"
    return _github_get_json(url, token=token, etag=etag)


def _post(conn, chan, text):
    if not text:
        return
    # IRC line safety (hard limit also enforced by core)
    text = str(text).replace("\n", " ").replace("\r", " ")
    conn.msg(chan, text[:450])


def _post_announcement(conn, chan, bot, text):
    # No embedded timestamps and no pseudo-nick prefix.
    _post(conn, chan, text)


def ghevent(inp, bot=None):
    """Show the latest public event for a repo.

    Use: `.git event owner/repo`
    """

    repo = _normalize_repo(inp)
    token = _github_token(bot)

    try:
        events, _ = _fetch_repo_events(repo, token=token)
    except http.HTTPError as e:
        code = getattr(e, "code", None)
        if code == 403:
            return "GitHub API rate limit exceeded (add api_keys.github token or increase github.poll_interval)"
        if code is not None:
            return f"GitHub API error (HTTP {code})"
        return "GitHub API error"
    except Exception:
        return "GitHub API error"
    if not events:
        return "no recent events"
    return format_event(events[0], token=token)


def _git_watch_list(rest, chan="", db=None):
    _db_init(db)

    parts = (rest or "").split()

    # Default to current channel if called in-channel; otherwise require explicit.
    target = chan
    if parts and parts[0].startswith("#"):
        target = parts[0]
    if not (target and target.startswith("#")):
        raise ValueError("please specify a channel (e.g. #mychan)")

    rows = db.execute(
        "select repo from github_watches where chan=? order by repo", (target,)
    ).fetchall()
    if not rows:
        return f"no watches for {target}"
    return f"watches for {target}: " + ", ".join(r[0] for r in rows)


def _git_watch_add(rest, chan="", db=None):
    _db_init(db)

    parts = (rest or "").split()
    if len(parts) < 1:
        raise ValueError("usage: .git add owner/repo [#channel]")

    repo = _normalize_repo(parts[0])
    target = parts[1] if len(parts) >= 2 and parts[1].startswith("#") else chan
    if not (target and target.startswith("#")):
        raise ValueError("please specify a channel (e.g. #mychan)")

    db.execute(
        "insert or ignore into github_watches(chan, repo, last_id, etag) values(?,?,NULL,NULL)",
        (target, repo),
    )
    db.commit()
    return f"ok, watching {repo} in {target}"


def _git_watch_remove(rest, chan="", db=None):
    _db_init(db)

    parts = (rest or "").split()
    if len(parts) < 1:
        raise ValueError("usage: .git remove owner/repo [#channel]")

    repo = _normalize_repo(parts[0])
    target = parts[1] if len(parts) >= 2 and parts[1].startswith("#") else chan
    if not (target and target.startswith("#")):
        raise ValueError("please specify a channel (e.g. #mychan)")

    cur = db.execute("delete from github_watches where chan=? and repo=?", (target, repo))
    db.commit()
    if cur.rowcount:
        return f"ok, stopped watching {repo} in {target}"
    return f"not watching {repo} in {target}"


@hook.command("git")
def git(inp, chan="", db=None, bot=None, nick=""):
    """GitHub helper commands (subcommand-style).

    Usage:
            .git event owner/repo
            .git add owner/repo [#channel]
            .git remove owner/repo [#channel]
            .git list [#channel]

    Notes:
      - Set token in config.json: api_keys.github
      - Poll interval: github.poll_interval (seconds)
    """

    parts = (inp or "").split(None, 1)
    if not parts:
        return None

    sub = parts[0].lower()
    rest = parts[1] if len(parts) > 1 else ""

    try:
        if sub in ("event", "events", "latest"):
            return ghevent(rest, bot=bot)

        if sub in ("add", "watch"):
            return _git_watch_add(rest, chan=chan, db=db)

        if sub in ("remove", "rm", "del", "unwatch"):
            return _git_watch_remove(rest, chan=chan, db=db)

        if sub in ("list", "ls"):
            return _git_watch_list(rest, chan=chan, db=db)
    except ValueError as e:
        return str(e)

    return "unknown subcommand (try: event, add, remove, list)"


@hook.singlethread
@hook.event("*")
def github_poll(inp, conn=None, db=None, bot=None):
    # Poll periodically on incoming server traffic (PINGs, joins, chat, etc.)
    if conn is None or db is None or bot is None:
        return

    if not _poll_due(conn, bot):
        return

    _db_init(db)
    token = _github_token(bot)

    watches = db.execute(
        "select chan, repo, last_id, etag from github_watches order by chan, repo"
    ).fetchall()
    if not watches:
        return

    for chan, repo, last_id, etag in watches:
        try:
            events, new_etag = _fetch_repo_events(repo, token=token, etag=etag)
        except http.HTTPError:
            # Avoid spamming the channel on API errors.
            continue
        except Exception:
            continue

        if events is None:
            # 304 Not Modified
            continue

        if not events:
            continue

        newest_id = events[0].get("id")

        # First time: set cursor but don't spam the channel.
        if not last_id:
            db.execute(
                "update github_watches set last_id=?, etag=? where chan=? and repo=?",
                (newest_id, new_etag, chan, repo),
            )
            db.commit()
            continue

        # Collect events after last_id (chronological).
        new_events = []
        collecting = False
        for ev in reversed(events):
            ev_id = ev.get("id")
            if ev_id == last_id:
                collecting = True
                continue
            if collecting:
                new_events.append(ev)

        # If last_id fell out of the window, just move the cursor.
        if not collecting:
            db.execute(
                "update github_watches set last_id=?, etag=? where chan=? and repo=?",
                (newest_id, new_etag, chan, repo),
            )
            db.commit()
            continue

        if not new_events:
            db.execute(
                "update github_watches set last_id=?, etag=? where chan=? and repo=?",
                (newest_id, new_etag, chan, repo),
            )
            db.commit()
            continue

        overflow = max(0, len(new_events) - MAX_EVENTS_PER_POLL)
        if overflow:
            new_events = new_events[-MAX_EVENTS_PER_POLL:]

        for ev in new_events:
            _post_announcement(conn, chan, bot, format_event(ev, token=token))

        if overflow:
            _post_announcement(conn, chan, bot, f"(+{overflow} more events)")

        db.execute(
            "update github_watches set last_id=?, etag=? where chan=? and repo=?",
            (newest_id, new_etag, chan, repo),
        )
        db.commit()
