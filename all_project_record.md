# Table of Contents
- [82109 Uganda PU_rule](#82109-uganda-pu_rule)

- [82139 Telkomsel add Ferry Route into NT2_GEO_POLYGON](#82139-telkomsel-add-ferry-route-into-nt2_geo_polygon)

- [82154 STC-VDT Provide roads with road_level-7 in the polygon PU73118 osm_offline_parser -locli](#82154-stc-vdt-provide-roads-with-road_level-7-in-the-polygon-pu73118-osm_offline_parser-locli)

- [81651 Create Africa PU rule for Nigeria](#81651-create-africa-pu-rule-for-nigeria)

- [81068 Africa 14 countries GIS landusage](#81068-africa-14-countries-gis-landusage)
  - [TZ (Tanzania)](#tz-tanzania)
    - [NT2_GEO_POLYGON_Tanzania](#nt2_geo_polygon_tanzania_81068)
    - [PU_Building_TZ](#pu_building_tanzania_81068)
  - [UG_Uganda_81068](#ug_uganda_81068)
    - [NT2_GEO_POLYGON_UG](#nt2_geo_polygon_ug_81068)
  - [NG_Nigeria_81068](#ng_nigeria_81068)
  - [PU_building for 12 countries](#pu_building-for-12-countries)
    - [1. UG (Uganda) 2. KE (Kenya) 3. ZM (Zambia) 4. CD (Democratic Republic of Congo) 5. CG (Republic of Congo) 6. GA (Gabon) 7. MG (Madagascar) 8. MW (Malawi) 9. NE (Niger) 10. RW (Rwanda) 11. SC (Seychelles and dependencies) 12. TD (Chad)](#1-ug-uganda-2-ke-kenya-3-zm-zambia-4-cd-democratic-republic-of-congo-5-cg-republic-of-congo-6-ga-gabon-7-mg-madagascar-8-mw-malawi-9-ne-niger-10-rw-rwanda-11-sc-seychelles-and-dependencies-12-td-chad)


- [79379 Prepare GIS and Hofn module for 2degrees (New Zealand)](#79379-prepare-gis-and-hofn-module-for-2degrees-new-zealand)
  - [NT2_GEO_POLYGON(1 Water, 2 Coastline, 7 Highway)](#nt2_geo_polygon_newzealand)
  - [PU_building](#pu_building_79379)

- [81019 Add new 3D building for Telkomsel](#81019-add-new-3d-building-for-telkomsel)
  - [3D_building](#3d_building)

- [80645 Maldives](#80645-maldives)
  - [NT2_GEO_POLYGON(10 ferry)](#nt2_geo_polygon_maldives)


# 82109 Uganda PU_rule
- provide total RRC for 'ZTE' and 'Huawei' in different region:

    **Huawei**
    | **Vendor** | **Region** | **Total RRC** |
    |-----|------|------|
    | Huawei | East 1 | 407,766,588 |
    | Huawei | East 2 | 100,156,171 |
    | Huawei | Central 1 | 498,981,566 |
    | Huawei | Central 2 | 319,297,450 |
    | Huawei | North | 97,614 |
    | Huawei | West 1 | 9,847,672 |
    | Huawei | Kampala | 1,082,208,881 |

    - No sites found for WestNile.
    - No sites found for West 2.

    **ZTE**
    | **Vendor** | **Region** | **Total RRC** |
    |------|-----|------|
    | ZTE | East 1 | 14,180,948 |
    | ZTE | East 2 | 18,968,266 |
    | ZTE | Central 1 | 80,040,219 |
    | ZTE | Central 2 | 8,095,005 |
    | ZTE | North | 29,470,466 |
    | ZTE | WestNile | 15,232,893 |
    | ZTE | West 1 | 44,474,154 |
    | ZTE | West 2 | 78,559,083 |

    - No sites found for Kampala.

    - ![alt text](./image/82109-4.png)

- source data prepropocess: Eliminate all gaps between regions and fix any incorrect regions boundry and clean some not necessery polygon.
    - run `program_PU_rule/1_preprocess_boundries.py`
      ||clean unnecessary polygon|fix region boundry|
      |-----|-----|-----|
      |before|![alt text](./image/82109-2.png)|![alt text](./image/82109.png)|
      |after| ![alt text](./image/82109-3.png)|![alt text](./image/82109-1.png)|

- run `3-2.append_polygon_into_file.py` to append new data

- run `4-validation_pu_rule.py`

|Before|After-ZTE|After-Huawei|
|-----|-----|-----|
| ![alt text](./image/82109-before.png)| ![alt text](./image/82109-after-zte.png)| ![alt text](./image/82109-after.png)

# 82139 Telkomsel add Ferry Route into NT2_GEO_POLYGON
- ferry route width adjust
```python
# osm_offlinw_parser/src/line.py
# line 116
if IS_BUFFER: #Hofn_type = ferry 航線生成一個??米的緩衝區
    result_gdf[DataColumns.GEOMETRY.value] = result_gdf.geometry.apply(lambda geometry: geometry.buffer(50 / 6371000 / math.pi * 180))

# osm_offline_parser/resource/config.ymal
Indonesia:
    mcc: "510"
    relation: "304751"

# osm_offline_parser/src/attribute.py
Indonesia = country_config.get("Indonesia").get("mcc"), country_config.get("Indonesia").get("relation")    
```
- `python osm_offline_parser.py ./data/input/indonesia-latest.osm.pbf 510 10`
- `python geo_polygon_generator.py 510 '10'`
- filter two ferry route: `./nt2_geo_polygon/extract_indicated_polygon.py`
- merge same ferry route name: `./nt2_geo_polygon/ferry_merge_polygon.py`
    - ferry route name `Ketapang - Gilimanuk` have 5 rows initally, merge into one route
        |original-1|original-2|merged|
        |------|-----|-----|
        |![alt text](./image/82139-1.png)|![alt text](./image/82139-2.png)|![alt text](./image/82139.png)|
- merge old and new `NT2_GEO_POLYGON.tsv` file: `./nt2_geo_polygon/merge_tsv.py`
- put in directry `\\INTERNAL1\Project3\CovMo\Module\Geolocation\Landusage_Hofn\Project_base_OSM_data\TKSL\20241031`
- write `readme` and `redmine`

# 82154 stc-vdt provide roads with road_level-7 in the polygon pu73118 osm_offline_parser locli
- input: `./data/input/gcc-states-latest.osm.pbf`
- output: `./data/output/Saudi_arabia/highway/custom/post_processed/highway.tsv`

1. run `python osm_offline_parser.py ./data/input/gcc-states-latest.osm.pbf 420 7`
    - since need `processed.osm.pbf` to use argument `-locli`
    - `./data/output/Saudi_arabia/limit_polygon/['307584']/processed.osm.pbf`

2. draw a handmade polygon by WKT provied by PM and put in right directory.
    - output from geojson.io: `map.geojson`
    - name as: `limit_polygon.geojson`
    - locate .geojson file in path: `./data/output/Saudi_arabia/limit_polygon/custom`
    - create directory `custom` manually.
    - ![alt text](./image/82154-geojson_io.png)

3. execute program using command `python osm_offline_parser.py ./data/input/gcc-states-latest.osm.pbf 420 7 -locli`

4. output: `./data/output/Saudi_arabia/highway/custom/post_processed/highway.tsv`
    | overview | zoom in |
    |------|-----|
    | ![alt text](./image/82154_overview_STC_PU73118_road_level_7.png)|![alt text](./image/82154_zoom_in_stc_pu73118_road_level_7.png)|

# 81651 Create Africa PU rule for Nigeria 
1. pin site location in the map with each vendor(Nokia, Hnawei, ZTE) 
    <!-- - ![alt text](./image/81651-0.png) -->
    - <img src="./image/81651-0.png" alt="description" height="500">

    - columns: `Siteid(enodebid)`, `Latitude`, `Longitude`, `Vendor_name`, `RRC`
2. Split PU for each districts
    |district|Before|After|
    |-----|------|-----|
    | Agege |![alt text](./image/81651-2.png)|![alt text](./image/81651-1.png)|

    - district with multipule vendor - split two vendor first
        |before|after|
        |-----|-----|
        | ![alt text](./image/81651-4.png) | ![alt text](./image/81651-3.png) |
    
    - calculate RRC in rach area
        - ![alt text](./image/81651-5.png)
    
    |Before|After|
    |-----|------|
    |![alt text](./image/81651-6.png)|![alt text](./image/81651-7.png)|
# 81068 Africa 14 countries GIS landusage
## Add 14 countries' information into program

- `./resource/config.yaml`
    - find relation
        - link: https://nominatim.openstreetmap.org/ui/search.html
        <!-- - ![alt text](image.png) -->
        - <img src="./image/81068-0.png" alt="description" height="500">
        - ![alt text](./image/81068-1.png)

    ``` python
    Tanzania:
        mcc: "640"
        relation: "195270"
    Uganda:
        mcc: "641"
        relation: "192796"
    Nigeria:
        mcc: "621"
        relation: "192787"
    etc...
    ```
    
- `./src/attributes.py`
    ``` python
    Tanzania = country_config.get("Tanzania").get("mcc"), country_config.get("Tanzania").get("relation")    
    Uganda = country_config.get("Uganda").get("mcc"), country_config.get("Uganda").get("relation")    
    Nigeria = country_config.get("Nigeria").get("mcc"), country_config.get("Nigeria").get("relation")    
    etc...
    ```
## TZ (Tanzania)
### NT2_GEO_POLYGON_Tanzania_81068
- note : osm_offline_parser.py different Hofn type should be execute seperately
- **1 water, 2 coast line, 7 highway, 11 village**
- 1 water
    - command: `python osm_offline_parser.py ./data/input/tanzania-latest.osm.pbf 640 '1'`
    - filter:  `area_threshold` 40000 (m^2), `area_perimeter_ratio_threshold` 0.35 
- 2 coastline
    - pin NT into map for filter
        - <img src="./image/81068-5.png" alt="description" height="500">
    - all coastline
        - <img src="./image/81068-4.png" alt="description" height="500">
    - draw an area manually in https://geojson.io/#map=2/0/20
        - locate .geojson in path: `./data/output/Tanzania/limit_polygon/custom`
        - name as: `limit_polygon.geojson`
        <!-- - ![alt text](image-2.png) -->
        - <img src="./image/81068-2.png" alt="description" height="500">
    1. coastline
        - download whole Africa data `africa-lastest.osm.pbf`
        - command: `python osm_offline_parser.py ./data/input/{}.osm.pbf 640 2 -locli`
        - filter: <4000 (m)
    2. 3 areas at lack in the country boundry
        - command: `python osm_offline_parser.py ./data/input/tanzania-latest.osm.osm.pbf 640 1 -relation 2606941 -locli`
            - `./data/output/Tanzania/water/custom/raw_processed/water_relation_[2606941].tsv`
            - `./data/output/Tanzania/water/custom/raw_processed/island.tsv`
            <!-- ![alt text](image-3.png) -->
            - <img src="./image/81068-3.png" alt="description" height="500">
    3. merge all data
- 7 highway
    - command: `python osm_offline_parser.py ./data/input/tanzania-latest.osm.pbf 640 '7'`
- 11 village
    - command: `python osm_offline_parser.py ./data/input/tanzania-latest.osm.pbf 640 '11'`

- **merge all data**
    - `python geo_polygon_generator.py 640 '1 2 7 11'`

- **Validation**
    - run `hofn.py`
    - **Input files 1:**  
        - **Path to put files 1:** `/home/covmo/test_ian/Hofn_v39/data/newzealand/input`
        - `NT2_GEO_POLYGON.tsv`  
        - `NT2_ANTENNA_{tech}.csv`  
        - `NT2_CELL_{tech}.csv`  
        - `NT2_NBR_VORONOI_LOC_{tech}.csv`  

    - **Input files 2:** `config.ini`
        - **Path to put files 2:** `/home/covmo/test_ian/Hofn_v39`
        - reminder: remember to modify `config.ini`

    - **command**: `python Hofn.py ./data/tanzania/input/ ./data/tanzania/output/`

    - **output files**:
        - `NT2_CELL_POLYGON_{tech}.tsv`  
        - `HOFN_CELL_INFO_{tech}.csv`  

    - **Put files into hofn_map**
        - **Path:** `/home/covmo/data/hofn_map`
        - **files**
            - `NT2_GEO_POLYGON.tsv`  
            - `NT2_CELL_POLYGON_{tech}.tsv`  
            - `HOFN_CELL_INFO_{tech}.csv`  
    
5. **FINISH**
    - write `log` in Hofn wiki
    - write `readme.txt` in `\\INTERNAL1\Project3\CovMo\Module\Geolocation\Landusage_Hofn\Project_base_OSM_data\`
    - reply ticket: provide screenshot in ticket

### PU_building_Tanzania_81068
- building data source: OVERTURE MAPS (https://github.com/OvertureMaps/overturemaps-py)

- rules
	1. filter buildings < 100 m^2
	2. buffer 10 meter
	3. merge overlap buildings
	4. fill in holes < 10000 m^2

- df shape: (30650235, 2) -> (963176, 1)

- details
- raw buildings area interval
```
                  Count  Percentage
area_interval                      
0-25 m²        12231271   39.905968
25-50 m²       10203346   33.289623
50-100 m²       5367343   17.511591
100-150 m²      1494281    4.875268
150-200 m²       683308    2.229373
200-250 m²       311780    1.017219
>250 m²          358901    1.170957
```
- holes after buffer and merge
```               Count  Percentage
0-10 m²        55866   35.690283
10-50 m²       34327   21.929981
50-100 m²      16131   10.305373
100-200 m²     15239    9.735514
200-500 m²     16411   10.484252
500-1000 m²     8623    5.508848
1000-1500 m²    3327    2.125471
1500-2000 m²    1796    1.147384
2000-10000 m²   4159    2.656999
>10000 m²        651    0.415895
```

- screenshot
    - <img src="./image/81068-6.png" alt="description" height="500">
    - der es-salaam
    - <img src="./image/81068-7.png" alt="description" height="500">

## UG_Uganda_81068
### NT2_GEO_POLYGON_UG_81068
- **1 water, 2 coastline, 7 highway, 11 village**

- `run_osm_offline_parser.py` to run 4 HOFN_TYPE together
    ```python
    commands = [
    ["python", "osm_offline_parser.py", "./data/input/uganda-latest.osm.pbf", "641", "1"],
    ["python", "osm_offline_parser.py", "./data/input/uganda-latest.osm.pbf", "641", "2"],
    ["python", "osm_offline_parser.py", "./data/input/uganda-latest.osm.pbf", "641", "7"],
    ["python", "osm_offline_parser.py", "./data/input/uganda-latest.osm.pbf", "641", "11"]
    ]
    ```

- **1 water**
    1. normal water(lakes, rivers)
        - area_threshold = 40000(m^2)
        - delete 43 polygons like this
            - ![alt text](image.png)

- **2 coastline**
    1. no real coastline from open street map

    2. water in country boundry seen as coastline
        - drow limit polygon in [geojson.io](https://geojson.io/#map=7.06/-0.181/32.384)
            - ![alt text](image-1.png)
        - save file as `.geojson`
        - rename as `limit_polygon.geojson`
        - move to directory `./data/output/Uganda/limit_polygon/custom/`
        - run pure `-locli` first. Command: `python osm_offline_parser.py ./data/input/uganda-latest.osm.pbf 641 1 -locli`
        - run with relation id. Command: ` python osm_offline_parser.py ./data/input/uganda-latest.osm.pbf 641 1 -relation 2606941 -locli`
            - find relation id in [open street map](https://www.openstreetmap.org/relation/2606941#map=7/-0.879/36.283)
        - output file path: `./data/output/Uganda/water/custom/raw_processed/water_relation_[2606941].tsv`
        - output file path: `./data/output/Uganda/water/custom/raw_processed/island.tsv`
            - use `PU_building` as a reference to select islands
                - ![alt text](image-2.png)
    
    3. merge all informations
        - run `lake-in-country-boundary_lake-boundary-and-island.py`
 
- **7 highway**
    - all data 

- **11 villege**
    - all data

- all screenshot
    | water | coastline | highway | villege |
    |-----|-----|-----|-----|
    | ![alt text](image-7.png) | ![alt text](image-3.png) | ![alt text](image-6.png) | ![alt text](image-5.png) |

- merge all hohn_type information
    - put all files into correct directory
    - 
## NG_Nigeria_81068
### PU_building_nigeria_81068

## PU_building for 12 countries
### 1. UG (Uganda) 2. KE (Kenya) 3. ZM (Zambia) 4. CD (Democratic Republic of Congo) 5. CG (Republic of Congo) 6. GA (Gabon) 7. MG (Madagascar) 8. MW (Malawi) 9. NE (Niger) 10. RW (Rwanda) 11. SC (Seychelles and dependencies) 12. TD (Chad)
- Continuously process 12 files by running `./pu_building/batch_processor.py`

## NG (Nigeria)
### NT2_GEO_POLYGON
### PU_building
## KE (Kenya)
### NT2_GEO_POLYGON
## ZM (Zambia)
### NT2_GEO_POLYGON
## CD (Democratic Republic of Congo)
### NT2_GEO_POLYGON
## CG (Republic of Congo)
### NT2_GEO_POLYGON
## GA (Gabon)
### NT2_GEO_POLYGON
## MG (Madagascar)
### NT2_GEO_POLYGON
## MW (Malawi)
### NT2_GEO_POLYGON
## NE (Niger)
### NT2_GEO_POLYGON
## RW (Rwanda)
### NT2_GEO_POLYGON
## SC (Seychelles and dependencies)
### NT2_GEO_POLYGON
## TD (Chad)
### NT2_GEO_POLYGON

# 79379 Prepare GIS and Hofn module for 2degrees (New Zealand)
## NT2_GEO_POLYGON_newzealand

- 1Water, 2Coastline, 7Highway

**readme**
- Hofn_type 1(Water):
	- filter: keep water bodies with an area > 70000(m^2)
	- filter: keep water bodies with area_perimeter_ratio > 0.1

- Hofn_type 2(coastline):
	- The two main islands(north island & south island) are seperated by 300(Km)
	- filter: keep costlines with a length > 5000(meters)
	- manually modify coastlines on the cross-ocean bridge 

- Hofn_type 7(highway): 
	- Road level 1-5

**procedure**

1. add New Zealand information into `OSM_offline_parser`
    * `./resource/config.yaml` line 132 add NewZealand

        ``` python
        NewZealand:
        mcc: "530"
        relation: "556706"
        ```
    * `./src/attributes.py` line 86 add NewZeland
        ``` python
        NewZealand = country_config.get("NewZealand").get("mcc"), country_config.get("NewZealand").get("relation")    
        ```
1. Road 1-5
    * 9857 Rows
    * `./resource/config.yaml` line 17 adjust target road level

        ```python
        highway:
            highway: [motorway, trunk, primary, secondary, tertiary] #1-5
        ```
    * command: `python  osm_offline_parser.py ./data/input/new-zealand-latest.osm.pbf 530 '7'`
    * output path: `/home/covmo/test_ian/osm_offline_parser/data/output/Newzealand/highway/['556706']/post_processed`

2. Water
    * command: `python osm_offline_parser.py ./data/input/new-zealand-latest.osm.pbf 530 '1'`
    
    * output path: `/home/covmo/test_ian/osm_offline_parser/data/output/Newzealand/water/['556706']/post_processed`
    
    * note: 
        1. below path `/home/covmo/test_ian/osm_offline_parser/data/output/Newzealand/water/['556706']/raw_processed` will generate two files 
            1. island.tsv - only include island in lake
            2. water.tsv - 
        2. will also generate island floder: `/home/covmo/test_ian/osm_offline_parser/data/output/Newzealand/island/['556706']/raw_processed/island.tsv`
            - `island.tsv` here include all islands (island in the ocean)
    
    - filter water (3195 rows -> 1534 rows)
        - run `water_filter.py`
        - drop area < 70000(m^2)
            ![alt text](./image/image-19.png)
        - drop area_perimeter_ratio < 0.1



3. Coastline: 
    - command: `python osm_offline_parser.py ./data/input/new-zealand-latest.osm.pbf 530 '2'`
    
    - find NT2_antenna_[tech] file to determine which coastline is necessery to keep
        - all cells are include in two main land

            ![alt text](./image/image-20.png)

    - filter: keep costlines with a length > 5000 (meter)
        - run `coastline_process.py`
        - coastline length distribution
            - ![alt text](./image/image-21.png)
        - 543 coastlines-> 120 coastlines

    - cut north island & south island coastline in threashole = 300 (Km)
        - need to run normal mode first.
        - command: `python osm_offline_parser.py ./data/input/new-zealand-latest.osm.pbf 530 2 -d 4801684`

        - Relation id 
            
            ![alt text](./image/image-22.png)

        - adjust divide costline length
            - `config.yaml`
            
                ![alt text](./image/image-26.png)

        - 300m: 
        
            ![alt text](./image/image-23.png)

        - 120 coastlines -> 171 coastlines
    
    - manually adjust cross oction bridge
        

        | before                          |after                          |
        |-----------------------------------|-----------------------------------|
        | ![alt text](./image/image-24.png)          | ![alt text](./image/image-25.png)          |

4. Concat `highway.tsv`, `coastline.tsv` and `water.tsv`
    * command: `python geo_polygon_generator.py 530 '1 2 7'`
    * output files:
        * `/home/covmo/test_ian/osm_offline_parser/data/output/Newzealand/NT2_GEO_POLYGON.csv`
        * `/home/covmo/test_ian/osm_offline_parser/data/output/Newzealand/NT2_GEO_POLYGON.tsv`
    * 11562 rows

6. **Validation**
    - run `hofn.py`
    - **prepare files**
        - **Input files 1:**  
            - **Path to put files 1:** `/home/covmo/test_ian/Hofn_v39/data/newzealand/input`
            - `NT2_GEO_POLYGON.tsv`  
            - `NT2_ANTENNA_LTE.csv`  
            - `NT2_ANTENNA_NR.csv`  
            - `NT2_CELL_LTE.csv`  
            - `NT2_CELL_NR.csv`  
            - `NT2_NBR_VORONOI_LOC_LTE.csv`  
            - `NT2_NBR_VORONOI_LOC_NR.csv`  

        - **Input files 2:** `config.ini`
            - **Path to put files 2:** `/home/covmo/test_ian/Hofn_v39`
            - reminder: remember to modify `config.ini`

    - **command**: `python Hofn.py ./data/newzealand/input/ ./data/newzealand/output/`

    - **output files**:
        - `NT2_CELL_POLYGON_LTE.tsv`  
        - `NT2_CELL_POLYGON_NR.tsv`  
        - `HOFN_CELL_INFO_LTE.csv`  
        - `HOFN_CELL_INFO_NR.csv`  

    - **Put files into hofn_map**
        - **Path:** `/home/covmo/data/hofn_map`
        - **files**
            - `NT2_GEO_POLYGON.tsv`  
            - `NT2_CELL_POLYGON_LTE.tsv`  
            - `NT2_CELL_POLYGON_NR.tsv`  
            - `HOFN_CELL_INFO_LTE.csv`  
            - `HOFN_CELL_INFO_NR.csv`

    ![alt text](./image/image-27.png)
    
5. **Reply ticket & add log in Hofn wiki**
    - provide screenshot in ticket


## PU_building_79379
0. step 1+2+3: run `PU_building.py` in vscode by jupygter
1. calculate building area interval

    ![alt text](./image/image-18.png)
    - PCS V.S. GCS

        | | PCS | GCS |
        |---|---|---|
        |cost time| 20 seconds | 5 mins 20 seconds |
        |adaptability| low | high |
        |screen shot| ![alt text](./image/image-10.png) | ![alt text](./image/image-7.png) |
        |method|![alt text](./image/image-8.png)|![alt text](./image/image-9.png)|


2. buffer & filter & merge
    - to select indicated area for visolization, run `select_area.py`
    - building count: 3490946 -> 524758(keep only 15%)

    | area | Raw Data | Buffer (10 meter) + Filter (100 m²) | Merged |
    | ------|----------|--------------------------------------|--------|
    | urben area(wellington) |![alt text](./image/image-4.png) | ![alt text](./image/image-5.png) |![alt text](./image/image-6.png)  |
    | rural area | ![alt text](./image/image-15.png)|![alt text](./image/image-16.png)|![alt text](./image/image-17.png)|

    references :   
    [GeoSeries.buffer documentation](https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.buffer.html)  
    [GeoSeries.unary_union documentation](https://geopandas.org/en/v0.10.0/docs/reference/api/geopandas.GeoSeries.unary_union.html)


3. fill in holes

    - count holes distribution

        ![alt text](./image/image-12.png)

    | Before | After |
    |------|-----|
    |![alt text](./image/image-1.png) |![alt text](./image/image-3.png)|

4. check output in QGIS
    - run `select_area.py` to select small area to show in QGIS

# 81019 Add new 3D building for Telkomsel
## 3D_building
**Note**
- 下次要做3D_building之前要先檢查(將第四支程式的內容移到一開始就先做)
    1. no null value
    2. invalid polygon -> valid
        - 有些會有小三角形或八字形，並且變成multipolygon
    3. all multipolygon -> polygon. 
        - 更改polygon_id編號部分要再精進，變為其中一行保留原始polygon_id，其他行找附近空的polygon_id。
    4. 所有資料(舊資料+所有新資料)比對是否有重複的polygon_id，修正到沒有再開始。
- 第二三隻程式可以融合在一起，做為第二步驟。
    - 第二支程式是從一開始搞building_id，改為將第三支程式的方法(找建築物群中最高的建築物polygon_id作為那一群建築物的building_id)融合進去
- 第三支程式保持原樣，將新舊資料融合

- 上傳的圖片可以加上zoom in 到一個小區域，把同樣building_id的渲染成同一個顏色，看是否正確。

**Details**

- Check:
    1. All geometries are valid
	    - some buildings are invalid -> validize by convert to multipolygon, split to polygons, reassign polygon_id
    2. All geometries type are Polygon 
	    - split to polygons, reassign polygon_id
    3. All `Polygon_ID` are unique
    4. No Null value 
	    - A building with null value in column `POLYGON_ID` is assigned as `103063173000010`
    5. (`AGL` & `AMSL` & `Building_max_AGL`) != 0
 
- Output files:
    - `3d_building_all` :　append all buildings
    - `3d_building.tsv` : filter `Building_max_AGL` < 20 (meter)
    - `3d_building.geojson` : filter `Building_max_AGL` < 20(meter) & drop columns 'Polygon_Centroid' & 'Building_max_AGL'

- new columns:(本次資料為電信商手動提供)
    - `Building_ID` and `Building_Name`: If two building intersect, their `building_ID` should be the same. Use highest building's `Polygon_name` as the ` Building_ID` and `Building_name` for the group(intersect buildings).
    - `Polygon_Centroid`: Assign each polygon's centroid.
    - `Building_max_AGL`: Assign the hightest building's `AGL` for the entire group(intersect buildings).

| Columns required| New File's Columns| Columns to Keep in new file| New Columns to Add in new file|
|-----------------------|-----------------------------|----------------------------------|----------------------------------------|
| WKT                   | Polygon_ID                  | Polygon_ID                      | Building_ID                           |
| Polygon_ID            | class                       | AGL                             | Building_Name                         |
| AGL                   | AGL                         | AMSL                            | Polygon_Centroid                      |
| AMSL                  | AMSL                        | geometry                        | Building_max_AGL                      |
| Building_ID           | Longitude                   |                                  |                                        |
| Building_Name         | Latitude                    |                                  |                                        |
| Polygon_Centroid      | geometry                    |                                  |                                        |
| Building_max_AGL      |                             |                                  |                                        |

|old data|new data|
|------|------|
|![alt text](./image/image-13.png)|![alt text](./image/image-14.png)|

**Procedure**
- run `1_merge_building_telkomsel.py`
- run `2_reassign_building_id.py`
- run `3_contact_old_and_new_data.py`
- run `4_agl_filter_output_tsv_geojson.tsv`
- run `5_check.py`

# 80645 Maldives
## NT2_GEO_POLYGON_maldives

**Added the ferry route to the NT2_GEO_POLYGON file.**  
The file now includes Hofn_type 1, 2, 7 (levels 1~6), and 10.  
Ferry road width is 100m.

### Original Hofn Type:
- 1: init water with site coverage
- 2: init coastline with site coverage
- 7: level 1 ~ 6

### Added Hofn Type:
- 10: ferry

### Procedure:
1. **Run osm_offline_parser**  
   - **Prepared file:**  
     - **Path:** `/home/covmo/test_ian/osm_offline_parser/data/input`  
     - **File name:** `maldives-latest.osm.pbf`
   - **Output file:**  
     - **Path:** `/home/covmo/test_ian/osm_offline_parser/data/output/Maldives`  
     - **File name:**  
       - `NT2_GEO_POLYGON.csv`  
       - `NT2_GEO_POLYGON.tsv`

   - **Path:** `/home/covmo/test_ian/osm_offline_parser`  
   - **Command:**  
     1. `python osm_offline_parser.py ./data/input/maldives-latest.osm.pbf 472 10`  
        - Manually move `ferry.tsv`  
          - From:  
            `/home/covmo/test_ian/osm_offline_parser/data/output/Maldives/ferry/['536773']/post_processed`  
          - To:  
            `/home/covmo/test_ian/osm_offline_parser/data/output/Maldives/ferry`
     2. `python geo_polygon_generator.py 472 '10'`

2. **Merge old & new GEO_POLYGON file**  
   - **Path:** `/home/covmo/test_ian/tools/merge_two_tsv`  
   - **Command:** `python merge_tsv.py ./data/NT2_GEO_POLYGON_old.tsv ./data/NT2_GEO_POLYGON_new.tsv`

3. **Run hofn.py**
   - **3.1 Prepared files:**
     - **3.1.1 Source data:** `/opt/covmo/parser/nt/nt_ready/`
     - **Path:** `/home/covmo/test_ian/Hofn_v39/data/maldives/input`
     - **Input files:**  
       - `NT2_GEO_POLYGON.tsv`  
       - `NT2_ANTENNA_GSM.csv`  
       - `NT2_ANTENNA_UMTS.csv`  
       - `NT2_ANTENNA_LTE.csv`  
       - `NT2_CELL_GSM.csv`  
       - `NT2_CELL_UMTS.csv`  
       - `NT2_CELL_LTE.csv`  
       - `NT2_NBR_VORONOI_LOC_GSM.csv`  
       - `NT2_NBR_VORONOI_LOC_UMTS.csv`
       - `NT2_NBR_VORONOI_LOC_LTE.csv`  

     - **3.1.2 Source data:**  
       - **Path:** `https://node82.ghtinc.com/configurations/hofn_configurations/blob/master/41.Maldives.config.ini`
       - **Path:** `/home/covmo/test_ian/Hofn_v39`
       - **Input file:** `config.ini`
       - **Reminder:** Remember to modify GEO_POLYGON input path & log output path

   - **3.2 Run hofn.py**  
     - **Path:** `/home/covmo/test_ian/Hofn_v39`
     - **Command:** `python Hofn.py ./data/maldives/input/ ./data/maldives/output/`

4. **Validation**
   - **4.1 Put files into hofn_map**
     - **Path:** `/home/covmo/data/hofn_map`
     - **Files:**  
       - `NT2_GEO_POLYGON.tsv`  
       - `HOFN_CELL_INFO_GSM.csv`  
       - `NT2_CELL_POLYGON_LTE.tsv`  
       - `HOFN_CELL_INFO_LTE.csv`  
       - `NT2_CELL_POLYGON_UMTS.tsv`  
       - `HOFN_CELL_INFO_UMTS.csv`  
       - `NT2_CELL_POLYGON_GSM.tsv`
   
   - **4.2 Open hofn map to check**

5. **Reply ticket & add log in Hofn wiki**
    - provide screenshot into ticket
