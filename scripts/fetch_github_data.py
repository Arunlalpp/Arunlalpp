"""Fetch public GitHub profile data for the README cards.

Runs inside GitHub Actions with GITHUB_TOKEN. Writes data/github.json.
"""
import json
import os
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone

USER = os.environ.get("GH_USER", "Arunlalpp")
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "github.json")

QUERY = """
query($login: String!) {
  user(login: $login) {
    name
    followers { totalCount }
    repositories(ownerAffiliations: OWNER, isFork: false, first: 100,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      nodes {
        name
        stargazerCount
        pushedAt
        languages(first: 6, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def graphql(query, variables):
    if not TOKEN:
        sys.exit("GITHUB_TOKEN is not set")
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        sys.exit(f"GraphQL errors: {payload['errors']}")
    return payload["data"]


def main():
    user = graphql(QUERY, {"login": USER})["user"]
    repos = user["repositories"]["nodes"]

    lang_bytes, lang_color = Counter(), {}
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            lang_bytes[name] += edge["size"]
            lang_color[name] = edge["node"]["color"] or "#8b949e"

    calendar = user["contributionsCollection"]["contributionCalendar"]
    days = [d for w in calendar["weeks"] for d in w["contributionDays"]]

    # current streak (days with contributions, counting back from today/yesterday)
    streak = 0
    for d in reversed(days):
        if d["contributionCount"] > 0:
            streak += 1
        elif streak == 0 and d is days[-1]:
            continue  # today may not have contributions yet
        else:
            break

    data = {
        "user": USER,
        "name": user["name"] or USER,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "followers": user["followers"]["totalCount"],
        "repos": user["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in repos),
        "contributions_year": calendar["totalContributions"],
        "current_streak": streak,
        "languages": [
            {"name": n, "bytes": b, "color": lang_color[n]}
            for n, b in lang_bytes.most_common(6)
        ],
        "days": [{"date": d["date"], "count": d["contributionCount"]} for d in days],
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(data, fh, indent=1)
    print(f"Wrote {OUT}: {data['repos']} repos, {data['contributions_year']} contributions")


if __name__ == "__main__":
    main()
