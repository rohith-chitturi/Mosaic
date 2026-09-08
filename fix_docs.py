import os

def update_known_issues():
    with open(".brain/KNOWN_ISSUES.md", "a") as f:
        f.write("\n## Era 2022 Data Lake Format Limitation\n")
        f.write("The current development environment emits a JSON fallback representation for the 2022 partitioned dataset because valid Parquet generation is not yet available in this environment. Files ending in `.parquet.json` must not be interpreted as valid Apache Parquet files. Real Parquet output remains an open Phase 1 requirement.\n")

def update_readme():
    with open("README.md", "r") as f:
        content = f.read()
    
    # If there's a claim about Parquet, clarify it
    if "Parquet" in content:
        content = content.replace("Parquet format", "simulated Parquet (JSON fallback) format")
        
    with open("README.md", "w") as f:
        f.write(content)

if __name__ == "__main__":
    update_known_issues()
    update_readme()
    print("Documentation updated.")
