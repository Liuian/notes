#######################################################################################
### 1. calculate every building's area, and delete small buildings. ###################
### 2. calaulate intersections, and merge connected buildings. ########################
### 3. calculate small holes interval, and fill in small holes. #######################
#######################################################################################

#%%
import math
import pandas as pd
from shapely import wkt
from shapely.ops import unary_union
from shapely.geometry import Polygon, MultiPolygon
from pyproj import Geod
import geopandas as gpd
from collections import deque
from rtree import index
import time

input_file = '/home/covmo/test_ian/Africa_raw_buildings/tz.geojson'
output_file = '/home/covmo/test_ian/Africa_raw_buildings/tz_output.tsv'

geod = Geod(ellps="WGS84")  # 使用 WGS84 參數的 Geod 對象
fill_in_holes_threshold_area = 10000  # You can adjust this value

# 定義一個函數來計算多邊形的面積
def calculate_area(geom):
    return abs(geod.geometry_area_perimeter(geom)[0])

def area_interval_gcs(gdf):
    gdf = gdf.copy()
    # 計算每個 geometry 的面積，結果是平方米
    gdf['area_m2'] = gdf['geometry'].apply(calculate_area)
    # 定義區間
    bins = [0, 25, 50, 100, 150, 200, 250, float('inf')]
    labels = ['0-25 m²',  '25-50 m²', '50-100 m²', '100-150 m²', '150-200 m²', '200-250 m²', '>250 m²']
    # 將面積劃分到不同區間
    gdf['area_interval'] = pd.cut(gdf['area_m2'], bins=bins, labels=labels, include_lowest=True)
    # 統計每個區間的幾何數量
    interval_counts = gdf['area_interval'].value_counts().sort_index()
    # 計算每個區間所佔的百分比
    interval_percentage = (interval_counts / interval_counts.sum()) * 100
    # 將數量和百分比結合在一起
    result = pd.DataFrame({
        'Count': interval_counts,
        'Percentage': interval_percentage
    })
    # 顯示統計結果
    return result, gdf

#####################################################################################
### DFS & BFS #######################################################################
#####################################################################################
# 使用空間索引計算相交幾何並同時构建连接图
def calculate_intersections_and_build_graph(gdf):
    # 使用 sindex 查找相交的几何
    intersections = gdf.sindex.query(gdf.geometry, predicate='intersects')

    # 过滤掉自相交并构建连接图
    seen = set()
    connection_graph = {i: [] for i in range(len(gdf))}

    for idx1, idx2 in zip(*intersections):
        if idx1 != idx2 and (idx2, idx1) not in seen:
            connection_graph[idx1].append(idx2)
            connection_graph[idx2].append(idx1)
            seen.add((idx1, idx2))
    
    return connection_graph

#####################################################################################
### DFS #############################################################################
#####################################################################################
def dfs_iterative(start_node, connection_graph, visited, gdf_update):
    stack = [start_node]
    current_geometries = []
    
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            current_geometries.append(gdf_update.loc[node, 'geometry'])
            # Add unvisited neighbors to the stack
            for neighbor in connection_graph[node]:
                if neighbor not in visited:
                    stack.append(neighbor)
    
    return current_geometries

#####################################################################################
### BFS #############################################################################
#####################################################################################
def bfs_iterative(start_node, connection_graph, visited, gdf_update):
    queue = deque([start_node])
    current_geometries = []

    while queue:
        node = queue.popleft()
        if node not in visited:
            visited.add(node)
            current_geometries.append(gdf_update.loc[node, 'geometry'])
            # Add unvisited neighbors to the queue
            for neighbor in connection_graph[node]:
                if neighbor not in visited:
                    queue.append(neighbor)

    return current_geometries

#####################################################################################
### R-tree ##########################################################################
#####################################################################################
# 使用空間索引計算相交幾何並同時构建连接图
def build_r_tree(gdf):
    # 使用 R-tree 索引
    rtree_idx = index.Index()
    for idx, geometry in enumerate(gdf.geometry):
        rtree_idx.insert(idx, geometry.bounds)
    
    return rtree_idx

# 用 DFS 進行合併，並在搜索過程中動態使用 R-tree 索引
def dfs_rtree_iterative(start_node, rtree_idx, visited, gdf_update):
    stack = [start_node]
    current_geometries = []
    
    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            current_geometries.append(gdf_update.loc[node, 'geometry'])

            # 使用 R-tree 查找相交的幾何
            possible_matches_index = list(rtree_idx.intersection(gdf_update.loc[node, 'geometry'].bounds))
            for neighbor in possible_matches_index:
                if neighbor not in visited and gdf_update.loc[node, 'geometry'].intersects(gdf_update.loc[neighbor, 'geometry']):
                    stack.append(neighbor)
    
    return current_geometries

# 用 BFS 進行合併，並在搜索過程中動態使用 R-tree 索引
def bfs_rtree_iterative(start_node, rtree_idx, visited, gdf_update):
    queue = [start_node]
    current_geometries = []

    while queue:
        node = queue.pop(0)  # BFS使用隊列 (FIFO)
        if node not in visited:
            visited.add(node)
            current_geometries.append(gdf_update.loc[node, 'geometry'])

            # 使用 R-tree 查找相交的幾何
            possible_matches_index = list(rtree_idx.intersection(gdf_update.loc[node, 'geometry'].bounds))
            for neighbor in possible_matches_index:
                if neighbor not in visited and gdf_update.loc[node, 'geometry'].intersects(gdf_update.loc[neighbor, 'geometry']):
                # if neighbor not in visited:
                    queue.append(neighbor)

    return current_geometries

# Define a function to calculate areas of all holes in a polygon
def calculate_holes_areas(polygon):
    if polygon.interiors:
        # Get the area of each interior (hole) in the polygon
        return [calculate_area(Polygon(hole)) for hole in polygon.interiors]
    return []

# Function to classify the areas of the holes into intervals with default bins and labels
def classify_holes_by_area(gdf, bins=None, labels=None):
    if bins is None:
        # Define the intervals for hole area classification (in square meters)
        bins = [0, 10, 50, 100, 200, 500, 1000, 1500, 2000, 10000, float('inf')]
    if labels is None:
        labels = ['0-10 m²', '10-50 m²', '50-100 m²', '100-200 m²', '200-500 m²', '500-1000 m²', '1000-1500 m²', '1500-2000 m²', '2000-10000 m²', '>10000 m²']

    all_holes_areas = []
    
    # New GeoDataFrame to handle splitting MultiPolygon into Polygon
    rows = []

    for idx, geom in gdf.iterrows():
        geometry = geom['geometry']
        
        if isinstance(geometry, Polygon):
            # For Polygon, calculate holes and add to rows as is
            holes_areas = calculate_holes_areas(geometry)
            all_holes_areas.extend(holes_areas)
            rows.append(geom)  # Keep original row

        elif isinstance(geometry, MultiPolygon):
            # For MultiPolygon, split into individual polygons
            for poly in geometry.geoms:
                holes_areas = calculate_holes_areas(poly)
                all_holes_areas.extend(holes_areas)
                new_row = geom.copy()
                new_row['geometry'] = poly  # Replace MultiPolygon with individual Polygon
                rows.append(new_row)  # Add new row for each polygon
    
    # Create new GeoDataFrame with split rows
    new_gdf = gpd.GeoDataFrame(rows, columns=gdf.columns)

    # Classify holes into intervals
    interval_counts = pd.cut(all_holes_areas, bins=bins, labels=labels, include_lowest=True)
    
    # Statistics on hole areas
    interval_summary = interval_counts.value_counts().sort_index()
    
    # Calculate percentage of holes in each interval
    interval_percentage = (interval_summary / interval_summary.sum()) * 100
    
    return pd.DataFrame({
        'Count': interval_summary,
        'Percentage': interval_percentage
    }), new_gdf

# Function to fill holes that are smaller than a specified threshold
def fill_small_holes(gdf, threshold):
    def remove_small_holes(polygon, threshold):
        if polygon.interiors:
            # Keep only holes that are larger than the threshold
            new_interiors = [hole for hole in polygon.interiors 
                                if calculate_area(hole) > threshold]
            return Polygon(polygon.exterior, new_interiors)
        return polygon

    # Apply the function to each geometry in the GeoDataFrame
    gdf['geometry'] = gdf['geometry'].apply(lambda geom: remove_small_holes(geom, threshold))
    return gdf
    
# %% 讀取 TSV 檔案
'''
df = pd.read_csv(input_file, sep='\t')
# 將 geometry 列轉換為 shapely 對象
df['geometry'] = df['geometry'].apply(wkt.loads)
# 創建 GeoDataFrame
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
# print(gdf.crs)
'''
gdf = gpd.read_file(input_file)
#%% GCS(choose one)
interval_stats, gdf_update = area_interval_gcs(gdf)
print(interval_stats)

#%%
gdf_update = gdf_update[gdf_update['area_m2'] >= 100]

#%% 删除 'area_m2' 和 'area_interval' 列
gdf_update = gdf_update.drop(columns=['area_m2', 'area_interval'])

#%% 對每個 geometry 添加 buffer（這裡的 buffer 大小可以根據需要調整）
gdf_update['geometry'] = gdf_update['geometry'].buffer(10 / 6371000 / math.pi * 180, join_style = 'mitre') 

#%% 重设 gdf_update 的索引
gdf_update = gdf_update.reset_index(drop=True)

#%%
gdf_tmp_with_buffer_not_merged = gdf_update.copy()
#%%
gdf_update.to_csv('tz_filter_100m2_buffer_10m_not_merged.tsv', sep='\t', index=False)
# #%% 計算相交並合併 & 生成相交的连接图
# connection_graph = calculate_intersections_and_build_graph(gdf_update)

#%%
# 先讀取 tz_filter_100m2_buffer_10m_not_merged.tsv 這個檔案，命名為gdf_update，再往下做
input_filter_buffer = '/home/covmo/test_ian/Africa_raw_buildings/tz_filter_100m2_buffer_10m_not_merged.tsv'
df = pd.read_csv(input_filter_buffer, sep='\t') # 使用 pandas 讀取 TSV 文件
df['geometry'] = df['geometry'].apply(wkt.loads)    # 將 'geometry' 列轉換為 Shapely geometry 對象
gdf_update = gpd.GeoDataFrame(df, geometry='geometry')  # 將 DataFrame 轉換為 GeoDataFrame
gdf_update.set_crs("EPSG:4326", inplace=True)   # 指定適當的坐標參考系 (例如 WGS84: EPSG 4326)

#%% ################################################################################################
# Depth First Search (DFS) #########################################################################
####################################################################################################
start_time = time.time()
connection_graph = calculate_intersections_and_build_graph(gdf_update)  #計算相交並合併 & 生成相交的连接图
end_time = time.time()
print(f"Time for calculating intersections and building connection graph: {end_time - start_time} seconds")
start_time = time.time()
# 合并相连的几何体
visited = set()
merged_geometries = []

# Iterate over each node in the GeoDataFrame
for index in range(len(gdf_update)):
    if index not in visited:
        # Call the iterative DFS function
        current_geometries = dfs_iterative(index, connection_graph, visited, gdf_update)
        
        # Merge current geometries if any exist
        if current_geometries:
            merged_geom = unary_union(current_geometries)
            merged_geometries.append(merged_geom)
end_time = time.time()
print(f"Time for merging geometries (DFS): {end_time - start_time} seconds")

start_time = time.time()
# Create a new GeoDataFrame with merged geometries
gdf_merged_dfs = gpd.GeoDataFrame({
    'geometry': merged_geometries
})
end_time = time.time()
print(f"Time for creating new GeoDataFrame: {end_time - start_time} seconds")

#%% ################################################################################################
### breadth-first search (BFS) #####################################################################
####################################################################################################
connection_graph = calculate_intersections_and_build_graph(gdf_update)  #計算相交並合併 & 生成相交的连接图

visited = set()
merged_geometries = []
# Iterate over each node in the GeoDataFrame
for index in range(len(gdf_update)):
    if index not in visited:
        # Call the BFS function instead of DFS
        current_geometries = bfs_iterative(index, connection_graph, visited, gdf_update)
        
        # Merge current geometries if any exist
        if current_geometries:
            merged_geom = unary_union(current_geometries)
            merged_geometries.append(merged_geom)

# Create a new GeoDataFrame with merged geometries
gdf_merged_bfs = gpd.GeoDataFrame({
    'geometry': merged_geometries
})


#%% ################################################################################################
### r-tree  + dfs ##################################################################################
####################################################################################################
# 使用 R-tree 計算相交並合併 & 生成相交的连接图
start_time = time.time()
rtree_idx = build_r_tree(gdf_update)
end_time = time.time()
print(f"Time for building R-tree: {end_time - start_time} seconds")

start_time = time.time()
# 用 R-tree 和 DFS 來合併幾何
visited = set()
merged_geometries_rtree_dfs = []
for i in range(len(gdf_update)):
    if i not in visited:
        merged_geometry = dfs_rtree_iterative(i, rtree_idx, visited, gdf_update)
        merged_geometries_rtree_dfs.append(unary_union(merged_geometry))
end_time = time.time()
print(f"Time for merging geometries with R-tree and DFS: {end_time - start_time} seconds")

start_time = time.time()
# 創建合併後的 GeoDataFrame
gdf_merged_rtree_dfs = gpd.GeoDataFrame(geometry=merged_geometries_rtree_dfs, crs=gdf_update.crs)
end_time = time.time()
print(f"Time for creating merged GeoDataFrame: {end_time - start_time} seconds")

#%% ################################################################################################
### r-tree + bfs ###################################################################################
####################################################################################################
# 使用 R-tree 計算相交並合併 & 生成相交的连接图
# connection_graph, rtree_idx = calculate_intersections_and_build_graph(gdf_update)
rtree_idx = build_r_tree(gdf_update)

# 用 R-tree 和 BFS 來合併幾何
visited = set()
merged_geometries_rtree_bfs = []

for i in range(len(gdf_update)):
    if i not in visited:
        merged_geometry = bfs_rtree_iterative(i, rtree_idx, visited, gdf_update)
        merged_geometries_rtree_bfs.append(unary_union(merged_geometry))

# 創建合併後的 GeoDataFrame
gdf_merged_rtree_bfs = gpd.GeoDataFrame(geometry=merged_geometries_rtree_bfs, crs=gdf_update.crs)

#%%
####################################################################################################
### test ###########################################################################################
####################################################################################################
#%% leaf capacity
dir(rtree_idx.properties)
print("Leaf capacity:", rtree_idx.properties.get_leaf_capacity())

#%% 将合并后的 GeoDataFrame 输出为 GeoJSON 文件
output_file = '/home/covmo/test_ian/Africa_raw_buildings/tz_gdf_merged_bfs.geojson'  # 指定输出文件名
gdf_merged_bfs.to_file(output_file, driver='GeoJSON')

#%%
output_file = '/home/covmo/test_ian/Africa_raw_buildings/tz_gdf_merged_rtree_bfs.geojson'  # 指定输出文件名
gdf_merged_rtree_bfs.to_file(output_file, driver='GeoJSON')

#%% ################################################################################################
### post process ###################################################################################
####################################################################################################
# Classify holes by size in the given intervals and split MultiPolygon into Polygon rows
interval_stats, gdf_multipolygon_to_polygon = classify_holes_by_area(merged_gdf)
print(interval_stats)

#%% Fill holes that are smaller than a specified threshold
gdf_filled = fill_small_holes(gdf_multipolygon_to_polygon, fill_in_holes_threshold_area)

#%% test
# interval_stats, gdf_tmp = classify_holes_by_area(gdf_filled)
# print(interval_stats)

#%% Save or process the updated GeoDataFrame with holes filled
gdf_filled.to_csv(output_file, sep='\t', index=False)
