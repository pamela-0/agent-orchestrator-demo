"""agent-orchestrator — reference demo server.

This is NOT the real governance engine. It shows the real API contract
(the exact request/response shapes) and the real BEHAVIOR a caller
sees, without any of the actual decision logic behind it (mission
scoring, evidence verification, consensus voting, audit-chain hashing,
signature verification, etc. all live in the private engine).

Run it locally:

    pip install -r requirements.txt
    python server.py

Then try the examples in README.md, or just point your AI assistant
at this file and this README and ask it to run through them for you.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

app = FastAPI(title="agent-orchestrator — reference demo")

# A rough, illustrative stand-in for the real engine's role classifier.
# The real one is a real content classifier over the full action, not
# a keyword list -- this is deliberately simplified.
_ADMIN_KEYWORDS = ("rotate", "delete", "credential", "payment", "production", "secret")

# A rough, illustrative stand-in for the real evidence-binding check.
# The real one is a real regex over evidence-citing phrasing plus real
# verification of attached evidence against a real audit chain / real
# filesystem -- this only demonstrates the SHAPE of that behavior.
_EVIDENCE_PHRASES = ("tests confirm", "verified", "the logs show", "as documented")


@dataclass
class Proposal:
    id: str
    trigger: str
    description: str
    status: str = "pending"
    required_role: str = "engineer"
    required_approvals: int = 1
    approvals: list[str] = field(default_factory=list)
    flagged_unsubstantiated_claim: bool = False
    approved_by: str | None = None
    rejected_reason: str | None = None


_PROPOSALS: dict[str, Proposal] = {}


class ProposeRequest(BaseModel):
    trigger: str
    description: str
    evidence: list[dict] | None = None


class ApproveRequest(BaseModel):
    operator: str


class RejectRequest(BaseModel):
    reason: str


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return (
        "<h1>agent-orchestrator — reference demo</h1>"
        "<p>This is a reference server, not the real engine. See README.md.</p>"
        "<p>Try: <code>POST /proposals</code>, <code>GET /proposals</code>, "
        "<code>POST /proposals/{id}/approve</code>.</p>"
    )


@app.post("/proposals", status_code=201)
def propose(body: ProposeRequest) -> Proposal:
    description_lower = body.description.lower()
    role_needed = "admin" if any(k in description_lower for k in _ADMIN_KEYWORDS) else "engineer"
    claims_evidence = any(phrase in description_lower for phrase in _EVIDENCE_PHRASES)
    has_real_evidence = bool(body.evidence)

    proposal = Proposal(
        id=str(uuid.uuid4()),
        trigger=body.trigger,
        description=body.description,
        required_role=role_needed,
        flagged_unsubstantiated_claim=claims_evidence and not has_real_evidence,
    )
    _PROPOSALS[proposal.id] = proposal
    return proposal


@app.get("/proposals")
def list_pending() -> list[Proposal]:
    return [p for p in _PROPOSALS.values() if p.status == "pending"]


@app.get("/proposals/{proposal_id}")
def get_proposal(proposal_id: str) -> Proposal:
    proposal = _PROPOSALS.get(proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="no such proposal")
    return proposal


_ROLE_RANK = {"engineer": 1, "admin": 2}


@app.post("/proposals/{proposal_id}/approve")
def approve(proposal_id: str, body: ApproveRequest) -> Proposal:
    proposal = _PROPOSALS.get(proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="no such proposal")
    if proposal.status != "pending":
        raise HTTPException(status_code=409, detail=f"proposal is already {proposal.status}")

    # Illustrative only -- the real engine checks a real, signed operator
    # role from a real identity registry, never a typed name's own claim.
    operator_role = "admin" if "admin" in body.operator.lower() else "engineer"
    if _ROLE_RANK[operator_role] < _ROLE_RANK[proposal.required_role]:
        raise HTTPException(
            status_code=403,
            detail=(
                f"'{body.operator}' has role {operator_role}, but this action requires "
                f"{proposal.required_role} — refusing this approval"
            ),
        )

    proposal.approvals.append(body.operator)
    if len(proposal.approvals) >= proposal.required_approvals:
        proposal.status = "approved"
        proposal.approved_by = body.operator
    return proposal


@app.post("/proposals/{proposal_id}/reject")
def reject(proposal_id: str, body: RejectRequest) -> Proposal:
    proposal = _PROPOSALS.get(proposal_id)
    if proposal is None:
        raise HTTPException(status_code=404, detail="no such proposal")
    proposal.status = "rejected"
    proposal.rejected_reason = body.reason
    return proposal


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
