#%%
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage
import matplotlib.pyplot as plt
import seaborn as sns

# Input and Output Paths
input_path = "/home/covmo/test_ian/pu_rule_r/vil/mum_nt_rrc.csv"
output_path = "/home/covmo/test_ian/pu_rule_r/vil/output_mum_1.tsv"

# rrc_cnt = 'RRC_CNT'

# Load Data
# df = pd.read_csv(input_path, sep="\t")
df = pd.read_csv(input_path)
coordinates = df[['LONGITUDE', 'LATITUDE']].values
rrc_values = df['RRC_CNT'].values

# Parameters
linkage_methods = ['ward', 'average', 'single', 'complete']
thresh_initial = 420_000_000
thresh_group = 380_000_000

# Initialize Variables
all_filtered_groups = []
group_id = 1
output_data = pd.DataFrame()

# Define TreeNode Class
class TreeNode:
    def __init__(self, node_id, rrc_sum=0, distance=None, lon=None, lat=None, children=None):
        self.node_id = node_id
        self.rrc_sum = rrc_sum
        self.distance = distance
        self.lon = lon
        self.lat = lat
        self.children = children or []

# Define Helper Functions
def collect_leaf_nodes(node):
    if node.lon is not None and node.lat is not None:
        return [node]
    leaves = []
    for child in node.children:
        leaves.extend(collect_leaf_nodes(child))
    return leaves

def group_tree(node, threshold):
    groups = []

    def traverse(n):
        if n.rrc_sum < threshold:
            groups.append(collect_leaf_nodes(n))
            return
        if n.children:
            for child in n.children:
                traverse(child)

    traverse(node)
    return groups

def filter_and_store_groups(groups, threshold):
    filtered_groups = []
    remaining_leaves = []

    for group in groups:
        group_rrc_sum = sum(leaf.rrc_sum for leaf in group)
        if group_rrc_sum > threshold:
            filtered_groups.append(group)
        else:
            remaining_leaves.extend(group)

    return filtered_groups, remaining_leaves

def assign_group_ids_and_save(groups, start_group_id):
    data = []
    group_id = start_group_id

    for group in groups:
        for leaf in group:
            data.append({
                "LONGITUDE": leaf.lon,
                "LATITUDE": leaf.lat,
                "GROUP": group_id
            })
        group_id += 1

    return pd.DataFrame(data), group_id

def plot_groups_with_highlight(groups, threshold):
    plt.figure(figsize=(50, 30))
    highlight_colors = sns.color_palette("tab10", len(groups))
    gray_color = (0.8, 0.8, 0.8)

    color_idx = 0
    for i, group in enumerate(groups):
        group_rrc_sum = sum(leaf.rrc_sum for leaf in group)
        lons = [leaf.lon for leaf in group]
        lats = [leaf.lat for leaf in group]

        if group_rrc_sum > threshold:
            color = highlight_colors[color_idx]
            color_idx += 1
            label = f"Group {i + 1}: RRC Sum = {group_rrc_sum:,}"
        else:
            color = gray_color
            label = None

        plt.scatter(lons, lats, label=label, color=color, s=24)

    plt.title(f"Groups with Highlighted RRC Sum > {threshold:,}")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend(title="Highlighted Groups")
    plt.grid(True)
    plt.show()

def print_dendrogram(linkage_matrix, df, method):
    sns.set(style="whitegrid")
    plt.figure(figsize=(24, 16))
    dendrogram(linkage_matrix, labels=None, leaf_rotation=90, leaf_font_size=10)
    plt.title(f"Hierarchical Clustering Dendrogram_{method}")
    plt.xlabel("ENODEB_ID")
    plt.ylabel("Distance")
    plt.show()

# Main Loop
while True:
    best_method = None
    max_groups = 0
    best_groups = None

    for method in linkage_methods:
        linkage_matrix = linkage(coordinates, method=method)

        # (optional) Print Dendrogram
        # print_dendrogram(linkage_matrix, df, method)

        # 計算每個節點rrc_sum
        n_samples = len(rrc_values) # original tsv file length
        rrc_sums = np.zeros(linkage_matrix.shape[0] + n_samples)

        # 初始化葉節點的 RRC 值
        rrc_sums[:n_samples] = rrc_values   # rrc_sums[:n_samples] refers to the first n_samples elements of the rrc_sums array.

        # 計算內部節點的 RRC 總和
        for i, (left, right, _, _) in enumerate(linkage_matrix):
            left = int(left)
            right = int(right)
            rrc_sums[n_samples + i] = rrc_sums[left] + rrc_sums[right]

        # Initialize nodes for all leaf nodes
        nodes = {i: TreeNode(node_id=i, rrc_sum=rrc_sums[i], lon=coordinates[i, 0], lat=coordinates[i, 1]) for i in range(n_samples)}

        # Create internal nodes using the linkage matrix
        for i, (left, right, dist, _) in enumerate(linkage_matrix):
            left = int(left)
            right = int(right)
            # Create a new internal node
            node_id = n_samples + i  # Internal node ID
            new_node = TreeNode(
                node_id=node_id,
                rrc_sum=rrc_sums[node_id],  # RRC sum for the new node
                distance=dist,             # Distance between the two clusters
                children=[nodes[left], nodes[right]]  # Add children nodes
            )
            # Add the new node to the nodes dictionary
            nodes[node_id] = new_node

        root = nodes[len(nodes) - 1]
        groups = group_tree(root, thresh_initial)

        group_rrc_sums = [sum(leaf.rrc_sum for leaf in group) for group in groups]
        num_groups_above_thresh = sum(1 for rrc_sum in group_rrc_sums if rrc_sum > thresh_group)

        if num_groups_above_thresh > max_groups:
            max_groups = num_groups_above_thresh
            best_method = method
            best_groups = groups

    if max_groups == 0:
        break

    # (optional) plot groups in the map
    plot_groups_with_highlight(best_groups, thresh_group)

    print(f"Best Method: {best_method}, Groups Found: {max_groups}")
    filtered_groups, filtered_leaves = filter_and_store_groups(best_groups, thresh_group)
    all_filtered_groups.extend(filtered_groups)

    iteration_data, group_id = assign_group_ids_and_save(filtered_groups, group_id)
    output_data = pd.concat([output_data, iteration_data], ignore_index=True)

    coordinates = np.array([[leaf.lon, leaf.lat] for leaf in filtered_leaves])
    rrc_values = np.array([leaf.rrc_sum for leaf in filtered_leaves])

    if len(coordinates) == 0:
        break

# Print RRC sum of each group
print("\nFinal Group RRC Sums:")
for i, group in enumerate(all_filtered_groups, start=1):
    group_rrc_sum = sum(leaf.rrc_sum for leaf in group)
    print(f"Group {i}: RRC Sum = {group_rrc_sum:,}")

# Save Final Output
output_data.to_csv(output_path, sep="\t", index=False)
print(f"Output saved to {output_path}")
