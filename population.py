import copy
import math
import random
import pandas as pd
import osmnx as ox



# destination-node 
# route
# age
# house
# work-school
# allelomimetic
# distance-walked
# walking-time
# waiting-tolerance
# distance-tolerance
# mode-preference
# unruliness
# jaywalking

# Walking speed in kilometers per hour
# Reference: 
# https://www.researchgate.net/publication/344166318_Walkability_Index_for_Elderly_Health_A_Proposal
# https://www.medicalnewstoday.com/articles/average-walking-speed

# WALKING_SPEED = {
#   "20-29": 4.85918,
#   "30-39": 4.9879,
#   "40-49": 5.076395,
#   "50-59": 4.931585,
#   "60-69": 4.641965,
#   "70-79": 4.304075,
#   "80-89": 3.435215
# }

WALKING_SPEED_KMH = {
  29: 4.85918,
  39: 4.9879,
  49: 5.076395,
  59: 4.931585,
  69: 4.641965,
  79: 4.304075,
  89: 3.435215
}

def sample_age(age_distribution):
    groups = list(age_distribution.keys())
    weights = list(age_distribution.values())
    age_group = random.choices(groups, weights=weights, k=1)[0]
    [age_min, age_max] = age_group.split("-")
    age = random.randint(int(age_min), int(age_max))
    return age

def determine_speed(age):
  if age <= 29: return WALKING_SPEED_KMH[29]
  elif age <= 39: return WALKING_SPEED_KMH[39]
  elif age <= 49: return WALKING_SPEED_KMH[49]
  elif age <= 59: return WALKING_SPEED_KMH[59]
  elif age <= 69: return WALKING_SPEED_KMH[69]
  elif age <= 79: return WALKING_SPEED_KMH[79]
  else: return WALKING_SPEED_KMH[89]

def calculate_netlogo_speed(age, min_x, max_x, min_y, max_y, world_size):
  speed = determine_speed(age)
  m_s = speed*(1000/3600)
  map_width_meters = ox.distance.great_circle(min_y, min_x, min_y, max_x)

  meters_per_patch = map_width_meters / world_size
  patches_per_tick = m_s/meters_per_patch

  return round(patches_per_tick, 5)


def generate_population(total_population,age_distribution, 
                        wait_tol_min, wait_tol_max, dist_tol_min, dist_tol_max,
                        transpo_pref_min, transpo_pref_max, 
                        unruliness_min, unruliness_max,
                        jaywalking_min, jaywalking_max,
                        allelomimetic_min, allelomimetic_max,
                        world_coords, world_size, seed):
  print("Generating population.")
  building_df = pd.read_csv('buildings.csv')
  # print(building_df)

  residential = building_df.loc[building_df["category"] == "residential", "bldg_id"].values
  commercial = building_df.loc[building_df["category"] == "commercial", "bldg_id"].values
  school = building_df.loc[building_df["category"] == "school", "bldg_id"].values

  groups = list(age_distribution.keys())
  weights = list(age_distribution.values())

  age_groups = random.choices(groups, weights=weights, k=total_population)

  age_ranges = [g.split("-") for g in age_groups]

  ages = [random.randint(int(a), int(b)) for a, b in age_ranges]

  house_ids = random.choices(residential, k=total_population)

  work_school_ids = [
    random.choice(school if age < 20 else commercial)
    for age in ages
  ]

  waiting = [random.randint(wait_tol_min, wait_tol_max) for _ in range(total_population)]
  distance = [random.randint(dist_tol_min, dist_tol_max) for _ in range(total_population)]
  unruliness = [round(random.uniform(unruliness_min, unruliness_max),2) for _ in range(total_population)]
  jaywalking = [round(random.uniform(jaywalking_min, jaywalking_max),2) for _ in range(total_population)]
  allelomimetic = [round(random.uniform(allelomimetic_min, allelomimetic_max),2) for _ in range(total_population)]
  transportation_preference = [round(random.uniform(transpo_pref_min, transpo_pref_max),2) for _ in range(total_population)]
  speed = [calculate_netlogo_speed(age, min_x=world_coords["min_x"], min_y=world_coords["min_y"], max_x=world_coords["max_x"], max_y=world_coords["max_y"], world_size=world_size) for age in ages]

  population_df = pd.DataFrame({
      "age": ages,
      "house_id": house_ids,
      "workSchool_id": work_school_ids,
      "waitingTolerance": waiting,
      "distanceTolerance": distance,
      "transportation_preference": transportation_preference,
      "unruliness": unruliness,
      "jaywalking": jaywalking,
      "speed": speed,
      "allelomimetic": allelomimetic,
  })

  population_df.to_csv("pedestrians.csv", index=False)
  print(population_df)

  pass

