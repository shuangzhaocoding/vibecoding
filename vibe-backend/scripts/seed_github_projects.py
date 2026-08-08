# -*- coding: utf-8 -*-
"""从 GitHub 搜索 Vibe Coding 作品并写入 projects 表。

用法（在 vibe-backend 目录下）:
  ../../venv/bin/python scripts/seed_github_projects.py --dry-run
  ../../venv/bin/python scripts/seed_github_projects.py --limit 12
  GITHUB_TOKEN=xxx ../../venv/bin/python scripts/seed_github_projects.py --min-stars 50

可选环境变量:
  GITHUB_TOKEN  提高 API 限额（未登录约 10 次/分钟，有 token 约 30 次/分钟）
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from loguru import logger
from tortoise import Tortoise
from tortoise.expressions import Q

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.settings import TORTOISE_ORM  # noqa: E402
from app.models import Project, User  # noqa: E402

# GitHub 搜索查询（按星数排序后合并去重）
DEFAULT_QUERIES = [
    "topic:vibecoding",
    "topic:vibe-coding",
    "vibe-coding in:name,description stars:>20",
    '"vibe coding" language:TypeScript stars:>100',
]

# 搜索可能漏掉、但适合展示的仓库（full_name）
CURATED_REPOS = [
    "onlook-dev/onlook",
    "cloudflare/vibesdk",
    "datawhalechina/easy-vibe",
    "datawhalechina/vibe-vibe",
    "ZSeven-W/openpencil",
    "Egonex-AI/Understand-Anything",
    "nexu-io/open-design",
    "CherryHQ/cherry-studio",
    "refly-ai/refly",
    "amantus-ai/vibetunnel",
    "Leonxlnx/taste-skill",
    "flipped-aurora/gin-vue-admin",
]

# 名称/描述命中则跳过（列表型仓库、非作品）
SKIP_NAME_KEYWORDS = (
    "awesome-",
    "awesome_",
    "best-practice",
    "best_practice",
    "cheatsheet",
    "tutorial-only",
)

API_ROOT = "https://api.github.com"
OG_COVER = "https://opengraph.githubassets.com/1/{full_name}"


def _request_json(url: str, token: Optional[str] = None) -> Dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "vibecoding-seed-script",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"GitHub API {e.code}: {body}") from e


def search_repos(query: str, *, token: Optional[str], per_page: int = 20) -> List[Dict[str, Any]]:
    qs = urllib.parse.urlencode(
        {"q": query, "sort": "stars", "order": "desc", "per_page": per_page}
    )
    data = _request_json(f"{API_ROOT}/search/repositories?{qs}", token=token)
    if data.get("message") and not data.get("items"):
        raise RuntimeError(data["message"])
    return list(data.get("items") or [])


def fetch_repo(full_name: str, *, token: Optional[str]) -> Dict[str, Any]:
    return _request_json(f"{API_ROOT}/repos/{full_name}", token=token)


def normalize_homepage(homepage: Optional[str], html_url: str) -> Optional[str]:
    hp = (homepage or "").strip()
    if not hp:
        return None
    if hp.startswith("http://") or hp.startswith("https://"):
        return hp.rstrip("/")
    return f"https://{hp}".rstrip("/")


def should_skip(repo: Dict[str, Any], *, min_stars: int) -> Optional[str]:
    name = (repo.get("name") or "").lower()
    full = (repo.get("full_name") or "").lower()
    desc = (repo.get("description") or "").lower()
    stars = int(repo.get("stargazers_count") or 0)
    if stars < min_stars:
        return f"stars<{min_stars}"
    if repo.get("archived") or repo.get("disabled"):
        return "archived/disabled"
    if not normalize_homepage(repo.get("homepage"), repo.get("html_url") or ""):
        return "no homepage"
    for kw in SKIP_NAME_KEYWORDS:
        if kw in name or kw in full:
            return f"skip keyword:{kw}"
    # 纯资源列表：名字含 awesome 且简介像 curated list
    if "awesome" in name and ("list" in desc or "curated" in desc or "collection" in desc):
        return "awesome list"
    return None


def pick_tags(repo: Dict[str, Any], limit: int = 6) -> List[str]:
    topics = list(repo.get("topics") or [])
    prefer = []
    for t in topics:
        tl = t.lower()
        if tl in {"vibecoding", "vibe-coding", "ai", "agent", "design", "vue", "react"}:
            prefer.append(tl)
    rest = [t for t in topics if t not in prefer]
    tags = prefer + rest
    lang = repo.get("language")
    if lang and lang.lower() not in {t.lower() for t in tags}:
        tags.append(lang.lower())
    # 去重保序
    seen: Set[str] = set()
    out: List[str] = []
    for t in tags:
        key = t.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
        if len(out) >= limit:
            break
    if "vibecoding" not in seen and "vibe-coding" not in seen:
        out = (out + ["vibecoding"])[:limit]
    return out


def build_summary(repo: Dict[str, Any]) -> str:
    desc = (repo.get("description") or "").strip()
    if desc:
        return desc[:500]
    return f"GitHub 开源项目 {repo.get('full_name')}"


def build_description(repo: Dict[str, Any]) -> str:
    full_name = repo["full_name"]
    desc = (repo.get("description") or "").strip() or "（暂无简介）"
    stars = repo.get("stargazers_count") or 0
    lang = repo.get("language") or "-"
    topics = ", ".join((repo.get("topics") or [])[:12]) or "-"
    site = normalize_homepage(repo.get("homepage"), repo["html_url"]) or repo["html_url"]
    return f"""## {repo.get('name')}

{desc}

### 信息
- **仓库**: https://github.com/{full_name}
- **站点**: {site}
- **Stars**: {stars:,}
- **语言**: {lang}
- **Topics**: {topics}

> 由 `scripts/seed_github_projects.py` 从 GitHub 同步。
"""


def popularity_seed(stars: int) -> Dict[str, int]:
    """按 star 粗略预填互动数，便于排行展示。"""
    view = max(50, min(stars // 20, 5000))
    like = max(5, min(stars // 500, 200))
    fav = max(3, min(stars // 800, 120))
    return {"view_count": view, "like_count": like, "favorite_count": fav}


def collect_candidates(
    *,
    queries: List[str],
    curated: List[str],
    token: Optional[str],
    min_stars: int,
    per_query: int,
    sleep_s: float,
) -> List[Dict[str, Any]]:
    by_full: Dict[str, Dict[str, Any]] = {}

    for q in queries:
        logger.info(f"search: {q}")
        try:
            items = search_repos(q, token=token, per_page=per_query)
        except Exception as e:
            logger.warning(f"search failed [{q}]: {e}")
            time.sleep(sleep_s)
            continue
        for item in items:
            full = item.get("full_name")
            if full:
                by_full[full] = item
        time.sleep(sleep_s)

    for full in curated:
        if full in by_full:
            continue
        logger.info(f"fetch curated: {full}")
        try:
            by_full[full] = fetch_repo(full, token=token)
        except Exception as e:
            logger.warning(f"fetch failed [{full}]: {e}")
        time.sleep(sleep_s)

    accepted: List[Dict[str, Any]] = []
    for full, repo in by_full.items():
        reason = should_skip(repo, min_stars=min_stars)
        if reason:
            logger.debug(f"skip {full}: {reason}")
            continue
        accepted.append(repo)

    accepted.sort(key=lambda r: int(r.get("stargazers_count") or 0), reverse=True)
    logger.info(f"candidates: {len(accepted)} / scanned {len(by_full)}")
    return accepted


async def upsert_projects(
    repos: List[Dict[str, Any]],
    *,
    author: User,
    limit: int,
    dry_run: bool,
) -> Dict[str, int]:
    stats = {"inserted": 0, "skipped": 0, "considered": 0}
    for repo in repos:
        if stats["inserted"] >= limit:
            break
        stats["considered"] += 1
        title = (repo.get("name") or repo["full_name"]).strip()[:200]
        # 更友好的展示名：owner/name 里取 name，保留原 description 在 summary
        display_title = title
        site_url = normalize_homepage(repo.get("homepage"), repo["html_url"])
        assert site_url  # should_skip 已保证

        exists = await Project.filter(
            Q(title=display_title) | Q(site_url=site_url) | Q(site_url=site_url + "/")
        ).exists()
        if exists:
            logger.info(f"exists, skip: {display_title} ({site_url})")
            stats["skipped"] += 1
            continue

        payload = {
            "title": display_title,
            "cover_url": OG_COVER.format(full_name=repo["full_name"]),
            "summary": build_summary(repo),
            "description": build_description(repo),
            "site_url": site_url,
            "tags": pick_tags(repo),
            "status": "published",
            "author": author,
            **popularity_seed(int(repo.get("stargazers_count") or 0)),
        }

        if dry_run:
            logger.info(
                f"[dry-run] would insert: {display_title} | {site_url} | "
                f"★{repo.get('stargazers_count')} | tags={payload['tags']}"
            )
            stats["inserted"] += 1
            continue

        p = await Project.create(**payload)
        logger.info(f"inserted #{p.id}: {display_title} -> {site_url}")
        stats["inserted"] += 1
    return stats


async def amain(args: argparse.Namespace) -> int:
    token = args.token or os.environ.get("GITHUB_TOKEN") or None
    queries = args.query or DEFAULT_QUERIES
    curated = [] if args.no_curated else CURATED_REPOS

    repos = collect_candidates(
        queries=queries,
        curated=curated,
        token=token,
        min_stars=args.min_stars,
        per_query=args.per_query,
        sleep_s=args.sleep,
    )
    if not repos:
        logger.error("no candidates found")
        return 1

    await Tortoise.init(config=TORTOISE_ORM)
    try:
        author = await User.get_or_none(username=args.author)
        if not author:
            logger.error(f"author user not found: {args.author}")
            return 1

        stats = await upsert_projects(
            repos,
            author=author,
            limit=args.limit,
            dry_run=args.dry_run,
        )
        logger.info(
            f"done: inserted={stats['inserted']} skipped={stats['skipped']} "
            f"considered={stats['considered']} dry_run={args.dry_run}"
        )
    finally:
        await Tortoise.close_connections()
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="从 GitHub 抓取 Vibe Coding 作品写入数据库")
    p.add_argument("--limit", type=int, default=12, help="最多新写入条数（默认 12）")
    p.add_argument("--min-stars", type=int, default=100, help="最低 star 数（默认 100）")
    p.add_argument("--per-query", type=int, default=20, help="每个搜索查询取前 N 条")
    p.add_argument("--author", default="admin", help="作品作者用户名（默认 admin）")
    p.add_argument("--token", default=None, help="GitHub token（也可用 GITHUB_TOKEN）")
    p.add_argument("--query", action="append", help="自定义搜索 query，可重复；默认用内置查询")
    p.add_argument("--no-curated", action="store_true", help="不强制拉取 CURATED_REPOS")
    p.add_argument("--sleep", type=float, default=1.2, help="请求间隔秒数，避免限流")
    p.add_argument("--dry-run", action="store_true", help="只打印将写入的条目，不落库")
    return p


def main() -> None:
    args = build_parser().parse_args()
    raise SystemExit(asyncio.run(amain(args)))


if __name__ == "__main__":
    main()
