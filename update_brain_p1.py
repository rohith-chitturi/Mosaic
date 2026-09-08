import os

updates = {
    ".brain/PROJECT_STATE.md": "# PROJECT_STATE\n\nState: PHASE 1\nPhase: Data Universe\n",
    ".brain/CURRENT_PHASE.md": "# CURRENT_PHASE\n\nPhase 1 — Data Universe\n",
    ".brain/COMPLETED_WORK.md": "# COMPLETED_WORK\n\n- Repository initialized.\n- .brain/ memory established.\n- Phase 0 Architecture designed and approved.\n- Professional README and Architecture Documentation merged to main.\n",
    ".brain/NEXT_ACTIONS.md": "# NEXT_ACTIONS\n\n1. Begin Phase 1: Meridian Commerce Data Universe.\n2. Build deterministic generators for MySQL, Postgres, CSV, JSON.\n",
    ".brain/GITHUB_STATE.md": "# GITHUB_STATE\n\n- Issue #1 (Architecture Foundation): Closed\n- README documentation PR: Merged\n- Next: Create Issue #2 (Meridian Commerce Data Universe)\n",
    ".brain/SESSION_LOG.md": "# SESSION_LOG\n\n- **Session 1**: Initialized repository, created initial README, set up .brain/.\n- **Session 2**: Refined architecture based on feedback (Candidate Generation, Event Model).\n- **Session 3**: Finalized architecture docs in `docs/architecture/`, committed, merged to `main`.\n- **Session 4**: Created complete professional README.md, merged to main, officially closing Phase 0.\n"
}

for filepath, content in updates.items():
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

print("Updated .brain states for Phase 1 transition.")
