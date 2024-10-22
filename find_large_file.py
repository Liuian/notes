import os

# 設定要檢查的資料夾路徑
folder_path = 'C:/Users/ianliu/Documents/notes'

# 設定檔案大小的閾值 (100 MB)
size_threshold = 100 * 1024 * 1024  # 100 MB in bytes

# 遍歷資料夾中的所有檔案並檢查大小
for root, dirs, files in os.walk(folder_path):
    for file in files:
        file_path = os.path.join(root, file)
        file_size = os.path.getsize(file_path)
        if file_size > size_threshold:
            # 打印出大於 100 MB 的檔案及其大小
            print(f'File: {file_path}, Size: {file_size / (1024 * 1024):.2f} MB')
