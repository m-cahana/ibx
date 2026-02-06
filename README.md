# NYC Subway + IBX Route Visualization

Generates map visualizations of NYC subway lines and the proposed Interborough Express (IBX) route.

## Data Sources

- **Subway lines**: NYU Spatial Data Repository ([routes_nyc_subway_may2016](https://geo.nyu.edu/catalog/nyu_2451_34758))
- **IBX route**: Extracted from [Overpass Turbo](https://overpass-turbo.eu/) with query:
  ```
  [bbox:{{bbox}}];
  (
    way["railway"="rail"]["name"="Bay Ridge Branch"];
    way["railway"="rail"]["name"="Fremont Secondary"];
    way["railway"="rail"]["name"~"Fremont"];
    way["railway"="rail"]["operator"="New York and Atlantic Railway"];
    way["railway"="rail"]["operator"="CSX Transportation"];
  );
  out geom;
  ```
- **LIRR lines**: Extracted from [Overpass Turbo](https://overpass-turbo.eu/) with query:
  ```
  [out:json][timeout:25];
  (
    way["railway"="rail"]["operator"~"Long Island Rail Road|LIRR",i]({{bbox}});
    relation["railway"="rail"]["operator"~"Long Island Rail Road|LIRR",i]({{bbox}});
    way["railway"="rail"]["name"~"Main Line|Port Washington",i]({{bbox}});
    relation["railway"="rail"]["name"~"Main Line|Port Washington",i]({{bbox}});
    way["railway"="rail"]["network"="Long Island Rail Road"]({{bbox}});
    relation["railway"="rail"]["network"="Long Island Rail Road"]({{bbox}});
  );
  out geom;
  ```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create `.env` file with Mapbox token:
   ```
   MAPBOX_TOKEN=your_token_here
   ```

3. Run the script:
   ```bash
   python main.py
   ```

## Outputs

All files are saved to the `output/` folder:
- `subway_lines_raw.svg` - Raw SVG paths (Figma-editable)
- `subway_lines_only.svg` - Lines with matplotlib canvas
- `basemap_only.png` - Mapbox basemap layer
- `subway_map_complete.png` - Complete map with basemap + lines
