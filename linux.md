# linux
## 指令
- 查詢正在跑的程式: `htop`
- 查詢當前檔案夾位置: `pwd`
- 切分大檔案: `split -b 6G large_file.geojson small_part_`
- 停止指令後release memory:
    1. **List Background Jobs**: `jobs`
    2. **Bring the Process to Foreground**: `fg %1`  # replace 1 with the job number from the jobs list
    3. **Terminate the Process**: `Ctrl + C`
