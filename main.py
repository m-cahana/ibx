import geopandas as gpd
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import contextily as ctx
from shapely.geometry import LineString, MultiLineString

# environment variables
load_dotenv()
MAPBOX_TOKEN = os.getenv('MAPBOX_TOKEN')
STYLE_ID = 'michael-cahana/cml9xfkqn002h01sge43w6n0b'

def geometry_to_svg_path(geom, scale_x=1, scale_y=1, offset_x=0, offset_y=0):
    """Convert a shapely geometry to SVG path data"""
    def coords_to_path(coords):
        if not coords:
            return ""
        path = f"M {coords[0][0]*scale_x + offset_x} {-coords[0][1]*scale_y + offset_y}"
        for x, y in coords[1:]:
            path += f" L {x*scale_x + offset_x} {-y*scale_y + offset_y}"
        return path
    
    if isinstance(geom, LineString):
        return coords_to_path(list(geom.coords))
    elif isinstance(geom, MultiLineString):
        return " ".join(coords_to_path(list(line.coords)) for line in geom.geoms)
    return ""

def export_lines_to_svg(subway, ibx, colors_dict, filename='subway_lines_raw.svg'):
    """Export geometries directly to SVG without matplotlib canvas"""
    
    # Get bounds for viewBox
    all_geoms = list(subway.geometry) + list(ibx.geometry)
    minx = min(geom.bounds[0] for geom in all_geoms)
    miny = min(geom.bounds[1] for geom in all_geoms)
    maxx = max(geom.bounds[2] for geom in all_geoms)
    maxy = max(geom.bounds[3] for geom in all_geoms)
    
    width = maxx - minx
    height = maxy - miny
    
    # Start SVG with viewBox
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        f'<g id="subway-lines">'
    ]
    
    # Add subway lines
    for route in subway['route_shor'].unique():
        route_data = subway[subway['route_shor'] == route]
        color = colors_dict.get(route, '#333333')
        svg_lines.append(f'  <g id="route-{route}" stroke="{color}" stroke-width="2.5" fill="none" stroke-opacity="0.9">')
        
        for idx, geom in enumerate(route_data.geometry):
            path_data = geometry_to_svg_path(geom, offset_x=-minx, offset_y=maxy)
            svg_lines.append(f'    <path id="route-{route}-{idx}" d="{path_data}"/>')
        
        svg_lines.append('  </g>')
    
    # Add IBX route
    svg_lines.append(f'  <g id="ibx-route" stroke="#0066FF" stroke-width="5" fill="none" stroke-opacity="0.95">')
    for idx, geom in enumerate(ibx.geometry):
        path_data = geometry_to_svg_path(geom, offset_x=-minx, offset_y=maxy)
        svg_lines.append(f'    <path id="ibx-{idx}" d="{path_data}"/>')
    svg_lines.append('  </g>')
    
    svg_lines.append('</g>')
    svg_lines.append('</svg>')
    
    # Write to file
    with open(filename, 'w') as f:
        f.write('\n'.join(svg_lines))
    
    return width, height, minx, miny, maxx, maxy

# Official NYC Subway colors
SUBWAY_COLORS = {
    '1': '#EE352E',  # Red
    '2': '#EE352E',  # Red
    '3': '#EE352E',  # Red
    '4': '#00933C',  # Green
    '5': '#00933C',  # Green
    '6': '#00933C',  # Green
    '7': '#B933AD',  # Purple
    'A': '#0039A6',  # Blue
    'C': '#0039A6',  # Blue
    'E': '#0039A6',  # Blue
    'B': '#FF6319',  # Orange
    'D': '#FF6319',  # Orange
    'F': '#FF6319',  # Orange
    'M': '#FF6319',  # Orange
    'G': '#6CBE45',  # Light Green
    'J': '#996633',  # Brown
    'Z': '#996633',  # Brown
    'L': '#A7A9AC',  # Gray
    'N': '#FCCC0A',  # Yellow
    'Q': '#FCCC0A',  # Yellow
    'R': '#FCCC0A',  # Yellow
    'W': '#FCCC0A',  # Yellow
    'S': '#808183',  # Dark Gray
}

# read the subway data and ibx geojson
subway = gpd.read_file('data/nyu_2451_34758/routes_nyc_subway_may2016.shp') 
ibx = gpd.read_file('data/ibx.geojson')

# Reproject to Web Mercator (required for basemaps)
subway = subway.to_crs(epsg=3857)
ibx = ibx.to_crs(epsg=3857)

# Create output folder if it doesn't exist
os.makedirs('output', exist_ok=True)

# ====== STEP 0: Export raw SVG paths (no canvas, fully editable in Figma) ======
svg_width, svg_height, minx, miny, maxx, maxy = export_lines_to_svg(subway, ibx, SUBWAY_COLORS, 'output/subway_lines_raw.svg')
print("✓ Saved raw SVG paths: output/subway_lines_raw.svg")

# ====== STEP 1: Create figure and plot lines only (for SVG with canvas) ======
fig, ax = plt.subplots(figsize=(20, 24), dpi=300)

# Plot IBX route in thick blue
ibx.plot(
    ax=ax,
    linewidth=5,
    color='#0066FF',
    alpha=0.95,
    zorder=3
)

# Plot each subway line with its own color
for route in subway['route_shor'].unique():
    route_data = subway[subway['route_shor'] == route]
    color = SUBWAY_COLORS.get(route, '#333333')  # Default to dark gray if route not found
    
    route_data.plot(
        ax=ax,
        linewidth=2.5,
        color=color,
        alpha=0.9,
        zorder=2,
        label=route
    )

# Set axis limits to match raw SVG for alignment
ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)

# Remove axes and save lines-only as SVG
ax.set_axis_off()
fig.savefig('output/subway_lines_only.svg', format='svg', bbox_inches='tight', pad_inches=0)
print("✓ Saved lines-only SVG (with canvas): output/subway_lines_only.svg")

# ====== STEP 2: Create basemap only (for PNG background) ======
fig2, ax2 = plt.subplots(figsize=(20, 24), dpi=300)

# Plot invisible dummy to establish bounds (use subway data to get extent)
subway.plot(ax=ax2, color='none', linewidth=0)

# Set the same axis limits for perfect alignment with raw SVG
ax2.set_xlim(minx, maxx)
ax2.set_ylim(miny, maxy)

# Add Mapbox basemap only
mapbox_url = f'https://api.mapbox.com/styles/v1/{STYLE_ID}/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={MAPBOX_TOKEN}'
ctx.add_basemap(ax2, source=mapbox_url, zoom=12)

# Remove axes and save basemap-only as PNG
ax2.set_axis_off()
fig2.savefig('output/basemap_only.png', dpi=300, bbox_inches='tight', pad_inches=0)
print("✓ Saved basemap-only PNG: output/basemap_only.png")

# ====== STEP 3: Create complete map with lines (for reference) ======
fig3, ax3 = plt.subplots(figsize=(20, 24), dpi=300)

# Plot the lines
ibx.plot(
    ax=ax3,
    linewidth=5,
    color='#0066FF',
    alpha=0.95,
    zorder=3
)

for route in subway['route_shor'].unique():
    route_data = subway[subway['route_shor'] == route]
    color = SUBWAY_COLORS.get(route, '#333333')
    
    route_data.plot(
        ax=ax3,
        linewidth=2.5,
        color=color,
        alpha=0.9,
        zorder=2,
        label=route
    )

# Add Mapbox basemap
ctx.add_basemap(ax3, source=mapbox_url, zoom=12)

# Set the same axis limits for perfect alignment with raw SVG
ax3.set_xlim(minx, maxx)
ax3.set_ylim(miny, maxy)

# Remove axes and save complete map as PNG
ax3.set_axis_off()
fig3.savefig('output/subway_map_complete.png', dpi=300, bbox_inches='tight', pad_inches=0)
print("✓ Saved complete map PNG: output/subway_map_complete.png")

plt.show()