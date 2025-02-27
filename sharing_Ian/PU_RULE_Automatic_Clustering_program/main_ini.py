#%%
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.spatial.distance import cdist
import matplotlib.pyplot as plt
import seaborn as sns

#%%
input = "/home/covmo/test_ian/pu_rule_r/input_stc.tsv"
output_path = "/home/covmo/test_ian/pu_rule_r/output_groups.tsv"
df = pd.read_csv(input, sep="\t")
rrc_values = df['RRC_CNT'].values
coordinates = df[['LONGITUDE', 'LATITUDE']].values

all_filtered_groups = []
group_id = 1
output_data = pd.DataFrame()

# linkage_method = 'complete'   #分到第 3 次穩定無法分出rrc_sum > 450_000_000
# linkage_method = 'average'  #分到第 3 次穩定無法分出rrc_sum > 450_000_000
linkage_method = 'ward'   #分到第 3 次穩定無法分出rrc_sum > 450_000_000
# linkage_method = 'single'   #分到第 4 次穩定無法分出rrc_sum > 450_000_000

#%% functions
# Function to plot the groups on a map
def plot_groups_on_map(groups):
    plt.figure(figsize=(50, 30))
    colors = sns.color_palette("tab10", len(groups))  # Assign unique colors for groups

    for i, group in enumerate(groups):
        lons = [leaf.lon for leaf in group]
        lats = [leaf.lat for leaf in group]
        plt.scatter(lons, lats, label=f"Group {i + 1}", color=colors[i], s=6)

    plt.title("Leaf Node Groups on Map")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend(title="Groups")
    plt.grid(True)
    plt.show()

# Define a tree node structure
class TreeNode:
    def __init__(self, node_id, rrc_sum=0, distance=None, lon=None, lat=None, children=None):
        self.node_id = node_id         # Unique ID for the node
        self.rrc_sum = rrc_sum         # RRC sum for the node
        self.distance = distance       # Distance (for non-leaf nodes only)
        self.lon = lon                 # Longitude (for leaf nodes only)
        self.lat = lat                 # Latitude (for leaf nodes only)
        self.children = children or [] # Children nodes (only for non-leaf nodes)

# Function to collect leaf nodes under a node
def collect_leaf_nodes(node):
    if node.lon is not None and node.lat is not None:  # Leaf node
        return [node]
    else:  # Internal node
        leaves = []
        for child in node.children:
            leaves.extend(collect_leaf_nodes(child))
        return leaves

# Function to perform grouping based on the rrc_sum threshold
def group_tree(node, threshold):
    groups = []

    def traverse(node):
        # If the node's RRC sum is below the threshold, treat all its leaves as a single group
        if node.rrc_sum < threshold:
            groups.append(collect_leaf_nodes(node))
            return  # Stop further traversal
        # Otherwise, traverse its children
        if node.children:
            for child in node.children:
                traverse(child)

    traverse(node)
    return groups

# Function to plot groups on a map with highlighting
def plot_groups_with_highlight(groups, threshold):
    plt.figure(figsize=(50, 30))

    # Create a color palette for highlighted groups
    highlight_colors = sns.color_palette("tab10", sum(
        sum(leaf.rrc_sum for leaf in group) > threshold for group in groups))
    gray_color = (0.8, 0.8, 0.8)  # Light gray for non-highlighted groups

    color_idx = 0  # Index for highlight colors

    for i, group in enumerate(groups):
        group_rrc_sum = sum(leaf.rrc_sum for leaf in group)
        lons = [leaf.lon for leaf in group]
        lats = [leaf.lat for leaf in group]

        if group_rrc_sum > threshold:
            color = highlight_colors[color_idx]  # Assign a unique color
            color_idx += 1
            label = f"Group {i + 1}: RRC Sum = {group_rrc_sum:,}"
        else:
            color = gray_color  # Assign light gray for non-highlighted groups
            label = None  # Do not show label for non-highlighted groups

        plt.scatter(lons, lats, label=label, color=color, s=6)

    plt.title(f"Leaf Node Groups with Highlighted RRC Sum > {threshold:,}")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.legend(title="Highlighted Groups")
    plt.grid(True)
    plt.show()
# 篩選掉 RRC Sum 超過閾值的 Groups
def filter_groups(groups, threshold):
    filtered_leaves = []
    for group in groups:
        group_rrc_sum = sum(leaf.rrc_sum for leaf in group)
        if group_rrc_sum <= threshold:  # 只保留未超過閾值的群組
            filtered_leaves.extend(group)
    return filtered_leaves


# Filter and store groups exceeding the threshold
def filter_and_store_groups(groups, threshold):
    filtered_groups = []
    remaining_leaves = []

    for group in groups:
        group_rrc_sum = sum(leaf.rrc_sum for leaf in group)
        if group_rrc_sum > threshold:
            filtered_groups.append(group)  # Store groups exceeding the threshold
        else:
            remaining_leaves.extend(group)  # Keep groups below the threshold

    return filtered_groups, remaining_leaves

# Assign group IDs and save results to a DataFrame
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




#%% 第一次分群 - 選擇可以分出最多群的方法
# linkage_method = 'ward'             # 15
# linkage_method = 'average'          # 14
linkage_method = 'single'           # 17
# linkage_method = 'complete'         # 13
#%% 第一次分群 
linkage_matrix = linkage(coordinates, method=linkage_method)

# Dendrogram
sns.set(style="whitegrid")
plt.figure(figsize=(24, 16))
dendrogram(linkage_matrix, labels=df['ENODEB_ID'].values, leaf_rotation=90, leaf_font_size=10)
plt.title(f"Hierarchical Clustering Dendrogram_{linkage_method}")
plt.xlabel("ENODEB_ID")
plt.ylabel("Distance")
plt.show()


# 計算每個節點rrc_sum
n_samples = len(rrc_values)
rrc_sums = np.zeros(linkage_matrix.shape[0] + n_samples)

# 初始化葉節點的 RRC 值
rrc_sums[:n_samples] = rrc_values   # rrc_sums[:n_samples] refers to the first n_samples elements of the rrc_sums array.

# 計算內部節點的 RRC 總和
for i, (left, right, _, _) in enumerate(linkage_matrix):
    left = int(left)
    right = int(right)
    rrc_sums[n_samples + i] = rrc_sums[left] + rrc_sums[right]


# Initialize nodes for all leaf nodes
n_samples = len(rrc_values)
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

# The root of the tree is the last node created
root = nodes[len(nodes) - 1]

# Function to print the tree (for visualization)
# def print_tree(node, depth=0):
#     indent = "  " * depth
#     if node.lon is not None and node.lat is not None:  # Leaf node
#         print(f"{indent}Leaf Node {node.node_id}: RRC Sum={node.rrc_sum}, Lon={node.lon}, Lat={node.lat}")
#     else:  # Internal node
#         print(f"{indent}Internal Node {node.node_id}: RRC Sum={node.rrc_sum}, Distance={node.distance}")
#         for child in node.children:
#             print_tree(child, depth + 1)

# # Print the constructed tree
# print_tree(root)


# Group the tree with the threshold
threshold = 600_000_000
groups_0 = group_tree(root, threshold)

# Display the groups
# for i, group in enumerate(groups_0):
#     print(f"Group {i + 1}:")
#     for leaf in group:
#         print(f"  Leaf Node {leaf.node_id}: RRC Sum={leaf.rrc_sum}, Lon={leaf.lon}, Lat={leaf.lat}")


# Display the groups and their RRC sums
# for i, group in enumerate(groups_0):
#     group_rrc_sum = sum(leaf.rrc_sum for leaf in group)  # Calculate RRC sum for the group
#     print(f"Group {i + 1}: RRC Sum = {group_rrc_sum:,}")


# show intervals with numbers
group_rrc_sums = [sum(leaf.rrc_sum for leaf in group) for group in groups_0]
max_rrc_sum = int(max(group_rrc_sums) + 50_000_000)
bins = list(range(0, max_rrc_sum, 50_000_000)) 
bin_counts = pd.cut(group_rrc_sums, bins=bins, right=False).value_counts().sort_index()
print(bin_counts)


# Function to plot the groups on a map
# Call the function to plot
# plot_groups_on_map(groups_0)


# Call the function to plot
threshold = 450_000_000
plot_groups_with_highlight(groups_0, threshold)


#%%
linkage_method = 'ward'             # 4
# linkage_method = 'average'          # 3
# linkage_method = 'single'           # 3
# linkage_method = 'complete'         # 4
#%% 第二次分群 選出>450_000_000的群以後，把這些點拿掉，重新分群，做相同的動作(分群 計算每個節點的rrc_sum 找出>450_000_000的群)
# Filter and store groups exceeding the threshold
threshold = 450_000_000
filtered_groups, filtered_leaves = filter_and_store_groups(groups_0, threshold)
all_filtered_groups.extend(filtered_groups)

# Assign group IDs and save
iteration_data, group_id = assign_group_ids_and_save(filtered_groups, group_id)
output_data = pd.concat([output_data, iteration_data], ignore_index=True)

# 重建剩餘的 coordinates 和 rrc_values
remaining_coordinates = np.array([[leaf.lon, leaf.lat] for leaf in filtered_leaves])
remaining_rrc_values = np.array([leaf.rrc_sum for leaf in filtered_leaves])

# 重新進行階層式分群
new_linkage_matrix = linkage(remaining_coordinates, method=linkage_method)

# 計算新的 RRC 總和
n_samples = len(remaining_rrc_values)
new_rrc_sums = np.zeros(new_linkage_matrix.shape[0] + n_samples)
new_rrc_sums[:n_samples] = remaining_rrc_values

for i, (left, right, _, _) in enumerate(new_linkage_matrix):
    left = int(left)
    right = int(right)
    new_rrc_sums[n_samples + i] = new_rrc_sums[left] + new_rrc_sums[right]

# 重建 Tree Nodes
new_nodes = {i: TreeNode(node_id=i, rrc_sum=new_rrc_sums[i], lon=remaining_coordinates[i, 0], lat=remaining_coordinates[i, 1]) for i in range(n_samples)}

for i, (left, right, dist, _) in enumerate(new_linkage_matrix):
    left = int(left)
    right = int(right)
    node_id = n_samples + i
    new_node = TreeNode(
        node_id=node_id,
        rrc_sum=new_rrc_sums[node_id],
        distance=dist,
        children=[new_nodes[left], new_nodes[right]]
    )
    new_nodes[node_id] = new_node

# 新的樹的根節點
new_root = new_nodes[len(new_nodes) - 1]

# 再次分群
threshold = 600_000_000
groups_1 = group_tree(new_root, threshold)

# 顯示新的分群結果
# for i, group in enumerate(groups_1):
#     group_rrc_sum = sum(leaf.rrc_sum for leaf in group)
#     print(f"New Group {i + 1}: RRC Sum = {group_rrc_sum:,}")
#     for leaf in group:
#         print(f"  Leaf Node {leaf.node_id}: RRC Sum={leaf.rrc_sum}, Lon={leaf.lon}, Lat={leaf.lat}")

#
group_rrc_sums = [sum(leaf.rrc_sum for leaf in group) for group in groups_1]
max_rrc_sum = int(max(group_rrc_sums) + 50_000_000)
bins = list(range(0, max_rrc_sum, 50_000_000)) 
bin_counts = pd.cut(group_rrc_sums, bins=bins, right=False).value_counts().sort_index()
print(bin_counts)

#
threshold = 450_000_000
plot_groups_with_highlight(groups_1, threshold)

#%% 第三次分群
# linkage_method = 'ward'             # 1
# linkage_method = 'average'          # 0
linkage_method = 'single'           # 3
# linkage_method = 'complete'         # 2
#%% 第三次分群
# Filter and store groups exceeding the threshold
threshold = 450_000_000
filtered_groups, filtered_leaves = filter_and_store_groups(groups_1, threshold)
all_filtered_groups.extend(filtered_groups)
# Assign group IDs and save
iteration_data, group_id = assign_group_ids_and_save(filtered_groups, group_id)
output_data = pd.concat([output_data, iteration_data], ignore_index=True)

# 重建剩餘的 coordinates 和 rrc_values
remaining_coordinates = np.array([[leaf.lon, leaf.lat] for leaf in filtered_leaves])
remaining_rrc_values = np.array([leaf.rrc_sum for leaf in filtered_leaves])

# 重新進行階層式分群
new_linkage_matrix = linkage(remaining_coordinates, method=linkage_method)

# 計算新的 RRC 總和
n_samples = len(remaining_rrc_values)
new_rrc_sums = np.zeros(new_linkage_matrix.shape[0] + n_samples)
new_rrc_sums[:n_samples] = remaining_rrc_values

for i, (left, right, _, _) in enumerate(new_linkage_matrix):
    left = int(left)
    right = int(right)
    new_rrc_sums[n_samples + i] = new_rrc_sums[left] + new_rrc_sums[right]

# 重建 Tree Nodes
new_nodes = {i: TreeNode(node_id=i, rrc_sum=new_rrc_sums[i], lon=remaining_coordinates[i, 0], lat=remaining_coordinates[i, 1]) for i in range(n_samples)}

for i, (left, right, dist, _) in enumerate(new_linkage_matrix):
    left = int(left)
    right = int(right)
    node_id = n_samples + i
    new_node = TreeNode(
        node_id=node_id,
        rrc_sum=new_rrc_sums[node_id],
        distance=dist,
        children=[new_nodes[left], new_nodes[right]]
    )
    new_nodes[node_id] = new_node

# 新的樹的根節點
new_root = new_nodes[len(new_nodes) - 1]

# 再次分群
threshold = 600_000_000
groups_2 = group_tree(new_root, threshold)

# # 顯示新的分群結果
# for i, group in enumerate(groups_2):
#     group_rrc_sum = sum(leaf.rrc_sum for leaf in group)
#     print(f"New Group {i + 1}: RRC Sum = {group_rrc_sum:,}")
#     for leaf in group:
#         print(f"  Leaf Node {leaf.node_id}: RRC Sum={leaf.rrc_sum}, Lon={leaf.lon}, Lat={leaf.lat}")

#
group_rrc_sums = [sum(leaf.rrc_sum for leaf in group) for group in groups_2]
max_rrc_sum = int(max(group_rrc_sums) + 50_000_000)
bins = list(range(0, max_rrc_sum, 50_000_000)) 
bin_counts = pd.cut(group_rrc_sums, bins=bins, right=False).value_counts().sort_index()
print(bin_counts)

#
threshold = 450_000_000
plot_groups_with_highlight(groups_2, threshold)


# Function to plot the groups on a map
# plot_groups_on_map(groups_2)


#%% 第四次分群
# linkage_method = 'ward'             # 1
# linkage_method = 'average'          # 1
# linkage_method = 'single'           # 2
linkage_method = 'complete'         # 3
#%% 第四次分群
# Filter and store groups exceeding the threshold
threshold = 450_000_000
filtered_groups, filtered_leaves = filter_and_store_groups(groups_2, threshold)
all_filtered_groups.extend(filtered_groups)
# Assign group IDs and save
iteration_data, group_id = assign_group_ids_and_save(filtered_groups, group_id)
output_data = pd.concat([output_data, iteration_data], ignore_index=True)

# 重建剩餘的 coordinates 和 rrc_values
remaining_coordinates = np.array([[leaf.lon, leaf.lat] for leaf in filtered_leaves])
remaining_rrc_values = np.array([leaf.rrc_sum for leaf in filtered_leaves])

# 重新進行階層式分群
new_linkage_matrix = linkage(remaining_coordinates, method=linkage_method)

# 計算新的 RRC 總和
n_samples = len(remaining_rrc_values)
new_rrc_sums = np.zeros(new_linkage_matrix.shape[0] + n_samples)
new_rrc_sums[:n_samples] = remaining_rrc_values

for i, (left, right, _, _) in enumerate(new_linkage_matrix):
    left = int(left)
    right = int(right)
    new_rrc_sums[n_samples + i] = new_rrc_sums[left] + new_rrc_sums[right]

# 重建 Tree Nodes
new_nodes = {i: TreeNode(node_id=i, rrc_sum=new_rrc_sums[i], lon=remaining_coordinates[i, 0], lat=remaining_coordinates[i, 1]) for i in range(n_samples)}

for i, (left, right, dist, _) in enumerate(new_linkage_matrix):
    left = int(left)
    right = int(right)
    node_id = n_samples + i
    new_node = TreeNode(
        node_id=node_id,
        rrc_sum=new_rrc_sums[node_id],
        distance=dist,
        children=[new_nodes[left], new_nodes[right]]
    )
    new_nodes[node_id] = new_node

# 新的樹的根節點
new_root = new_nodes[len(new_nodes) - 1]

# 再次分群
threshold = 600_000_000
groups_3 = group_tree(new_root, threshold)

# # 顯示新的分群結果
# for i, group in enumerate(groups_2):
#     group_rrc_sum = sum(leaf.rrc_sum for leaf in group)
#     print(f"New Group {i + 1}: RRC Sum = {group_rrc_sum:,}")
#     for leaf in group:
#         print(f"  Leaf Node {leaf.node_id}: RRC Sum={leaf.rrc_sum}, Lon={leaf.lon}, Lat={leaf.lat}")

#
group_rrc_sums = [sum(leaf.rrc_sum for leaf in group) for group in groups_3]
max_rrc_sum = int(max(group_rrc_sums) + 50_000_000)
bins = list(range(0, max_rrc_sum, 50_000_000)) 
bin_counts = pd.cut(group_rrc_sums, bins=bins, right=False).value_counts().sort_index()
print(bin_counts)

#
threshold = 450_000_000
plot_groups_with_highlight(groups_3, threshold)


# Function to plot the groups on a map
# plot_groups_on_map(groups_2)


#%% 第 5 次分群
linkage_method = 'ward'             # 1
# linkage_method = 'average'          # 1
# linkage_method = 'single'           # 0
# linkage_method = 'complete'         # 1
#%% 第 5 次分群
# Filter and store groups exceeding the threshold
threshold = 450_000_000
filtered_groups, filtered_leaves = filter_and_store_groups(groups_3, threshold)
all_filtered_groups.extend(filtered_groups)
# Assign group IDs and save
iteration_data, group_id = assign_group_ids_and_save(filtered_groups, group_id)
output_data = pd.concat([output_data, iteration_data], ignore_index=True)

# 重建剩餘的 coordinates 和 rrc_values
remaining_coordinates = np.array([[leaf.lon, leaf.lat] for leaf in filtered_leaves])
remaining_rrc_values = np.array([leaf.rrc_sum for leaf in filtered_leaves])

# 重新進行階層式分群
new_linkage_matrix = linkage(remaining_coordinates, method=linkage_method)

# 計算新的 RRC 總和
n_samples = len(remaining_rrc_values)
new_rrc_sums = np.zeros(new_linkage_matrix.shape[0] + n_samples)
new_rrc_sums[:n_samples] = remaining_rrc_values

for i, (left, right, _, _) in enumerate(new_linkage_matrix):
    left = int(left)
    right = int(right)
    new_rrc_sums[n_samples + i] = new_rrc_sums[left] + new_rrc_sums[right]

# 重建 Tree Nodes
new_nodes = {i: TreeNode(node_id=i, rrc_sum=new_rrc_sums[i], lon=remaining_coordinates[i, 0], lat=remaining_coordinates[i, 1]) for i in range(n_samples)}

for i, (left, right, dist, _) in enumerate(new_linkage_matrix):
    left = int(left)
    right = int(right)
    node_id = n_samples + i
    new_node = TreeNode(
        node_id=node_id,
        rrc_sum=new_rrc_sums[node_id],
        distance=dist,
        children=[new_nodes[left], new_nodes[right]]
    )
    new_nodes[node_id] = new_node

# 新的樹的根節點
new_root = new_nodes[len(new_nodes) - 1]

# 再次分群
threshold = 600_000_000
groups_4 = group_tree(new_root, threshold)

# # 顯示新的分群結果
# for i, group in enumerate(groups_2):
#     group_rrc_sum = sum(leaf.rrc_sum for leaf in group)
#     print(f"New Group {i + 1}: RRC Sum = {group_rrc_sum:,}")
#     for leaf in group:
#         print(f"  Leaf Node {leaf.node_id}: RRC Sum={leaf.rrc_sum}, Lon={leaf.lon}, Lat={leaf.lat}")

#
group_rrc_sums = [sum(leaf.rrc_sum for leaf in group) for group in groups_4]
max_rrc_sum = int(max(group_rrc_sums) + 50_000_000)
bins = list(range(0, max_rrc_sum, 50_000_000)) 
bin_counts = pd.cut(group_rrc_sums, bins=bins, right=False).value_counts().sort_index()
print(bin_counts)

#
threshold = 450_000_000
plot_groups_with_highlight(groups_4, threshold)


# Function to plot the groups on a map
# plot_groups_on_map(groups_2)




#%% 第 6 次分群
# linkage_method = 'ward'             # 0
linkage_method = 'average'          # 1
# linkage_method = 'single'           # 0
# linkage_method = 'complete'         # 0
#%% 第 6 次分群
# Filter and store groups exceeding the threshold
threshold = 450_000_000
filtered_groups, filtered_leaves = filter_and_store_groups(groups_4, threshold)
all_filtered_groups.extend(filtered_groups)
# Assign group IDs and save
iteration_data, group_id = assign_group_ids_and_save(filtered_groups, group_id)
output_data = pd.concat([output_data, iteration_data], ignore_index=True)

# 重建剩餘的 coordinates 和 rrc_values
remaining_coordinates = np.array([[leaf.lon, leaf.lat] for leaf in filtered_leaves])
remaining_rrc_values = np.array([leaf.rrc_sum for leaf in filtered_leaves])

# 重新進行階層式分群
new_linkage_matrix = linkage(remaining_coordinates, method=linkage_method)

# 計算新的 RRC 總和
n_samples = len(remaining_rrc_values)
new_rrc_sums = np.zeros(new_linkage_matrix.shape[0] + n_samples)
new_rrc_sums[:n_samples] = remaining_rrc_values

for i, (left, right, _, _) in enumerate(new_linkage_matrix):
    left = int(left)
    right = int(right)
    new_rrc_sums[n_samples + i] = new_rrc_sums[left] + new_rrc_sums[right]

# 重建 Tree Nodes
new_nodes = {i: TreeNode(node_id=i, rrc_sum=new_rrc_sums[i], lon=remaining_coordinates[i, 0], lat=remaining_coordinates[i, 1]) for i in range(n_samples)}

for i, (left, right, dist, _) in enumerate(new_linkage_matrix):
    left = int(left)
    right = int(right)
    node_id = n_samples + i
    new_node = TreeNode(
        node_id=node_id,
        rrc_sum=new_rrc_sums[node_id],
        distance=dist,
        children=[new_nodes[left], new_nodes[right]]
    )
    new_nodes[node_id] = new_node

# 新的樹的根節點
new_root = new_nodes[len(new_nodes) - 1]

# 再次分群
threshold = 600_000_000
groups_5 = group_tree(new_root, threshold)

#
group_rrc_sums = [sum(leaf.rrc_sum for leaf in group) for group in groups_5]
max_rrc_sum = int(max(group_rrc_sums) + 50_000_000)
bins = list(range(0, max_rrc_sum, 50_000_000)) 
bin_counts = pd.cut(group_rrc_sums, bins=bins, right=False).value_counts().sort_index()
print(bin_counts)

#
threshold = 450_000_000
plot_groups_with_highlight(groups_5, threshold)




#%% 第 7 次分群 - all 0 for threshold = 600_000_000
# linkage_method = 'ward'             # 0
# linkage_method = 'average'          # 0
# linkage_method = 'single'           # 0
# linkage_method = 'complete'         # 0
#%% 第 7 次分群 -  threshold = 650_000_000
# linkage_method = 'ward'             # 1
# linkage_method = 'average'          # 1
# linkage_method = 'single'           # 1
linkage_method = 'complete'         # 1
#%% 第 7 次分群
# Filter and store groups exceeding the threshold
threshold = 450_000_000
filtered_groups, filtered_leaves = filter_and_store_groups(groups_5, threshold)
all_filtered_groups.extend(filtered_groups)
# Assign group IDs and save
iteration_data, group_id = assign_group_ids_and_save(filtered_groups, group_id)
output_data = pd.concat([output_data, iteration_data], ignore_index=True)

# 重建剩餘的 coordinates 和 rrc_values
remaining_coordinates = np.array([[leaf.lon, leaf.lat] for leaf in filtered_leaves])
remaining_rrc_values = np.array([leaf.rrc_sum for leaf in filtered_leaves])

# 重新進行階層式分群
new_linkage_matrix = linkage(remaining_coordinates, method=linkage_method)

# 計算新的 RRC 總和
n_samples = len(remaining_rrc_values)
new_rrc_sums = np.zeros(new_linkage_matrix.shape[0] + n_samples)
new_rrc_sums[:n_samples] = remaining_rrc_values

for i, (left, right, _, _) in enumerate(new_linkage_matrix):
    left = int(left)
    right = int(right)
    new_rrc_sums[n_samples + i] = new_rrc_sums[left] + new_rrc_sums[right]

# 重建 Tree Nodes
new_nodes = {i: TreeNode(node_id=i, rrc_sum=new_rrc_sums[i], lon=remaining_coordinates[i, 0], lat=remaining_coordinates[i, 1]) for i in range(n_samples)}

for i, (left, right, dist, _) in enumerate(new_linkage_matrix):
    left = int(left)
    right = int(right)
    node_id = n_samples + i
    new_node = TreeNode(
        node_id=node_id,
        rrc_sum=new_rrc_sums[node_id],
        distance=dist,
        children=[new_nodes[left], new_nodes[right]]
    )
    new_nodes[node_id] = new_node

# 新的樹的根節點
new_root = new_nodes[len(new_nodes) - 1]

# 再次分群
threshold = 650_000_000
groups_6 = group_tree(new_root, threshold)

#
group_rrc_sums = [sum(leaf.rrc_sum for leaf in group) for group in groups_6]
max_rrc_sum = int(max(group_rrc_sums) + 50_000_000)
bins = list(range(0, max_rrc_sum, 50_000_000)) 
bin_counts = pd.cut(group_rrc_sums, bins=bins, right=False).value_counts().sort_index()
print(bin_counts)

#
threshold = 450_000_000
plot_groups_with_highlight(groups_6, threshold)




#%% 把第七次分ok結果存到output
# Filter and store groups exceeding the threshold
threshold = 450_000_000
filtered_groups, filtered_leaves = filter_and_store_groups(groups_6, threshold)
all_filtered_groups.extend(filtered_groups)
# Assign group IDs and save
iteration_data, group_id = assign_group_ids_and_save(filtered_groups, group_id)
output_data = pd.concat([output_data, iteration_data], ignore_index=True)

#%%
# Function to plot the groups on a map
plot_groups_on_map(groups_6)

#%%
output_data.to_csv(output_path, sep="\t", index=False)
print(f"Output saved to {output_path}")

#%%

























#%% 印出節點rrc_sum (無法正確印出圖上的位置)
# 設定閾值
threshold = 450_000_000

# 計算每個節點的 RRC 總和
n_samples = len(rrc_values)
rrc_sums = np.zeros(linkage_matrix.shape[0] + n_samples)

# 初始化葉節點的 RRC 值
rrc_sums[:n_samples] = rrc_values   # rrc_sums[:n_samples] refers to the first n_samples elements of the rrc_sums array.

# 計算內部節點的 RRC 總和
for i, (left, right, _, _) in enumerate(linkage_matrix):
    left = int(left)
    right = int(right)
    rrc_sums[n_samples + i] = rrc_sums[left] + rrc_sums[right]

# 找到超過閾值的節點
top_indices = np.where(rrc_sums > threshold)[0]

def plot_dendrogram_with_rrc_corrected(linkage_matrix, rrc_sums, top_indices, threshold, n_samples):
    dendro = dendrogram(
        linkage_matrix,
        leaf_rotation=90,
        leaf_font_size=10,
        above_threshold_color="grey",
        no_labels=True  # 不顯示預設標籤
    )

    # 獲取樹狀圖資訊
    icoord = np.array(dendro['icoord'])
    dcoord = np.array(dendro['dcoord'])
    ivl = list(map(int, dendro['ivl']))  # 標籤順序對應的節點索引

    # 獲取每個節點的x座標和y座標
    coord_map = {}
    for i, d in enumerate(dcoord):
        x = np.mean(icoord[i])
        y = max_rrc_sum(d)
        coord_map[n_samples + i] = (x, y)  # 保存內部節點的座標

    # 標註 RRC 值
    for node_id in top_indices:
        if node_id < n_samples:
            # 葉節點不需要標註
            continue
        else:  # 內部節點
            x, y = coord_map[node_id]  # 獲取對應節點的x, y座標
            plt.text(
                x, y + 5, f"{rrc_sums[node_id]:,.0f}",  # 向上偏移一點
                color="red", fontsize=8, ha='center', va='bottom'
            )

    # 添加標題和閾值線
    plt.title(f"Hierarchical Clustering Dendrogram ({linkage_method})")
    plt.xlabel("Node Index")
    plt.ylabel("Distance")
    plt.axhline(y=threshold, color='blue', linestyle='--', label=f"Threshold: {threshold}")
    plt.legend()
    plt.show()

# 繪製修正後的樹狀圖
plt.figure(figsize=(24, 16))
plot_dendrogram_with_rrc_corrected(linkage_matrix, rrc_sums, top_indices, threshold, n_samples)






















#%% 切割树状图 default #########################################################################################
num_of_group = 10
# 使用 fcluster 方法进行切割
cluster_labels = fcluster(linkage_matrix, num_of_group, criterion='maxclust')

# 将分群结果添加到原始数据中
df['Cluster'] = cluster_labels

plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='LONGITUDE', y='LATITUDE', hue='Cluster', palette='tab10', s=100)
plt.title("Hierarchical Clustering: 2 Clusters")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(title="Cluster")
plt.show()










#%% Step 2: Custom DFS clustering with dynamic RRC threshold
def dfs_grouping_with_dynamic_threshold(
    node, linkage_matrix, rrc_values, coordinates, 
    min_threshold, max_threshold, visited, cluster_labels, 
    current_cluster, current_sum, cluster_points
):
    """
    Perform DFS to assign clusters based on dynamic RRC thresholds.

    Args:
        node: Current node index in the linkage matrix.
        linkage_matrix: Linkage matrix from hierarchical clustering.
        rrc_values: Array of RRC values for leaf nodes.
        coordinates: Array of coordinates for leaf nodes.
        min_threshold: Minimum RRC threshold to consider cluster completion.
        max_threshold: Maximum RRC threshold to enforce cluster completion.
        visited: Set of visited nodes.
        cluster_labels: Array to store cluster labels for each leaf.
        current_cluster: Current cluster ID.
        current_sum: Current sum of RRC values in the cluster.
        cluster_points: List of points in the current cluster (for proximity checks).

    Returns:
        Updated cluster_labels, current_cluster, current_sum, cluster_points.
    """
    n_samples = len(rrc_values)

    if node < n_samples:  # Leaf node
        if node not in visited:
            if current_sum + rrc_values[node] > max_threshold or (
                current_sum >= min_threshold and current_sum + rrc_values[node] > min_threshold
            ):
                # Complete current cluster and start a new one
                current_cluster += 1
                current_sum = 0
                cluster_points = []

            cluster_labels[node] = current_cluster
            current_sum += rrc_values[node]
            visited.add(node)
            cluster_points.append(coordinates[node])
        return cluster_labels, current_cluster, current_sum, cluster_points

    left, right = int(linkage_matrix[node - n_samples, 0]), int(linkage_matrix[node - n_samples, 1])

    def compute_average_coords(index):
        if index < n_samples:  # Leaf node
            return coordinates[index]
        else:  # Internal node
            child_indices = linkage_matrix[index - n_samples, :2].astype(int)
            child_coords = [compute_average_coords(child) for child in child_indices]
            return np.mean(child_coords, axis=0)

    left_coord = compute_average_coords(left)
    right_coord = compute_average_coords(right)

    if cluster_points:
        cluster_center = np.mean(cluster_points, axis=0)
        left_distance = np.linalg.norm(cluster_center - left_coord)
        right_distance = np.linalg.norm(cluster_center - right_coord)
    else:
        left_distance = right_distance = 0

    if left_distance <= right_distance:
        cluster_labels, current_cluster, current_sum, cluster_points = dfs_grouping_with_dynamic_threshold(
            left, linkage_matrix, rrc_values, coordinates, 
            min_threshold, max_threshold, visited, cluster_labels, 
            current_cluster, current_sum, cluster_points
        )
        cluster_labels, current_cluster, current_sum, cluster_points = dfs_grouping_with_dynamic_threshold(
            right, linkage_matrix, rrc_values, coordinates, 
            min_threshold, max_threshold, visited, cluster_labels, 
            current_cluster, current_sum, cluster_points
        )
    else:
        cluster_labels, current_cluster, current_sum, cluster_points = dfs_grouping_with_dynamic_threshold(
            right, linkage_matrix, rrc_values, coordinates, 
            min_threshold, max_threshold, visited, cluster_labels, 
            current_cluster, current_sum, cluster_points
        )
        cluster_labels, current_cluster, current_sum, cluster_points = dfs_grouping_with_dynamic_threshold(
            left, linkage_matrix, rrc_values, coordinates, 
            min_threshold, max_threshold, visited, cluster_labels, 
            current_cluster, current_sum, cluster_points
        )

    return cluster_labels, current_cluster, current_sum, cluster_points

# Initialize variables
min_threshold = 300_000_000
max_threshold = 600_000_000
n_samples = len(rrc_values)
visited = set()
cluster_labels = np.zeros(n_samples, dtype=int)
cluster_points = []

# Perform DFS
cluster_labels, _, _, _ = dfs_grouping_with_dynamic_threshold(
    len(linkage_matrix) + n_samples - 1, linkage_matrix, rrc_values, coordinates, 
    min_threshold, max_threshold, visited, cluster_labels, 
    current_cluster=1, current_sum=0, cluster_points=[]
)

# Add cluster labels to DataFrame
df['Cluster'] = cluster_labels

# Step 3: Visualize results
plt.figure(figsize=(50, 30))
sns.scatterplot(data=df, x='LONGITUDE', y='LATITUDE', hue='Cluster', palette='tab10', s=8)
plt.title(f"Hierarchical Clustering with RRC Threshold = [{min_threshold}, {max_threshold}], Method = {linkage_method}")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(title="Cluster")
plt.show()
















#%% 計算每個節點的總和
def calculate_rrc_totals(linkage_matrix, rrc_values):
    """
    计算层次聚类中每个节点的 RRC 总和
    """
    n_samples = len(rrc_values)
    rrc_totals = {i: rrc_values[i] for i in range(n_samples)}  # 初始 RRC 值为叶节点值

    # 遍历非叶节点
    for i, (left, right, _, _) in enumerate(linkage_matrix, start=n_samples):
        rrc_totals[i] = rrc_totals[int(left)] + rrc_totals[int(right)]
    return rrc_totals

rrc_totals = calculate_rrc_totals(linkage_matrix, rrc_values)












#%% 分群优化切割
def split_clusters(linkage_matrix, rrc_totals, target_k):
    """
    使用递归切分树状图，将数据分为 target_k 个分组，尽量满足地理和 RRC 平衡性。
    """
    n_samples = len(rrc_totals) // 2 + 1  # 原始叶节点数量

    # 初始分配
    cluster_assignments = {i: i for i in range(n_samples)}

    def recursive_split(node_id, current_clusters):
        """
        递归分割树状图
        """
        nonlocal cluster_assignments

        # 如果已经达到目标分组数，则停止
        if len(current_clusters) >= target_k:
            return

        # 获取当前节点的左、右子节点
        left, right, _, _ = linkage_matrix[node_id - n_samples]

        # 将当前节点分为两个子节点
        current_clusters.remove(node_id)
        current_clusters.add(int(left))
        current_clusters.add(int(right))

        # 更新 cluster_assignments
        for cluster in [int(left), int(right)]:
            cluster_assignments[cluster] = cluster

        # 递归处理子节点
        recursive_split(int(left), current_clusters)
        recursive_split(int(right), current_clusters)

    # 初始递归从根节点开始
    root_node = len(linkage_matrix) + n_samples - 1
    current_clusters = {root_node}
    recursive_split(root_node, current_clusters)

    return cluster_assignments

# 切割结果
target_k = 3  # 指定要分成的组数
cluster_assignments = split_clusters(linkage_matrix, rrc_totals, target_k)

# 统计每组的 RRC 总和和分布
grouped_rrc = {}
for idx, cluster in cluster_assignments.items():
    if cluster not in grouped_rrc:
        grouped_rrc[cluster] = 0
    grouped_rrc[cluster] += rrc_values[idx]

# 输出结果
for cluster_id, total_rrc in grouped_rrc.items():
    print(f"Cluster {cluster_id}: RRC Total = {total_rrc}")

# 可视化分组
plt.figure(figsize=(12, 8))
dendrogram(linkage_matrix, labels=df['ENODEB_ID'].values, leaf_rotation=90, leaf_font_size=10, 
           color_threshold=linkage_matrix[-target_k, 2])  # 设置颜色阈值以显示分组
plt.title(f"Hierarchical Clustering with {target_k} Groups")
plt.xlabel("ENODEB_ID")
plt.ylabel("Distance")
plt.show()
















#%% Step 2: Custom grouping using DFS with nearest neighbor logic
rrc_threshold = 8_000_000_000  # RRC value threshold for grouping

def dfs_grouping_with_proximity(node, linkage_matrix, rrc_values, coordinates, threshold, visited, cluster_labels, current_cluster, current_sum, cluster_points):
    """
    Perform DFS to assign clusters based on RRC threshold, prioritizing proximity.

    Args:
        node: Current node index in the linkage matrix.
        linkage_matrix: Linkage matrix from hierarchical clustering.
        rrc_values: Array of RRC values for leaf nodes.
        coordinates: Array of coordinates for leaf nodes.
        threshold: Threshold for RRC value sum to form a group.
        visited: Set of visited nodes.
        cluster_labels: Array to store cluster labels for each leaf.
        current_cluster: Current cluster ID.
        current_sum: Current sum of RRC values in the cluster.
        cluster_points: List of points in the current cluster (for proximity checks).

    Returns:
        Updated cluster_labels, current_cluster, current_sum, cluster_points.
    """
    n_samples = len(rrc_values)

    if node < n_samples:  # Leaf node
        if node not in visited:
            if current_sum + rrc_values[node] > threshold:
                current_cluster += 1
                current_sum = 0
                cluster_points = []
            cluster_labels[node] = current_cluster
            current_sum += rrc_values[node]
            visited.add(node)
            cluster_points.append(coordinates[node])
        return cluster_labels, current_cluster, current_sum, cluster_points

    left, right = int(linkage_matrix[node - n_samples, 0]), int(linkage_matrix[node - n_samples, 1])

    # Get coordinates for left and right children
    def compute_average_coords(index):
        if index < n_samples:  # Leaf node
            return coordinates[index]
        else:  # Internal node
            child_indices = linkage_matrix[index - n_samples, :2].astype(int)
            child_coords = [
                compute_average_coords(child) for child in child_indices
            ]
            return np.mean(child_coords, axis=0)

    left_coord = compute_average_coords(left)
    right_coord = compute_average_coords(right)

    # Find the closest child to the current cluster
    if cluster_points:
        cluster_center = np.mean(cluster_points, axis=0)
        left_distance = np.linalg.norm(cluster_center - left_coord)
        right_distance = np.linalg.norm(cluster_center - right_coord)
    else:
        left_distance = right_distance = 0  # If no points, prioritize any child

    # Traverse the closer child first
    if left_distance <= right_distance:
        cluster_labels, current_cluster, current_sum, cluster_points = dfs_grouping_with_proximity(
            left, linkage_matrix, rrc_values, coordinates, threshold, visited, cluster_labels, current_cluster, current_sum, cluster_points)
        cluster_labels, current_cluster, current_sum, cluster_points = dfs_grouping_with_proximity(
            right, linkage_matrix, rrc_values, coordinates, threshold, visited, cluster_labels, current_cluster, current_sum, cluster_points)
    else:
        cluster_labels, current_cluster, current_sum, cluster_points = dfs_grouping_with_proximity(
            right, linkage_matrix, rrc_values, coordinates, threshold, visited, cluster_labels, current_cluster, current_sum, cluster_points)
        cluster_labels, current_cluster, current_sum, cluster_points = dfs_grouping_with_proximity(
            left, linkage_matrix, rrc_values, coordinates, threshold, visited, cluster_labels, current_cluster, current_sum, cluster_points)

    return cluster_labels, current_cluster, current_sum, cluster_points

# Initialize variables for DFS
n_samples = len(rrc_values)
visited = set()
cluster_labels = np.zeros(n_samples, dtype=int)
cluster_points = []

# Perform DFS from the root of the tree
cluster_labels, _, _, _ = dfs_grouping_with_proximity(
    len(linkage_matrix) + n_samples - 1, linkage_matrix, rrc_values, coordinates, rrc_threshold, visited, cluster_labels, current_cluster=1, current_sum=0, cluster_points=[])

# Add custom cluster labels to the dataframe
df['Cluster'] = cluster_labels

# Step 3: Visualize custom clusters
plt.figure(figsize=(30, 18))
sns.scatterplot(data=df, x='LONGITUDE', y='LATITUDE', hue='Cluster', palette='tab10', s=20)
plt.title(f"Custom Hierarchical Clustering by RRC Threshold = {rrc_threshold}(Proximity)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(title="Cluster")
plt.show()

















#%% Step 2: Custom grouping using DFS
# rrc_threshold = 10_000_000_000  # RRC value threshold for grouping

def dfs_grouping(node, linkage_matrix, rrc_values, threshold, visited, cluster_labels, current_cluster, current_sum):
    """
    Perform DFS to assign clusters based on RRC threshold.

    Args:
        node: Current node index in the linkage matrix.
        linkage_matrix: Linkage matrix from hierarchical clustering.
        rrc_values: Array of RRC values for leaf nodes.
        threshold: Threshold for RRC value sum to form a group.
        visited: Set of visited nodes.
        cluster_labels: Array to store cluster labels for each leaf.
        current_cluster: Current cluster ID.
        current_sum: Current sum of RRC values in the cluster.

    Returns:
        Updated cluster_labels, current_cluster, current_sum.
    """
    n_samples = len(rrc_values)

    if node < n_samples:  # Leaf node
        if node not in visited:
            if current_sum + rrc_values[node] > threshold:
                current_cluster += 1
                current_sum = 0
            cluster_labels[node] = current_cluster
            current_sum += rrc_values[node]
            visited.add(node)
        return cluster_labels, current_cluster, current_sum

    left, right = int(linkage_matrix[node - n_samples, 0]), int(linkage_matrix[node - n_samples, 1])

    # Traverse left child
    cluster_labels, current_cluster, current_sum = dfs_grouping(left, linkage_matrix, rrc_values, threshold, visited, cluster_labels, current_cluster, current_sum)

    # Traverse right child
    cluster_labels, current_cluster, current_sum = dfs_grouping(right, linkage_matrix, rrc_values, threshold, visited, cluster_labels, current_cluster, current_sum)

    return cluster_labels, current_cluster, current_sum

# Initialize variables for DFS
n_samples = len(rrc_values)
visited = set()
cluster_labels = np.zeros(n_samples, dtype=int)

# Perform DFS from the root of the tree
cluster_labels, _, _ = dfs_grouping(len(linkage_matrix) + n_samples - 1, linkage_matrix, rrc_values, rrc_threshold, visited, cluster_labels, current_cluster=1, current_sum=0)

# Add custom cluster labels to the dataframe
df['Cluster'] = cluster_labels

# Step 3: Visualize custom clusters
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='LONGITUDE', y='LATITUDE', hue='Cluster', palette='tab10', s=100)
plt.title("Custom Hierarchical Clustering by RRC Threshold (DFS)")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(title="Cluster")
plt.show()











#%% Step 2: Custom grouping based on RRC threshold
rrc_threshold = 5_000_000_000  # RRC value threshold for grouping

def custom_grouping_by_rrc(linkage_matrix, rrc_values, threshold):
    """
    Custom grouping by aggregating RRC values.
    Each group is formed by accumulating leaf nodes until the threshold is reached.

    Args:
        linkage_matrix: The linkage matrix from hierarchical clustering.
        rrc_values: Array of RRC values for leaf nodes.
        threshold: Threshold for RRC value sum to form a group.

    Returns:
        A list of cluster labels for each leaf node.
    """
    n_samples = len(rrc_values)
    rrc_totals = {i: rrc_values[i] for i in range(n_samples)}

    # Initialize cluster assignments and other variables
    cluster_labels = np.zeros(n_samples, dtype=int)
    current_cluster = 1
    current_sum = 0

    # Iterate through linkage matrix to accumulate RRC totals
    for i, (left, right, _, _) in enumerate(linkage_matrix):
        # Aggregate RRC values for the two nodes being merged
        left, right = int(left), int(right)
        rrc_totals[i + n_samples] = rrc_totals[left] + rrc_totals[right]

        # Assign clusters if leaf nodes
        if left < n_samples and cluster_labels[left] == 0:
            if current_sum + rrc_totals[left] > threshold:
                current_cluster += 1
                current_sum = 0
            cluster_labels[left] = current_cluster
            current_sum += rrc_totals[left]

        if right < n_samples and cluster_labels[right] == 0:
            if current_sum + rrc_totals[right] > threshold:
                current_cluster += 1
                current_sum = 0
            cluster_labels[right] = current_cluster
            current_sum += rrc_totals[right]

    return cluster_labels

# Compute custom clusters
custom_cluster_labels = custom_grouping_by_rrc(linkage_matrix, rrc_values, rrc_threshold)

# Add custom cluster labels to the dataframe
df['Cluster'] = custom_cluster_labels

# Step 3: Visualize custom clusters
plt.figure(figsize=(10, 6))
sns.scatterplot(data=df, x='LONGITUDE', y='LATITUDE', hue='Cluster', palette='tab10', s=100)
plt.title("Custom Hierarchical Clustering by RRC Threshold")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend(title="Cluster")
plt.show()






















