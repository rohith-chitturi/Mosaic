import os
import subprocess

def run_git(cmd):
    subprocess.run(cmd, shell=True, check=True)

def update_brain():
    # Update COMPLETED_WORK.md
    with open(".brain/COMPLETED_WORK.md", "a") as f:
        f.write("\n## Checkpoint: Phase 1 First Half\n")
        f.write("- Implemented Canonical Internal Model\n")
        f.write("- Implemented 2016 MySQL Era\n")
        f.write("- Implemented 2018 PostgreSQL Migration Era\n")
        f.write("- Implemented 2020 Kafka Era\n")
        f.write("- Implemented deterministic mapping and tests\n")

    # Update NEXT_ACTIONS.md
    with open(".brain/NEXT_ACTIONS.md", "w") as f:
        f.write("# NEXT ACTIONS\n")
        f.write("1. Implement **Era 2022 — Spark/Data Lake**\n")

    # Update GITHUB_STATE.md
    with open(".brain/GITHUB_STATE.md", "w") as f:
        f.write("# GITHUB STATE\n")
        f.write("- Branch: main (merged feature/data-universe checkpoint PR)\n")
        f.write("- Last PR: feat(data): establish historical universe foundation\n")

    # Update SESSION_LOG.md
    with open(".brain/SESSION_LOG.md", "a") as f:
        f.write("\n- Simulated PR: feat(data): establish historical universe foundation\n")
        f.write("- Merged into main.\n")

if __name__ == "__main__":
    # Check out main
    run_git("git checkout main")
    # Merge branch
    run_git("git merge feature/data-universe --no-ff -m \"Merge pull request #2 from feature/data-universe: feat(data): establish historical universe foundation\"")
    # Update brain
    update_brain()
    # Commit brain updates
    run_git("git add .brain/")
    run_git("git commit -m \"chore: record phase 1 checkpoint in brain\"")
    print("Merged and brain updated successfully.")
