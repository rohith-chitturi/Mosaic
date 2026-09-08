import sys
import os
import ast

def validate_spark_artifact(script_name):
    print(f"Running Spark AST Validation on {script_name}...")
    spark_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'artifacts', 'spark', script_name))
    
    if not os.path.exists(spark_script_path):
        print(f"Spark script {script_name} not found, skipping or failed.")
        return
        
    with open(spark_script_path, "r", encoding="utf-8") as f:
        source_code = f.read()
        
    try:
        tree = ast.parse(source_code)
        has_sparksession = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == 'pyspark.sql':
                has_sparksession = True
        assert has_sparksession, f"{script_name} does not import pyspark.sql"
        print(f"Spark AST Validation passed for {script_name}.")
    except SyntaxError as e:
        assert False, f"Syntax error in {script_name}: {e}"

if __name__ == "__main__":
    validate_spark_artifact("customer_enrichment.py")
    validate_spark_artifact("historical_backfill_2024.py")
