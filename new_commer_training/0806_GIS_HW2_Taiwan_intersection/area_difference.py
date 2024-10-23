# %%
import geopandas as gpd

# 讀取兩個 GeoJSON 檔案
geojson_pyproj = gpd.read_file('output_pyproj.geojson')
geojson_base = gpd.read_file('grid_intersection.geojson')

# 合併兩個 GeoDataFrame，根據 'id' 欄位對應
merged = geojson_pyproj.merge(geojson_base[['id', 'area']], on='id', suffixes=('_pyproj', '_base'))

# 保留 coordinates (geometry)
merged['geometry'] = geojson_pyproj['geometry']  # 使用第一個 GeoJSON 檔案的 geometry

# 計算面積差異百分比
merged['area_diff_percentage'] = (merged['area_pyproj'] - merged['area_base']) / merged['area_base'] * 100

# 選擇需要輸出的欄位
output_columns = ['id', 'area_pyproj', 'area_base', 'area_diff_percentage', 'geometry']

# 生成新的 GeoDataFrame
output_gdf = merged[output_columns]

# 設置 CRS（根據你需要的 CRS，這裡假設是 WGS84）
output_gdf.set_crs(epsg=4326, inplace=True)

# 將結果導出為新的 GeoJSON 檔案
output_gdf.to_file('merged_output.geojson', driver='GeoJSON')

# 顯示結果
print(output_gdf[['id', 'area_pyproj', 'area_base', 'area_diff_percentage']])
