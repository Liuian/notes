# Depth First Search(DFS)
## iterative method V.S. recursive method
## Method 1: iterative method
- Use iterative method is better. 
    ```python
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

    #%% 合并相连的几何体
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

    # Create a new GeoDataFrame with merged geometries
    merged_gdf = gpd.GeoDataFrame({
        'geometry': merged_geometries
    })
    ```

## Method 2: use recursive will meet error 
- `RecursionError: maximum recursion depth exceeded in comparison`
    ```python
    def dfs(node, connection_graph, visited, gdf_update, current_geometries):
        if node in visited:
            return
        visited.add(node)
        current_geometries.append(gdf_update.loc[node, 'geometry'])
        
        for neighbor in connection_graph[node]:
            dfs(neighbor, connection_graph, visited, gdf_update, current_geometries)
    visited = set()
    merged_geometries = []

    for index in range(len(gdf_update)):
        if index not in visited:
            current_geometries = []
            dfs(index, connection_graph, visited, gdf_update, current_geometries)
            
            # 合并当前连接的几何体
            if current_geometries:
                merged_geom = unary_union(current_geometries)
                merged_geometries.append(merged_geom)

    # 创建新的 GeoDataFrame
    merged_gdf = gpd.GeoDataFrame({
        'geometry': merged_geometries
    })
    ```