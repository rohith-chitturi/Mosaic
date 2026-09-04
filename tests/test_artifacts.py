import sys
import os
import ast

def validate_spark_artifact():
    print("Running Spark AST Validation...")
    spark_script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'artifacts', 'spark', 'customer_enrichment.py'))
    
    if not os.path.exists(spark_script_path):
        print("Spark script not found, skipping or failed.")
        return
        
    with open(spark_script_path, "r", encoding="utf-8") as f:
        source_code = f.read()
        
    try:
        tree = ast.parse(source_code)
        # Just simple validation that it parses and contains Spark references
        has_sparksession = False
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module == 'pyspark.sql':
                has_sparksession = True
        assert has_sparksession, "PySpark artifact does not import pyspark.sql"
        print("Spark AST Validation passed.")
    except SyntaxError as e:
        assert False, f"Syntax error in Spark artifact: {e}"

if __name__ == "__main__":
    validate_spark_artifact()
