import logging
import osmnx as ox
import numpy as np
from shapely.geometry import LineString, Point

ox.settings.log_console = True
ox.settings.log_level = "INFO"
logging.basicConfig(level=logging.INFO)

# ============================================================
# CONFIG
# ============================================================
WORLD_WIDTH = 200
WORLD_HEIGHT = 200


# ============================================================
# 1. DOWNLOAD OSM NETWORK
# ============================================================
# left bottom right top
def get_osm_graph(north, south, east, west):
    bbox = (west, south, east, north)
    G = ox.graph_from_bbox(
      bbox,
      network_type="drive"
    )
    return G


# ============================================================
# 2. COORDINATE CONVERSION (lat/lon → patch px/py)
# ============================================================
def latlon_to_patch(lat, lon, north, south, east, west):
    px = (lon - west) / (east - west) * WORLD_WIDTH - (WORLD_WIDTH / 2)
    py = (lat - south) / (north - south) * WORLD_HEIGHT - (WORLD_HEIGHT / 2)
    return int(round(px)), int(round(py))


# ============================================================
# 3. RASTERIZE A LINE INTO PATCHES
# ============================================================
def rasterize_line(p1, p2):
    (x1, y1), (x2, y2) = p1, p2
    points = []

    # Bresenham-like: sample at small increments
    steps = max(abs(x2 - x1), abs(y2 - y1), 1)
    for i in range(steps + 1):
        t = i / steps
        x = int(round(x1 + (x2 - x1) * t))
        y = int(round(y1 + (y2 - y1) * t))
        points.append((x, y))

    return points


# ============================================================
# 4. MAIN: CONVERT OSM → PATCH LIST
# ============================================================
def osm_to_patches(north, south, east, west):
    print("Converting into patches")
    G = get_osm_graph(north, south, east, west)

    road_patches = set()
    node_map = {}
    edge_list = []

    # Convert node coordinates
    for node_id, data in G.nodes(data=True):
        lat = data['y']
        lon = data['x']
        px, py = latlon_to_patch(lat, lon, north, south, east, west)
        node_map[node_id] = (px, py)

    # Rasterize edges
    for u, v, data in G.edges(data=True):
        edge_list.append([u, v])

        # Road geometry: either a LineString or create from nodes
        if 'geometry' in data:
            coords = list(data['geometry'].coords)
        else:
            # straight line between nodes
            coords = [
                (G.nodes[u]['x'], G.nodes[u]['y']),
                (G.nodes[v]['x'], G.nodes[v]['y'])
            ]

        # Convert each point into patches
        patch_points = []
        for lon, lat in coords:
            px, py = latlon_to_patch(lat, lon, north, south, east, west)
            patch_points.append((px, py))

        # Rasterize consecutive segments
        for i in range(len(patch_points) - 1):
            p1 = patch_points[i]
            p2 = patch_points[i + 1]
            segment = rasterize_line(p1, p2)
            road_patches.update(segment)

    # Convert set → list
    road_patches = list(road_patches)

    return {
        "world_width": WORLD_WIDTH,
        "world_height": WORLD_HEIGHT,
        "road_patches": road_patches,
        "node_map": node_map,
        "edge_list": edge_list
    }


# ============================================================
# USAGE EXAMPLE
# ============================================================
if __name__ == "__main__":
    print("Running main")
    north = 14.138477
    south = 14.247168
    east = 121.127798
    west = 121.263329
    # get_osm_graph(north=north, south=south, east=east, west=west)
    # 121.127798,14.138477,121.263329,14.247168 # Calamba and Los Banos only

    out = osm_to_patches(north, south, east, west)
    print("Total patch roads:", len(out["road_patches"]))
