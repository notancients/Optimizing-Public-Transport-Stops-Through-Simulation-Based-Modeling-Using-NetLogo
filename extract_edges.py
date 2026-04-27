import osmnx as ox
import pandas as pd
import warnings

warnings.filterwarnings('ignore')



# place_name = "Los Baños, Laguna, Philippines"
# print(f"Fetching network and buildings for {place_name}.")

def fetch_roads(place_name, world_size):
    print("Fetching roads.")
    # Step 1:
    # Fetch road networks and walkways
    
    # 'all' fetches drivable roads AND pedestrian walkways/paths
    G = ox.graph_from_place(place_name, network_type='all', simplify=True)
    nodes, edges = ox.graph_to_gdfs(G)
    edges.to_csv("raw_edges.csv", index=False)
    nodes.to_csv("raw_nodes.csv", index=False)

    # Step 3:
    # Apply proper formatting and scale it so that it works in the size of our NetLogo world
    print("Formatting nodes.")
    nodes_df = nodes.reset_index()[['osmid', 'x', 'y']]

    nodes_df.rename(columns={'osmid': 'node_id', 'x': 'x_coord', 'y': 'y_coord'}, inplace=True)

    # We use the min/max of the nodes to establish the boundary of our NetLogo world
    min_x, max_x = nodes_df['x_coord'].min(), nodes_df['x_coord'].max()
    min_y, max_y = nodes_df['y_coord'].min(), nodes_df['y_coord'].max()

    # Scale nodes to 0-100 grid
    nodes_df['x_coord'] = ((nodes_df['x_coord'] - min_x) / (max_x - min_x)) * world_size
    nodes_df['y_coord'] = ((nodes_df['y_coord'] - min_y) / (max_y - min_y)) * world_size
    nodes_df.to_csv('nodes.csv', index=False)

    # Step 4: 

    edges_df = edges.reset_index()[['u', 'v', 'length', 'highway']]
    edges_df.rename(columns={'u': 'source_node_id', 'v': 'target_node_id', 'length': 'road_length', 'highway': 'road_type'}, inplace=True)

    # Clean up lists in road_type
    edges_df['road_type'] = edges_df['road_type'].apply(lambda x: x[0] if isinstance(x, list) else x)

    print("Saving map image.")

    # This plots the road network and saves it as a high-res JPEG
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


SPECIAL = ["weather_station", "shrine", "civic", "chapel", "veterinary", "townhall", "prison", "place_of_worship", "laboratory", "fire_station", "police", "dentist", "doctors", "studio", "clinic", "childcare", "courthouse", "grave_yard", "health_post", "hospital", ]
SCHOOL = ["university", "school", "research_institute", "prep_school", "library", "lecture_hall", "kindergarten", "college"]
TRANSPORT = ["train_station", "pedicab_terminal", "taxi", "pedicab", "terminal", "bicycle_rental", "bus_station", "air_filling", "bicycle_parking", "parking_space", "parking", "motorcycle_taxi", "motorcycle_parking",]
COMMERCIAL = ["vending_machine","farm_auxiliary", "greenhouse", "warehouse","supermarket", "retail", "office", "industrial", "garages", "garage", "commercial", "clubhouse", "theatre", "restaurant", "money_transfer", "marketplace", "karaoke_box", "internet_cafe", "ice_cream", "bar", "car_wash", "events_venue", "food_court", "fuel", "fast_food", "pharmacy", "bank", "parking", "atm", "pub", "cafe", "gambling", "bureau_de_change", ]
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

def categorize_building(row):
    amenity = str(row.get('amenity', '')).lower()
    
    building_use = str(row.get('building:use', '')).lower()
    building = str(row.get('building', '')).lower()
    landuse = str(row.get('landuse', '')).lower()

    if pd.notna(row.get('house', '')) or pd.notna(row.get('residential', '')):
        return 'residential'
    elif pd.notna(row.get('shop', '')):
        return 'commercial'
    elif pd.notna(row.get('education', '')) or pd.notna(row.get('place_of_worship', '')):
        return 'special'
    
    fields = [amenity, building_use, building, landuse]

    for field in fields:
        if not field:
            continue 

        category = CATEGORY_MAP.get(field)
        if category:
            return category

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
    # Step 2:
    # Fetch buildings and get their 'tags'
    print("Fetching buildings.")
    # tags = {'building': True, 'amenity': ['school', 'college', 'university', 'hospital', 'clinic'], 'highway':'crossing'}
    tags = {
        "building": True,
        "amenity": True,
        "shop": True,
        "office": True,
        "landuse": True,
        "public_transport": True,
        "highway": True
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

    buildings.to_csv('categorized_buildings.csv', index=True)
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















