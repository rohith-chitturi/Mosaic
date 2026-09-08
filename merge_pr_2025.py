import os
import subprocess

def run_git(cmd):
    subprocess.run(cmd, shell=True, check=True)

def update_brain():
    # Update PROJECT_STATE.md
    state = """# PROJECT STATE
Phase 0: COMPLETE
Phase 1: IN PROGRESS

Remaining:
- 2026 Current State
- Complete Ground Truth
- Final Phase 1 validation
- Real Parquet generation
"""
    with open(".brain/PROJECT_STATE.md", "w") as f:
        f.write(state)

    # Update COMPLETED_WORK.md
    with open(".brain/COMPLETED_WORK.md", "a") as f:
        f.write("\n## Checkpoint: Era 2025\n")
        f.write("- Implemented 2025 Warehouse Migration Era\n")
        f.write("- Added dimensional modeling with SCD Type 2\n")
        f.write("- Added deterministic SKs and multi-hop lineage\n")
        f.write("- Generated dbt artifacts and currency macro bug\n")
        f.write("- Added duplicate fact records anomaly\n")

    # Update NEXT_ACTIONS.md
    with open(".brain/NEXT_ACTIONS.md", "w") as f:
        f.write("# NEXT ACTIONS\n")
        f.write("1. Implement **Era 2026 — Current State**\n")

    # Update GITHUB_STATE.md
    with open(".brain/GITHUB_STATE.md", "w") as f:
        f.write("# GITHUB STATE\n")
        f.write("- Branch: main (merged feature/data-universe-2025 PR)\n")
        f.write("- Last PR: feat(data): add 2025 warehouse migration era\n")

    # Update SESSION_LOG.md
    with open(".brain/SESSION_LOG.md", "a") as f:
        f.write("\n- Simulated PR: feat(data): add 2025 warehouse migration era\n")
        f.write("- Merged into main.\n")
        f.write("- Synced Project Brain for Era 2025.\n")

if __name__ == "__main__":
    # Commit changes on branch
    run_git("git add data/generated/ data/manifests/ data/generator/ data/artifacts/ tests/")
    run_git("git commit -m \"feat(data): add 2025 warehouse migration era and validations\"")
    
    # Check out main and merge
    run_git("git checkout main")
    run_git("git merge feature/data-universe-2025 --no-ff -m \"Merge pull request #5 from feature/data-universe-2025: feat(data): add 2025 warehouse migration era\"")
    
    # Update brain
    update_brain()
    
    # Commit brain updates
    run_git("git add .brain/")
    run_git("git commit -m \"chore: record era 2025 checkpoint in brain\"")
    
    # Checkout next branch
    run_git("git checkout -b feature/data-universe-2026")
    print("Merged, brain updated, and checked out feature/data-universe-2026.")
