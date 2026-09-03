import os

brain_dir = ".brain"
os.makedirs(brain_dir, exist_ok=True)

files = {
    "PROJECT_STATE.md": "# PROJECT_STATE\n\nState: INITIALIZED\nLast Updated: {{timestamp}}\n",
    "CURRENT_PHASE.md": "# CURRENT_PHASE\n\nPhase 0 - Architecture\n",
    "ARCHITECTURE_STATE.md": "# ARCHITECTURE_STATE\n\nInitial architecture pending review.\n",
    "DECISIONS.md": "# DECISIONS\n\n* ADR-001: Project memory via .brain/ established.\n",
    "ROADMAP.md": "# ROADMAP\n\nPhase 0 to Phase 15.\n",
    "TODO.md": "# TODO\n\n- [ ] Complete Architecture Review\n- [ ] Setup initial GitHub actions\n",
    "BLOCKERS.md": "# BLOCKERS\n\nNone.\n",
    "KNOWN_ISSUES.md": "# KNOWN_ISSUES\n\nNone.\n",
    "COMPLETED_WORK.md": "# COMPLETED_WORK\n\n- Repository initialized.\n- .brain/ memory established.\n",
    "NEXT_ACTIONS.md": "# NEXT_ACTIONS\n\n1. Review implementation_plan.md for architecture.\n2. Create GitHub issues corresponding to roadmap.\n",
    "CODEBASE_MAP.md": "# CODEBASE_MAP\n\nCodebase map empty.\n",
    "DATABASE_STATE.md": "# DATABASE_STATE\n\nDatabases not yet provisioned.\n",
    "KAFKA_STATE.md": "# KAFKA_STATE\n\nKafka not yet provisioned.\n",
    "SPARK_STATE.md": "# SPARK_STATE\n\nSpark not yet provisioned.\n",
    "API_STATE.md": "# API_STATE\n\nAPI not yet built.\n",
    "UI_STATE.md": "# UI_STATE\n\nUI not yet built.\n",
    "TEST_STATE.md": "# TEST_STATE\n\nNo tests yet.\n",
    "DEPLOYMENT_STATE.md": "# DEPLOYMENT_STATE\n\nNo deployments yet.\n",
    "GITHUB_STATE.md": "# GITHUB_STATE\n\nInitial setup phase.\n",
    "LESSONS_LEARNED.md": "# LESSONS_LEARNED\n\n",
    "SESSION_LOG.md": "# SESSION_LOG\n\n- **Session 1**: Initialized repository, created README, set up .brain/.\n",
}

for filename, content in files.items():
    with open(os.path.join(brain_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)

print("Created .brain directory and files.")
