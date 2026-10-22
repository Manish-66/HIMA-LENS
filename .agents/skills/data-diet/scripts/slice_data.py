"""
Data Diet CLI Slicer: Inspects large GeoJSON and tabular files safely without blowing LLM context.
"""
import sys
import json
import argparse
from collections import Counter

def slice_geojson(filepath, head=2, stats_field=None):
    with open(filepath, 'r', encoding='utf-8') as f:
        # Load JSON (efficient in native C backend)
        data = json.load(f)

    features = data.get("features", [])
    total = len(features)
    print(f"=== [DATA-DIET] Dataset Summary for {filepath} ===")
    print(f"Total Features: {total:,}")

    if total > 0:
        first_feat = features[0]
        props = first_feat.get("properties", {})
        print(f"Geometry Type : {first_feat.get('geometry', {}).get('type')}")
        print(f"Property Keys ({len(props)}): {list(props.keys())}")

    if stats_field:
        values = [feat.get("properties", {}).get(stats_field) for feat in features]
        counts = Counter(values).most_common(10)
        print(f"\n--- Distribution for '{stats_field}' (Top 10) ---")
        for val, cnt in counts:
            print(f"  {val}: {cnt:,} ({(cnt/total)*100:.1f}%)")

    if head > 0:
        print(f"\n--- Head Sample ({min(head, total)} features) ---")
        for i in range(min(head, total)):
            print(json.dumps(features[i], indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Safely inspect large GeoJSON files without context explosion")
    parser.add_argument("file", help="Path to GeoJSON file")
    parser.add_argument("--head", type=int, default=1, help="Number of features to print (default: 1)")
    parser.add_argument("--stats", type=str, default=None, help="Property field to calculate distribution for")

    args = parser.parse_args()
    slice_geojson(args.file, head=args.head, stats_field=args.stats)
