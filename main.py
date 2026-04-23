from population import *
from extract_edges import *

WORLD_SIZE = 100
PLACE_NAME = "Los Baños, Laguna, Philippines"


def main():
  world_coords = fetch_roads(place_name=PLACE_NAME, world_size=WORLD_SIZE)

  buildings = fetch_buildings(place_name=PLACE_NAME, world_size=WORLD_SIZE,
                              min_x=world_coords["min_x"], max_x=world_coords["max_x"],
                              min_y=world_coords["min_y"], max_y=world_coords["max_y"]
                              )
  
  # Reference: https://psa.gov.ph/philippine-statistical-yearbook/year/2020
  calabarzon_age_distribution = {
  "15-19":	 1474716, 
  "20-24":	 1511748, 
  "25-29":	 1433847, 
  "30-34":	 1299787, 
  "35-39":	 1183643, 
  "40-44":	 1066537, 
  "45-49":	 873461, 
  "50-54":	 760023, 
  "55-59":	 620045, 
  "60-64":	 500453, 
  "65-69":	 344340, 
  "70-74":	 217671, 
  "75-79":	 117824, 
  "80-100":	 115120
  }

  # Reference: https://psa.gov.ph/philippine-statistical-yearbook/year/2020
  calabarzon_total_population = sum(calabarzon_age_distribution.values())


  # Reference: https://losbanos.gov.ph/facts
  # Total population of Los Banos over the age of 15 
  los_banos_total_population = 81686
  los_banos_calabarzon_ratio = los_banos_total_population/calabarzon_total_population

  maximum_population = 1000

  los_banos_age_distribution = {k: math.floor(v*los_banos_calabarzon_ratio) for k,v in calabarzon_age_distribution.items()}
  max_pop_adjusted_distribution = {k: math.floor(v/1000) for k,v in los_banos_age_distribution.items()}
  # print("UPDATED", sum(los_banos_age_distribution.values()))
  # print("Los Banos Age Distribution", los_banos_age_distribution)

  print("GENERATING POPULATION")
  generate_population(maximum_population, max_pop_adjusted_distribution, 
                      wait_tol_min=20, wait_tol_max=60,
                      dist_tol_min=100, dist_tol_max=200,
                      transpo_pref_min=0.3, transpo_pref_max=0.5,
                      unruliness_min=0.1, unruliness_max=0.7,
                      jaywalking_min=0.8, jaywalking_max=0.9,
                      allelomimetic_min=0.0, allelomimetic_max=0.2,
                      world_coords=world_coords, world_size=WORLD_SIZE, seed=67)
  pass

if __name__ == "__main__":
  main()