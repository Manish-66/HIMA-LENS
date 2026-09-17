# HIMA-LENS

Run `python convert_xlsx.py` to build the inventory, then `python app.py`.

For Cesium terrain, copy `.env.example` to `.env` in this project folder, then
set `CESIUM_ION_TOKEN=your-token` (no quotes). Restart Flask after saving.
Alternatively set `$env:CESIUM_ION_TOKEN = "your-token"` before starting it.
The 2D Standard layer and 3D OSM imagery need no API key; without the optional
token, 3D still works but uses an ellipsoid instead of high-resolution terrain.

The converter replaces only Mandi records from `landslides_legacy.geojson` with
`data.xlsx`; it retains every non-Mandi legacy feature. The legacy source is not
included in this workspace, so the current export contains the supplied 9,399
Mandi observations until that file is provided.

District outlines come from Esri India's 2024 India Administrative Boundaries
district layer. Run `python districts.py` to verify every inventory coordinate
with point-in-polygon classification. The converter performs the same validation
and stops rather than exporting unmatched or overlapping records.
