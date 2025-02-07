# linux
## 指令
```bash
ssh app03
exit
```
```bash
$ ll /opt/covmo/parser/hofn/NT2_GEO_POLYGON.tsv
-rw-r--r-- 1 covmo covmo 22280422 Nov 21 09:01 /data/covmo_config/gis_information/NT2_GEO_POLYGON.tsv
```
```bash
$ wc -l /data/covmo_config/gis_information/NT2_GEO_POLYGON.tsv
18679 /data/covmo_config/gis_information/NT2_GEO_POLYGON.tsv
```
```bash
$ head -2 /opt/covmo/parser/nt/20241121/Hofn/NT2_CELL_POLYGON_LTE.tsv
PU_ID   ENODEB_ID       CELL_ID POLYGON_STR     POLYGON_ID      HOFN_TYPE       POS_TYPE        POS_INDOOR_TYPE DIST_MIN        DIST_MA        X       ROAD_LEVEL
92037   70024   32              510010131304854 1       5       0       0       0       0
```
```bash
$ awk -F'\t' '$6==10 {print}' /opt/covmo/parser/nt/20241121/Hofn/NT2_CELL_POLYGON_LTE.tsv | wc -l
805
```
```bash
ianliu@IAN-M710T:/mnt/z$ awk -F'\t' '{print $4, $5}' ./VIL/20250205/highway.tsv  | uniq -c
      1 HOFN_TYPE ROAD_LEVEL
  29336 7 4
 154999 7 5
  16328 7 3
   8190 7 2
    240 7 1
```

- `htop`: 查詢正在跑的程式
- `pwd` (print working directory): 查詢當前檔案夾位置
- 切分大檔案: `split -b 6G large_file.geojson small_part_`
- 停止指令後release memory:
    1. **List Background Jobs**: `jobs`
    2. **Bring the Process to Foreground**: `fg %1`  # replace 1 with the job number from the jobs list
    3. **Terminate the Process**: `Ctrl + C`

- 印出tsv檔指定內容
    - print all columns name: `head -n 1 [file name].tsv`
    - print indicated column info: `awk -F'\t' '{print $[num of column]}' NT2_GEO_POLYGON.tsv | sort -u`
        - ```bash
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
    - word count: `wc`
        ```bash
        8  6 46 test.txt
        // file has 8 lines, 6 words, and 46 bytes
        ```
    - To determine the row number of the line where the value 7 appears in the 5th column:
        ```bash
        $awk -F'\t' '$5 == 7 {print NR}' NT2_GEO_POLYGON.tsv
        211068
        ```
        - `-F'\t'`: Specifies that the file is tab-delimited.
        - `$5 == 7`: Checks if the value in the 5th column is equal to 7.
        - `{print NR}`: Prints the line number (NR) of the matching row.
    - To print the entire row for a specific line number:
        ```bash
        $sed -n '211068p' NT2_GEO_POLYGON.tsv
        208010726532962 "Rond-Point de  Toulsiac'h"     LINESTRING (-3.13493 47.62032, -3.13490 47.62040, -3.13491 47.62047, -3.13495 47.62051, -3.13502 47.62056, -3.13512 47.62058, -3.13522 47.62058, -3.13528 47.62056, -3.13535 47.62052, -3.13540 47.62047, -3.13541 47.62041, -3.13541 47.62037, -3.13536 47.62030, -3.13529 47.62026, -3.13525 47.62025, -3.13516 47.62024, -3.13508 47.62024, -3.13501 47.62026, -3.13493 47.62032, -3.13490 47.62022, -3.13485 47.62015, -3.13456 47.61981, -3.13409 47.61933, -3.13218 47.61738, -3.13174 47.61695, -3.13156 47.61677, -3.13073 47.61592, -3.12922 47.61437, -3.12875 47.61392)  7       3
        ```
        - `sed -n`: Prevents sed from printing all lines.
        - `211068p`: Specifies that only the 211068th line should be printed.