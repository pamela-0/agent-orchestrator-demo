# agent-orchestrator — reference demo

A governance layer for AI agents: every risky action goes through a real
approval gate before it runs. This repo is a **reference demo**, not the
product — it shows the real API shape and real behavior, without the
actual engine (mission scoring, evidence verification, consensus voting,
cryptographic audit trail, signed identities) that powers the real thing.

## Try it — 2 minutes, nothing to sign up for

```bash
pip install -r requirements.txt
python server.py
```

That's it. It's running on `http://127.0.0.1:8000`.

**Easiest way to try it:** open this folder in Claude Code (or any AI
coding assistant) and say:

> "Run server.py, then walk me through the examples in README.md and
> show me what happens."

Or run the curl commands yourself:

### A normal action gets approved

```bash
curl -X POST http://127.0.0.1:8000/proposals \
  -H "Content-Type: application/json" \
  -d '{"trigger": "cleanup", "description": "remove an unused dependency"}'
# -> {"id": "...", "status": "pending", "required_role": "engineer", ...}

curl -X POST http://127.0.0.1:8000/proposals/<id>/approve \
  -H "Content-Type: application/json" \
  -d '{"operator": "dana"}'
# -> {"status": "approved", "approved_by": "dana", ...}
```

### A risky action gets blocked by role, automatically

```bash
curl -X POST http://127.0.0.1:8000/proposals \
  -H "Content-Type: application/json" \
  -d '{"trigger": "rotate_key", "description": "rotate the production payment credential"}'
# -> {"id": "...", "required_role": "admin", ...}

curl -X POST http://127.0.0.1:8000/proposals/<id>/approve \
  -H "Content-Type: application/json" \
  -d '{"operator": "dana"}'
# -> 403: 'dana' has role engineer, but this action requires admin — refusing this approval
```

### A claim with no evidence gets flagged

```bash
curl -X POST http://127.0.0.1:8000/proposals \
  -H "Content-Type: application/json" \
  -d '{"trigger": "deploy", "description": "tests confirm this change is safe to deploy"}'
# -> {"flagged_unsubstantiated_claim": true, ...}
```

An agent claiming "tests confirm this is safe" with nothing to back that
claim up is exactly the shape of a hallucination — this gets flagged for
review instead of trusted at face value.

## What the real product adds on top of this

- Real Ed25519-signed operator identities (not a typed name)
- A real, tamper-evident, hash-chained audit trail of every decision
- Real evidence verification (a claim has to point at something
  checkable — a real file, a real prior audit event — not just attached
  JSON that looks plausible)
- Real mission-relevance and prompt-injection-provenance checks
- Multi-tenant plan tiers, real persistence, real deployment tooling

Interested in the real thing? Reach out — [contact info here].

## What this demo is honest about NOT being

This is a simplified reference implementation. The role/evidence checks
above are illustrative keyword matching, not the real engine's actual
logic — good enough to show you the shape of how this works, not a
substitute for it.
