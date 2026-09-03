import json
import os
from typing import List, Dict

def export_to_json(data: List[Dict], filepath: str):
    if not data:
        return
    
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
