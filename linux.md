# linux
## 指令
```
ssh app03
exit
```
```
$ ll /opt/covmo/parser/hofn/NT2_GEO_POLYGON.tsv
-rw-r--r-- 1 covmo covmo 22280422 Nov 21 09:01 /data/covmo_config/gis_information/NT2_GEO_POLYGON.tsv
```
```
$ wc -l /data/covmo_config/gis_information/NT2_GEO_POLYGON.tsv
18679 /data/covmo_config/gis_information/NT2_GEO_POLYGON.tsv
```
```
$ head -2 /opt/covmo/parser/nt/20241121/Hofn/NT2_CELL_POLYGON_LTE.tsv
PU_ID   ENODEB_ID       CELL_ID POLYGON_STR     POLYGON_ID      HOFN_TYPE       POS_TYPE        POS_INDOOR_TYPE DIST_MIN        DIST_MA        X       ROAD_LEVEL
92037   70024   32              510010131304854 1       5       0       0       0       0
```
```
$ awk -F'\t' '$6==10 {print}' /opt/covmo/parser/nt/20241121/Hofn/NT2_CELL_POLYGON_LTE.tsv | wc -l
805
```

- 查詢正在跑的程式: `htop`

- 查詢當前檔案夾位置: `pwd` (print working directory)

- 切分大檔案: `split -b 6G large_file.geojson small_part_`

- 停止指令後release memory:
    1. **List Background Jobs**: `jobs`
    2. **Bring the Process to Foreground**: `fg %1`  # replace 1 with the job number from the jobs list
    3. **Terminate the Process**: `Ctrl + C`

- 印出tsv檔指定內容
    - print all columns name: `head -n 1 [file name].tsv`
    - print indicated column info: `awk -F'\t' '{print $[num of column]}' NT2_GEO_POLYGON.tsv | sort -u`
        ```bash
        1
        11
        2
        7
        HOFN_TYPE
        ```
    - print indicated column num of rows: `awk -F'\t' '{print $4}' NT2_GEO_POLYGON.tsv | sort | uniq -c`
        ```bash
           828 1
        130426 11
            69 2
          4128 7
             1 HOFN_TYPE
        ```
    - print rows count: `wc -l NT2_GEO_POLYGON.tsv`
        ```bash
        1971 NT2_GEO_POLYGON.tsv
        ```