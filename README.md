# InaRISK to QGIS

QGIS plugin to download and process disaster spatial data (Hazard, Risk, Vulnerability) directly from the official BNPB InaRISK map services.

![InaRISK to QGIS](inarisktoqgis.png)

## Features

- **BNPB Server Access**: Direct access to BNPB InaRISK ImageServers.
- **Batch Processing**: Download multiple disaster data layers for an Area of Interest (AOI) in a single run.
- **Coordinate Reprojection**: Reprojects AOI vector layers to EPSG:4326 to match the server coordinate reference system.
- **Processing Options**: Pixel noise filtering (sieve), vector polygon conversion, and 3-class index classification (Low, Medium, High).
- **Spatial Planning Mode (Tata Ruang)**: Dedicated workflow producing standardized `KRB` layers with official `Kawasan Rawan Bencana {Bencana} {Kelas}` attributes.
- **Attribute Fields**: Adds `Kelas`, `Value`, and `Source` (with optional access year) attributes to vector outputs.
- **Summary Log**: Process log and summary tracking for each requested disaster layer.
- **Bilingual Interface**: Supports English and Bahasa Indonesia.

## Installation

### Option 1: Install via ZIP
1. Download `inarisk_to_qgis.zip`.
2. Open QGIS.
3. Open **Plugins** -> **Manage and Install Plugins...**
4. Select the **Install from ZIP** tab.
5. Select `inarisk_to_qgis.zip` and click **Install Plugin**.

### Option 2: Manual Installation
Copy or extract the plugin folder into your QGIS python plugins directory:
- **Windows**: `C:\Users\<username>\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
- **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
- **macOS**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`

Restart QGIS or reload plugins.

## Usage

The plugin provides two dedicated menus from the QGIS toolbar and Plugins menu:
1. **InaRISK to QGIS (General)**: Full access to all index types (Hazard, Vulnerability, Risk).
2. **InaRISK for Spatial Planning**: Dedicated spatial planning tool focused on Hazard data, generating official `KRB_{DISASTER}_AR` layers for RTRW and RDTR.

### Configuration Steps
1. **Disasters**: Select individual disaster types or check **Download all types**.
2. **Area Selection**: Select an active layer in your project or browse to an AOI boundary file.
3. **Output Options**:
   - **Output Type**: Choose Raster or Vector Polygons.
   - **Format**: Select format (`.gpkg`, `.shp`, `.geojson`, `.kml`, or `.tif`).
   - **Classification**: Choose *Classify* to categorize into Low, Medium, High (0 - 0.333, 0.333 - 0.667, 0.667 - 1.0), or *Do Not Classify*.
   - **Adjust Gradual Symbology**: Apply gradual thematic colors without borders (Green, Yellow, Red).
   - **Access Year**: Specify the data access year (e.g., 2024) to record in output metadata.
   - **Save Folder**: Select destination folder, or leave empty to create temporary layers in memory.
4. Click **Run**. Progress is displayed in the **Log** tab.

### Attribute Fields
Vector polygon outputs contain:
- `Kelas`: Index class name (e.g., `Indeks Bahaya Banjir Tinggi` or `Kawasan Rawan Bencana Banjir Tinggi`).
- `Value`: Class value range (e.g., `0.667 - 1.0`).
- `Source`: Official attribution (e.g., `InaRISK, Badan Nasional Penanggulangan Bencana (BNPB), Tahun Akses 2024`).

## Disclaimer

This plugin is developed independently by **Juhans** for spatial disaster analysis and is not officially affiliated with BNPB. Data is served directly by the public InaRISK server (gis.bnpb.go.id).

**Author**: Juhans  
**Contact**: [juhans@karpo.work](mailto:juhans@karpo.work)
