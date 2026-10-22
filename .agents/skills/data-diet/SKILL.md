---
name: data-diet
description: "Use whenever dealing with large spatial datasets, GeoJSON files > 250KB, shapefiles, Excel sheets, or multi-megabyte repositories. Enforces strict context-window protection by forbidding full-file ingestion, mandating sample slicing, JSONPath extraction, and memory-mapped queries."
---

# Data Diet & Context Token Protection

This skill guards against blowing the 100k+ token context window when interacting with spatial or tabular datasets in HIMA-LENS (e.g. `landslides_clean.geojson` [6.1MB], `old_data.geojson` [11MB], `data.xlsx` [14,190 rows]).

## 1. Absolute Ingestion Ban

*   **NEVER** run `read_file` or print the entirety of any file over `250 KB`.
*   Reading a 6MB GeoJSON dumps ~1.5 million characters into context, exhausting context capacity, slowing down reasoning, and risking truncation.

## 2. Permitted Extraction Patterns

Instead of reading the raw file, use one of the following progressive inspection techniques:

### Pattern A: Fast CLI Slicer
Use the included `slice_data.py` helper to inspect schema and sample records without token cost:
```powershell
# Inspect schema and 2 sample features:
python .agents/skills/data-diet/scripts/slice_data.py landslides_clean.geojson --head 2

# Inspect specific property distribution:
python .agents/skills/data-diet/scripts/slice_data.py landslides_clean.geojson --stats district
```

### Pattern B: GeoPandas / Pyogrio Stream
If using Python, never load all attributes if you only need columns or summary statistics:
```python
import geopandas as gpd

# Read only schema without loading records:
schema = gpd.read_file("landslides_clean.geojson", rows=2)
print(schema.columns)
print(schema.dtypes)
```

### Pattern C: Tailored Filter Queries
Filter before loading:
```python
# Read only features matching a specific district:
gdf = gpd.read_file("landslides_clean.geojson", where="district = 'Mandi'")
```

## 3. Safe Verification Reflex
When asked "What columns are in this GeoJSON?" or "Why is a property missing?", inspect 1-2 features or run `slice_data.py`, never the whole dataset.
