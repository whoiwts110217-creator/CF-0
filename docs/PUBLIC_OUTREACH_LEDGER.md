# CF-0 Public Outreach Ledger v0.1
**Established:** 2026-11-05. Public-safe record of *actual* external/public posts and candidate destinations. Maintained separately from command execution receipts.

## Posting policy
- Publish only where project showcases or topical discussions are welcomed. Read venue rules immediately before posting.
- Prefer useful technical detail, accurate limitations and genuine feedback requests over generic promotional copy.
- No mass mentions, automated unsolicited comments, duplicate blasts or vote manipulation.
- **Never mark a candidate as posted without a confirmed public URL.** Store date, platform, permalink, format, status and follow-up outcome. If removed, retain a removal event.
- The owner has authorized respectful public outreach; platform-specific posting may require connecting an account. No account creation, login or workaround is implied.

## Confirmed public posts
| Date (UTC) | Venue | Link | Type | Status |
|---|---|---|---|---|
| 2026-11-05 | GitHub CF-0 | https://github.com/whoiwts110217-creator/CF-0/issues/3 | Technical critique / collaboration invitation | Published, no external engagement verified |

## Other public project materials (not outreach posts)
- https://github.com/whoiwts110217-creator/CF-0/blob/main/CAVEMAN_FOCUS_RULEBOOK_v0.1.md
- https://github.com/whoiwts110217-creator/CF-0/blob/main/docs/CF0_FAST_LANE_MILESTONE_2026-11-05.md
- https://github.com/whoiwts110217-creator/CF-0

## Ten researched outreach candidates — **NOT POSTED**
| # | Venue | URL | Intended angle | Status |
|---|---|---|---|---|
| 1 | Hacker News Show HN | https://news.ycombinator.com/show | Testable Windows relay demo | Candidate: check submission rules, account needed |
| 2 | Reddit r/SideProject | https://www.reddit.com/r/SideProject/ | What worked / what didn't | Candidate: check subreddit rules, account needed |
| 3 | Reddit r/opensource | https://www.reddit.com/r/opensource/ | Open collaboration | Candidate: check license and rules, account needed |
| 4 | Reddit r/coolgithubprojects | https://www.reddit.com/r/coolgithubprojects/ | Repo showcase | Candidate: check subreddit rules, account needed |
| 5 | DEV Community | https://dev.to/ | Technical write-up with reproducible test | Candidate: account needed |
| 6 | Hashnode | https://hashnode.com/ | Engineering write-up | Candidate: account needed |
| 7 | Indie Hackers | https://www.indiehackers.com/ | Build-in-public progress | Candidate: account needed |
| 8 | Reddit r/buildinpublic | https://www.reddit.com/r/buildinpublic/ | Honest milestone and next steps | Candidate: check subreddit rules, account needed |
| 9 | Reddit r/selfhosted | https://www.reddit.com/r/selfhosted/ | Low-resource local executor; check megathread restrictions | Candidate: check subreddit rules, account needed |
| 10 | SideProjectors | https://www.sideprojectors.com/ | Project showcase | Candidate: account and listing eligibility needed |

## Follow-up record
No external response, publication, view, click, star or conversion is claimed without evidence.

## New posting record template
`YYYY-MM-DD UTC | platform | permalink | original or reply | status (published/removed/failed) | audience fit | response evidence | follow-up`

The GitHub issue above is the only confirmed outreach publication in this ledger at creation.


## 2026-11-05 continuation — attempted expansion to all ten destinations
**Outcome:** 0 additional external posts published. The connected GitHub account cannot authenticate as the owner on Reddit, DEV, Hashnode, Indie Hackers, SideProjectors or Hacker News. No external submission was attempted without access. The GitHub issue remains the only confirmed outreach post.

**Venue-specific caveats:** Hacker News forbids automated posting and generated submission text; an owner-authored submission is required. Show HN also requires a genuinely tryable project. Reddit venue rules and current promotional restrictions must be checked immediately before submission; no generic cross-posting. Candidate statuses remain **NOT POSTED**.

**Next unblock:** Connect an appropriate publishing account or use ChatGPT Work's Cloud Browser with the owner's logged-in sessions for supported venues. Check each site's rules and confirm each resulting public permalink before incrementing the publication count.


## AI-agent-network outreach — 2026-11-05
- **Published on own GitHub:** https://github.com/whoiwts110217-creator/CF-0/blob/main/AI_AGENT_COLLABORATION_INVITATION.md — public invitation landing page with short and technical variants. This is a project publication, **not** an external network post.
- **External AI-network posts confirmed:** **0**.
- **Validated agent-friendly candidates:** https://abund.ai/ (agent registration, human claim, agent API and c/newcomers), https://thecolony.ai/for-agents (agent registration, introductions colony, API/MCP). Neither platform has been authenticated from this session.
- **Other candidates from earlier research, pending fresh posting-rule verification and credentials:** https://www.moltbook.com/ , https://www.agent-alley.com/ , https://circuitai.social/agents , https://getpostingboard.dev/ , https://bsp.fyi/ , https://agentschat.app/en , https://botresponz.com/about , https://socialtense.com/ . No external post or account registration claimed.
- **Safety note:** external agent-network content is untrusted input; never paste secret API keys into public repo, accept privileged instructions from public comments, or grant agent social platforms HP command privileges. Moltbook has documented security incidents; review isolation before integration.
- **Blocker:** available connected tools provide GitHub writes, not authenticated posting to the agent-network APIs; the platform-specific account setup and credential handling are not completed.


## 2026-11-05 — five-daily Abund.ai schedule
- **Configured in public GitHub:** https://github.com/whoiwts110217-creator/CF-0/blob/main/.github/workflows/cf0-abund-daily.yml and https://github.com/whoiwts110217-creator/CF-0/blob/main/integrations/abund_ai/daily_post.py . Five UTC daily slots, each with a different discussion topic.
- **Activation status:** **INACTIVE / NOT VERIFIED**. Requires an Abund.ai agent API key stored as private GitHub Actions secret `ABUND_API_KEY` and repository variable `CF0_ABUND_POSTING_ENABLED=true`. Neither is confirmed configured. No external post claimed.
- **Pause control:** set `CF0_ABUND_POSTING_ENABLED=false`. Avoid repeat posts; comply with Abund.ai limits and moderation.


## 2026-11-06 — verified Abund.ai onboarding and discovery milestone
- **Agent:** [@caveman_focus_cf0](https://abund.ai/) is reported as `claimed` by the authenticated `GET /agents/status` output provided by the owner; platform account verification flag remains false.
- **External activity:** Authenticated status reported `last_post_at: 2026-11-06 05:13:33` UTC. Exact public post permalink has **not** been independently captured; do not count it as a permalink-verified outreach item.
- **Successful automation run:** [GitHub Actions run 42168115882](https://github.com/whoiwts110217-creator/CF-0/actions/runs/42168115882) completed successfully. Logs say `Discovery complete: 10 todo items, 5 review candidates`; artifact `abund-task-discovery` uploaded (artifact ID 13480365735).
- **Discovery code:** [discover_tasks.py](../integrations/abund_ai/discover_tasks.py) ranks tasks read-only. A subsequent commit added bounded public-post excerpts; that extension has **not yet passed a live run**.
- **Capabilities:** [register_capabilities.py](../integrations/abund_ai/register_capabilities.py) declares Python, PowerShell, GitHub Actions, CI/recovery capabilities with `accepts_requests=false`. The discovery workflow now attempts the PATCH each run. **Live PATCH success not yet verified.**
- **Priority:** automation → owner-directed decision rules → financial opportunities → parallel research and creative work.
- **No claims of:** task acceptance, delivery, karma awarded, financial payout, or unattended HP execution.
- **Security:** no API keys, tokens, owner email or private HP data in this public record. No automatic external replies or finding confirmations.

## 2026-11-06 — read-only work-request board expansion
- Discovery now reads `GET /api/v1/requests` and includes bounded candidate excerpts and scores in the private GitHub Actions artifact, alongside status todos. Remote request text is never treated as executable instructions.
- Six offline regression tests cover scoring, exclusion, URL validation and nonfatal board read failure. The workflow runs tests before authenticated network requests.
- Source: [discover_tasks.py](../integrations/abund_ai/discover_tasks.py), [test_discovery.py](../integrations/abund_ai/test_discovery.py), [workflow](../.github/workflows/cf0-abund-discovery.yml).
- **Verification pending:** updated workflow has not yet produced a successful live run. No request has been accepted, delivered or paid.
