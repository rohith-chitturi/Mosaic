import argparse
from data.generator.domains.universe import DataUniverse
from data.generator.eras.era_2016 import Era2016
from data.generator.eras.era_2018 import Era2018
from data.generator.eras.era_2020 import Era2020
from data.generator.eras.era_2022 import Era2022
from data.generator.manifests.ground_truth import generate_ground_truth
import os

def main():
    parser = argparse.ArgumentParser(description="Meridian Commerce Data Generator")
    parser.add_argument("--scale", type=str, default="small", choices=["small", "medium", "large", "benchmark"])
    parser.add_argument("--seed", type=int, default=42)
    
    args = parser.parse_args()
    
    print(f"Initializing universe (Scale: {args.scale}, Seed: {args.seed})")
    universe = DataUniverse(seed=args.seed, scale=args.scale)
    universe.generate()
    
    # Next step: apply eras and export
    output_dir = "data/generated"
    
    era_2016 = Era2016(universe, output_dir)
    era_2016.generate()
    
    era_2018 = Era2018(universe, output_dir)
    era_2018.generate()
    
    era_2020 = Era2020(universe, output_dir)
    era_2020.generate()
    
    era_2022 = Era2022(universe, output_dir)
    era_2022.generate()
    
    generate_ground_truth(universe, os.path.join("data", "manifests"))
    print("Generated ground truth in data/manifests/")
    
if __name__ == "__main__":
    main()
