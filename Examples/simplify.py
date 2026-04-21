import osmnx as ox
import matplotlib.pyplot as plt

# --- 1. Define area ---
place_name = "Piedmont, California, USA"

# --- 2. Fetch street network ---
G = ox.graph_from_place(place_name, network_type='drive')  # change 'drive' to 'walk' or 'bike' if needed

# --- 3. Plot original network ---
fig1, ax1 = ox.plot_graph(G, node_size=10, edge_color='gray', show=False, close=False)
fig1.savefig("original_network.png", dpi=300)
plt.close(fig1)
print("Saved original_network.png")

# --- 4. Simplify network ---
# G_simplified = ox.simplify_graph(G)

# # --- 5. Plot simplified network ---
# fig2, ax2 = ox.plot_graph(G_simplified, node_size=10, edge_color='blue', show=False, close=False)
# fig2.savefig("simplified_network.png", dpi=300)
# plt.close(fig2)
# print("Saved simplified_network.png")