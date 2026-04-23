import copy
import math
import random
import pandas as pd
import osmnx as ox

  # destination-node
  # route
  # speed
  # max-capacity
  # current-capacity
  # is-public?          ; previously category, switched to boolean for cheaper calculations
  # unruliness
  # boarding-time
  # alighting-time
  # dwell-time

def generate_private_vehicles(private_vehicle_amount):
  vehicle_type = ["car", "truck", "motorcycle", "tricycle"]

  types = [random.sample(vehicle_type, 1) for _ in range(private_vehicle_amount)]

  pass

def generate_public_transport():
  pass