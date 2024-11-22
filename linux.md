# linux
## 指令
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
        - example output
        ```bash
        1
        11
        2
        7
        HOFN_TYPE
        ```
    - print indicated column num of rows: `awk -F'\t' '{print $4}' NT2_GEO_POLYGON.tsv | sort | uniq -c`
        - example output:
        ```bash
           828 1
        130426 11
            69 2
          4128 7
             1 HOFN_TYPE
        ```
