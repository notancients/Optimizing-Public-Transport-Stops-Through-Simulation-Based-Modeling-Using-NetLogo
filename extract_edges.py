import csv

import osmnx as ox
import pandas as pd
import warnings

warnings.filterwarnings('ignore')


SPEED_MAP = {
    "primary": 50,
    "secondary": 40,
    "tertiary": 30,
    "residential": 20,
    "unclassified": 20,
    "service": 10,
    "track": 10,
    "footway": 5,
    "path": 5,
    "cycleway": 15,
    "steps": 2
}


# place_name = "Los Baños, Laguna, Philippines"
# print(f"Fetching network and buildings for {place_name}.")

def fetch_roads(place_name, world_size):
    print("Fetching roads.")
    # Fetch road networks and walkways
    
    # 'all' fetches drivable roads AND pedestrian walkways/paths
    G = ox.graph_from_place(place_name, network_type='all', simplify=True)
    G = ox.add_edge_speeds(G)
    nodes, edges = ox.graph_to_gdfs(G)
    edges.to_csv("raw_edges.csv", index=False)
    nodes.to_csv("raw_nodes.csv", index=False)

    tags = {
        "public_transport": True,
        "highway": True
    }
    stops = ox.features_from_place(place_name, tags=tags)
    stops = stops[stops[['public_transport', 'highway']].notna().any(axis=1)]
    stops.to_csv('stops.csv', index=True)
    # gdf = gdf[gdf[['col1', 'col2', 'col3']].notna().any(axis=1)]

    # Apply proper formatting and scale it so that it works in the size of our NetLogo world
    print("Formatting nodes.")
    nodes_df = nodes.reset_index()[['osmid', 'x', 'y', 'highway']]

    nodes_df.rename(columns={'osmid': 'node_id', 'x': 'x_coord', 'y': 'y_coord', 'highway':'highway'}, inplace=True)

    # get the boundary of the netlogo world based on the min and max X & Y coordinates
    min_x, max_x = nodes_df['x_coord'].min(), nodes_df['x_coord'].max()
    min_y, max_y = nodes_df['y_coord'].min(), nodes_df['y_coord'].max()

    # scale to world size
    nodes_df['x_coord'] = ((nodes_df['x_coord'] - min_x) / (max_x - min_x)) * world_size
    nodes_df['y_coord'] = ((nodes_df['y_coord'] - min_y) / (max_y - min_y)) * world_size
    nodes_df.to_csv('nodes.csv', index=False)

    edges_df = edges.reset_index()[['u', 'v', 'length', 'highway', 'name', 'oneway', 'speed_kph', 'access', 'lanes']]
    edges_df.rename(columns={
            'u': 'source_node_id', 
            'v': 'target_node_id', 
            'length': 'road_length',
            'highway': 'road_type',
            'speed_kph': 'max_speed',
            'oneway': 'one-way',
            }, 
        inplace=True)

    # Clean up lists in road_type
    edges_df['road_type'] = edges_df['road_type'].apply(lambda x: x[0] if isinstance(x, list) else x)
    edges_df['name'] = edges_df['name'].fillna("Unnamed")
    edges_df['access'] = edges_df['access'].fillna("Uncategorized")
    edges_df['max_speed'] = edges_df['max_speed'].apply(lambda x: round(x, 2))
    
    edges_df.to_csv("edges.csv", index=False)
    print("Saving map image.")

    #Ssave as image for checking
    fig, ax = ox.plot_graph(
        G, 
        show=False, 
        save=True, 
        node_size=0,
        filepath='los_banos_complete_network.jpg', 
        dpi=1000)
    print("Saved los_banos_network.jpg.")

    return {
        'min_x': min_x,
        'max_x': max_x,
        'min_y': min_y,
        'max_y': max_y
    }


SPECIAL = ["utility", "research", "ngo", "government", "foundation", "weather_station", "shrine", "civic", "chapel", "veterinary", "townhall", "prison", "place_of_worship", "laboratory", "fire_station", "police", "dentist", "doctors", "studio", "clinic", "childcare", "courthouse", "grave_yard", "health_post", "hospital", ]
SCHOOL = ["student_union", "educational_institution", "alumni_affairs", "university", "school", "research_institute", "prep_school", "library", "lecture_hall", "kindergarten", "college"]
TRANSPORT = ["train_station", "pedicab_terminal", "taxi", "pedicab", "terminal", "bicycle_rental", "bus_station", "air_filling", "bicycle_parking", "parking_space", "parking", "motorcycle_taxi", "motorcycle_parking",]
COMMERCIAL = ["telecommunication", "travel_agent", "security", "newspaper", "it", "financial", "estate_agent", "courier", "company", "consulting", "cable_television", "administrative", "vending_machine","farm_auxiliary", "greenhouse", "warehouse","supermarket", "retail", "office", "industrial", "garages", "garage", "commercial", "clubhouse", "theatre", "restaurant", "money_transfer", "marketplace", "karaoke_box", "internet_cafe", "ice_cream", "bar", "car_wash", "events_venue", "food_court", "fuel", "fast_food", "pharmacy", "bank", "parking", "atm", "pub", "cafe", "gambling", "bureau_de_change", ]
MISCELLANEOUS = ["public", "guardhouse",  "telephone", "social_facility", "security_booth", "recycling", "post_office", "post_box",  "hut", "community_centre", "conference_centre", "computer","toilets", "bench", "waste_basket", "telephone", "fountain", "auditorium"]
RESIDENTIAL = ["residential", "house", "detached", "dormitory", "shelter", 'apartments']

def build_category_map():
    category_map = {}
    groups = {
        'special': SPECIAL,
        'school': SCHOOL,
        'transport': TRANSPORT,
        'commercial': COMMERCIAL,
        'miscellaneous': MISCELLANEOUS,
        'residential': RESIDENTIAL,
    }
    
    for category, values in groups.items():
        for v in values:
            category_map[v] = category
    return category_map

CATEGORY_MAP = build_category_map()

with open('output.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(CATEGORY_MAP.items())


def categorize_building(row):
    amenity = str(row.get('amenity', '')).lower()
    
    building_use = str(row.get('building:use', '')).lower()
    building = str(row.get('building', '')).lower()
    landuse = str(row.get('landuse', '')).lower()
    office = str(row.get('office', '')).lower()

    if pd.notna(row.get('house', '')) or pd.notna(row.get('residential', '')):
        return 'residential'
    elif pd.notna(row.get('shop', '')):
        return 'commercial'
    elif pd.notna(row.get('education', '')) or pd.notna(row.get('place_of_worship', '')):
        return 'special'
    
    fields = [office, amenity, building_use, building, landuse]

    for field in fields:
        if not field:
            continue 

        category = CATEGORY_MAP.get(field)
        if category:
            return category

    # fallback
    return 'miscellaneous'
    
# Categorize each building
# def categorize_building(row):
#     print(row)
#     amenity = str(row.get('amenity', '')).lower()
#     b_type = str(row.get('building', '')).lower()


    
#     if 'school' in amenity or 'college' in amenity or 'university' in amenity:
#         return 'school'
#     elif 'hospital' in amenity or 'clinic' in amenity:
#         return 'special' # Special zones
#     elif b_type in ['retail', 'commercial', 'supermarket', 'office']:
#         return 'commercial'
#     elif b_type in ['residential', 'house', 'apartments', 'dormitory']:
#         return 'residential'
#     else:
#         return 'residential' # Default for unlabelled

def give_building_names(row):
    name = row.get('name')
    if pd.notna(name):
        return str(name)
    else:
        return 'Unnamed'
    pass

def fetch_nodes(place_name, min_x, max_x, min_y, max_y, world_size):
    # Fetch buildings and get their 'tags'
    print("Fetching buildings.")
    # tags = {'building': True, 'amenity': ['school', 'college', 'university', 'hospital', 'clinic'], 'highway':'crossing'}
    tags = {
        "building": True,
        "amenity": True,
        "shop": True,
        "office": True,
        "landuse": True,
    }
    buildings = ox.features_from_place(place_name, tags=tags)

    # Step 5:
    # Format and scale buildings

    print("Formatting buildings.")
    # Get centroid of each building
    buildings = buildings.copy()
    buildings['centroid'] = buildings.geometry.centroid
    buildings['x'] = buildings['centroid'].x
    buildings['y'] = buildings['centroid'].y

    buildings.to_csv('raw_buildings.csv', index=False)
    print(buildings)

    buildings['category'] = buildings.apply(categorize_building, axis=1)
    buildings['name'] = buildings.apply(give_building_names, axis=1)

    # buildings.to_csv('categorized_buildings.csv', index=True)
    # Extract only the data we need
    buildings_df = buildings[['name', 'x', 'y', 'category']].copy()


    # Scale buildings to line up with the roads
    buildings_df['x_coord'] = ((buildings_df['x'] - min_x) / (max_x - min_x)) * world_size
    buildings_df['y_coord'] = ((buildings_df['y'] - min_y) / (max_y - min_y)) * world_size

    # Drop the unnecessary raw lat/long columns and save
    buildings_df = buildings_df[['name', 'x_coord', 'y_coord', 'category']]
    buildings_df.insert(0, "bldg_id", range(len(buildings_df)))
    buildings_df.to_csv('buildings.csv', index=False)

    print("Finished fetching buildings.")















