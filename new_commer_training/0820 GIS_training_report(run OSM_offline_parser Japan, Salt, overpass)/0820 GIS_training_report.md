# Run OSM_offline_parser - Japan with Hofn_type 1(water), 2(coastline), 7(1~3) (highway), 14(railway)
## 1. run osm_offline_parser.py
**1. execute directly for Hofn_type 1(water), 2(coastline) and 14(railway)**
 ```base
python osm_offline_parser.py ./data/input/japan-latest.osm.pbf 440 1
python osm_offline_parser.py ./data/input/japan-latest.osm.pbf 440 2
python osm_offline_parser.py ./data/input/japan-latest.osm.pbf 440 14
```
**2. select the road_level before executing for Hofn type 7(1~3) (highway)**

**(method 1) modify config.ymal**

![alt text](./image-6.png)
```base
python osm_offline_parser.py ./data/input/japan-latest.osm.pbf 440 7
```
**(method 2)from input line**
```base
python osm_offline_parser.py ./data/input/malaysia-singapore-brunei-latest.osm.pbf 525 7 -t highway:[motorway,trunk,primary]
```

## 2. run geo_polygn_gengerator.py
**merge**
```base
python geo_polygon_generator.py 440 '1 2 7 14'
```

# Run OSM_offline_paresr - salt(3D building)
```bash
python osm_offline_parser.py ./data/input/switzerland-latest.osm.pbf 228 9
```
* output: building.tsv
    * Hight & Level 很多 UNKNOWN

![alt text](./image-7.png)

![alt text](./image-10.png)

![alt text](./image-8.png)

# Research what was checked in the process
## geo_polygn_generator.py
**Validation:**
1. NO multi
  * Multipolygon & Multistring    
    ```python
    multi_polygon_df = hofn_df[hofn_df.geometry.apply(lambda x: x.type == "MultiPolygon")]
    multi_linestring_df = hofn_df[hofn_df.geometry.apply(lambda x: x.type == "MultiLineString")]
    ```
2. NO POLYGON_ID duplicate
3. check POLYGON_STR is valid.    
    0. only check for hofn_type == 1 5 10 11 2
    1.  ```python
        if hofn_type in ["1", "5", "10", "11"]:
                if not all(hofn_df[DataColumns.GEOMETRY.value].is_valid):
        ```
    2.  ```python
        elif hofn_type == "2":
                if not all(hofn_df[DataColumns.GEOMETRY.value].is_simple):
        ```
    * shapely: is_valid, is_simple    
        ![alt text](./image-9.png)

## osm_offline_parser.py
**procedure**
1. READ CONFIG
2. PROGRAM ARGUMENTS
3. Loading program arguments
    - input file path
    - hofn type
    - Get nation by mcc.
    - Limit polygon mode
    - Divide mode for lines with specified way id
    - Post processing mode
    - Output relation geometry
    - Grouping tags
    - use three lable to decide which process to do 
        ```python
        is_post_process = not is_process_only_output_relation_geometries
        is_divide_process = only_divide_ids is not None and not only_post_processing
        is_normal_process = not only_post_processing and not is_divide_process and not is_process_only_output_relation_geometries
        ```
4. log file setting & log info
5. 
    - cut down source data into area we need only
    - line 222 - line 248
    - ex: malaysia-singapore-brunei-latest.osm.pbf -> processed.osm.pbf(singapore only)
    - output file path: ./osm_offline_parser/data/output/Singapore/limit_polygon/['536780']/processed.osm.pbf
6. Entries


- 將Hofn-type分類
  ```yaml
  mode:
    rings: [ "1", "5",  "11" ]
    lines: [ "2", "7", "10", "6", "14", "3" ]
  ```
# overpass 

## Taipei MRT
TODO:如何用area ID指定搜尋的區域
```sql
[out:json][timeout:25];
//{{geocodeArea:Taipei}}->.searchArea;
area(3601293250)->.searchArea;
(
  way[railway=subway](area.searchArea);
);
out body;
>;
out skel qt;
```

```sql
[out:json][timeout:25];
{{geocodeArea:Taipei}}->.searchArea;
(
  way[railway=subway](area.searchArea);
);
out body;
>;
out skel qt;
```
![alt text](./image-1.png)

```sql
[out:json][timeout:25];
{{geocodeArea:Taipei}}->.searchArea;
(
   relation[route=subway](area.searchArea);
);
out body;
>;
out skel qt;
```
- 如果用relation會把台北以外的都帶出來

![alt text](./image-3.png)
## Taipei MRT Above ground parts
```sql
[out:json][timeout:25];
{{geocodeArea:Taipei}}->.searchArea;
(
  way[railway=subway][layer=1](area.searchArea);
);
out body;
>;
out skel qt;
```
* 只有way有layer屬性，realation & node 都沒有

![alt text](./image.png)

```sql
[out:json][timeout:25];
{{geocodeArea:Taipei}}->.searchArea;
(
  way[railway=subway][layer=1](area.searchArea);
  way[railway=subway][layer=2](area.searchArea);
);
out body;
>;
out skel qt;
```

![alt text](./image-2.png)

TODO: 如何知道layer的範圍

## Taipei + Taichung MRT
* search two region in the same time
* union several region
```sql
[out:json][timeout:55];
// Fetch areas "Taipei" and "Taichung" to search in
{{geocodeArea:Taipei}}->.taipeiArea;
{{geocodeArea:Taichung}}->.taichungArea;
(.taipeiArea; .taichungArea;)->.combinedArea;

(
  way[railway=subway](area.combinedArea);
);

out body;
>;
out skel qt;
```
![alt text](image-4.png)

## singapore water
```sql
[out:json][timeout:25];
// Fetch the area of Singapore
{{geocodeArea:Singapore}}->.searchArea;

// Gather results for water bodies within Singapore
(
  way[natural=water](area.searchArea);
  relation[natural=water](area.searchArea);
);

// Print results
out body;
>;
out skel qt;
```
* way, relation 都需要寫出來
* 因為有些湖只有一個way，所以不屬於任何relation
* 有的relation下的way完全沒有tag，必須要用relation才抓的到

![alt text](./image-5.png)

## useful links:
- Filter by area
How to get all data within a named area, e.g. a city or a county.: https://dev.overpass-api.de/overpass-doc/en/full_data/area.html