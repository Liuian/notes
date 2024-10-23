# %%
# 讀取GeoJSON檔案並轉換為GeoDataFrame
import pandas as pd
import geopandas as gpd
from pyproj import Geod

counties = gpd.read_file('county.geojson')
grid = gpd.read_file('self_grid.geojson')
#result = gpd.read_file('grid_intersection.geojson')

# %% 
# 檢查是否有無效的幾何對象&去除幾何對象為 None 的行
invalid_counties = counties[~counties.is_valid]
print(invalid_counties)
invalid_grids = grid[~grid.is_valid]
print(invalid_grids)
counties = counties[counties['geometry'].notnull()]

# %%
#multipolygn要轉成一個polygn
# counties = counties.explode().reset_index(drop=True)

# %%
# epsg:4326
# print(grid.crs)
# print(counties.crs)

# %%
# 計算相交的圖形
intersections = gpd.overlay(grid, counties, how='intersection')

# %%
# 使用 pyproj.Geod 計算面積
# TODO:計算的結果不正確，可能要往上trace相交圖形是否正確
geod = Geod(ellps="WGS84")

def calculate_area(geom):
    # 計算多邊形或集合多邊形的面積，返回的面積為平方米
    return abs(geod.geometry_area_perimeter(geom)[0])

intersections['area'] = intersections['geometry'].apply(calculate_area)
#result['area1'] = result['geometry'].apply(calculate_area)

# %%
#result
#intersections


# %%
# 將結果根據網格ID分組，並將每個網格內的縣市和面積加總
result = intersections.groupby('id').apply(lambda x: pd.Series({
    'num_of_district': x['CityName'].nunique(),  # 計算不同縣市的數量
    'area': x['area'].sum(),  # 計算總面積
    'geometry': x['geometry'].unary_union  # 合併所有幾何形狀
})).reset_index()  # 將結果轉換回一個標準的 DataFrame

# %%
result

# %%
# 將geodf換回geojson的格式
result.set_crs(epsg=4326, inplace=True)
result.to_file('output.geojson', driver='GeoJSON')

# %%
# intersections.set_crs(epsg=4326, inplace=True)
# f6_intersections = intersections[intersections['id'] == 'F6']
# f6_intersections.to_file('intersections_F6.geojson', driver='GeoJSON', encoding='utf-8')