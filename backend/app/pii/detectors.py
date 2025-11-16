import re
import yaml

with open("app/pii/registry.yaml") as f:
    REGISTRY = yaml.safe_load(f)

def detect_pii(text):
    results = []
    for id_type, props in REGISTRY.items():
        pattern = re.compile(props["regex"])
        for match in pattern.finditer(text):
            results.append({
                "type": id_type,
                "value": match.group(),
                "start": match.start(),
                "end": match.end()
            })
    return results
