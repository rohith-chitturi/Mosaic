import os
import csv
from typing import List, Dict

def export_to_csv(data: List[Dict], filepath: str):
    if not data:
        return
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    keys = data[0].keys()
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)
