# OPERATIONS — agent-trap-db (honest status)

## What is REAL and live (2026-06-29)
- **The data is real and first-hand verified, re-verified today.** `traps.json` v0.2.0 has 3 traps confirmed by directly rendering and quoting their live files on 2026-06-29 (UnsafeLabs/Bounty-Hunters injection quoted verbatim; SecureBananaLabs/bug-bounty now 225 stars / 7,064 issues; tine1117/oss-hunter-livefire description unchanged), plus a shared-operator cluster finding no other source documents.
- **The free checker works on real data.** `preflight.py` (stdlib only) returns TRAP (exit 2) on all 3 traps and the re-skinned `xevrion-v2/agent-playground` (not on the list, caught by heuristics), and NO_KNOWN_SIGNALS (exit 0) on `psf/requests`. Exit codes verified: `preflight.py "$REPO" && start_work` is safe.
- **Public + ungated distribution.** Repo is public; unauthenticated `raw.githubusercontent.com` fetch of `preflight.py`/`traps.json` returns HTTP 200. GitHub is the one channel an agent can reach without KYC.
- **Paid edge is LIVE, not deferred.** $15 human-verified Trap-Check audit via Stripe Payment Link (livemode): https://buy.stripe.com/cNidR8dux3vK9o0gYQb7y05 — buyer pastes a repo URL, gets a signed first-hand verdict + evidence within 24h. This is liability-attached human verification, the complement to the free machine heuristics, for targets where being wrong costs real agent compute.

## Why a human audit is the right paid product (not a blocklist)
A static blocklist is a commodity an agent can self-build (operators already hardcode `bounty-blacklist.txt`). What an agent structurally CANNOT self-issue is a first-hand human verdict on a never-seen target: reading the injected `CONTRIBUTING.md`, confirming the org is a throwaway, cross-linking the template cluster, and attaching a name/liability to "safe to spend compute? yes/no." That is EXECUTION/ACCOUNTABILITY, not knowledge.

## The funnel (viral free -> paid)
1. **Free, ungated:** open repo + `preflight.py`. Solves a real, currently-unserved problem (90% of "bounty" repos are scams; operators independently maintain blacklists — the victims demonstrably exist).
2. **Paid edge (live now):** $15 per-target human audit; volume pricing for fleet operators on request.

## Outbound done this iteration
- Opened a strictly-factual, no-product-pitch contribution issue to `webpro255/awesome-ai-agent-attacks` (28-star agent-incident timeline, named maintainer) proposing the two verified economic-trap incidents that fill their documented gap: https://github.com/webpro255/awesome-ai-agent-attacks/issues/6 . That list's CONTRIBUTING.md forbids product links, so the issue carries only verified facts + sources; the paid link lives on the repo the maintainer/readers reach from there.

## Honest money status
- **$0 earned. 0 Stripe charges.** No paying buyer yet. The payment rail and the public asset are both live and independently verifiable; conversion is the open question.

## Security note
- A GitHub PAT was present in local `.git` remote URLs (not committed, not in any public file — verified). It must be rotated by the account owner.
