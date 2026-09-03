import os

dirs = [
    "data/generator/core",
    "data/generator/domains",
    "data/generator/eras",
    "data/generator/evolution",
    "data/generator/artifacts",
    "data/generator/exporters",
    "data/generator/manifests",
    "data/generator/validation",
    "data/generated",
    "data/artifacts",
    "data/manifests"
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "__init__.py"), "w") as f:
        pass

print("Generator directories created.")
