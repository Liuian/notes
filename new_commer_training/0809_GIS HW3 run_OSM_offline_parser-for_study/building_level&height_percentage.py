# %%
import pandas as pd

# 讀取TSV檔案
df = pd.read_csv("building.tsv", sep='\t')

# %%
# 計算 `height` 欄位中 "UNKNOWN" 的比例
height_unknown_count = df['HEIGHT'].str.upper().eq("UNKNOWN").sum()
height_total_count = df['HEIGHT'].count()
height_unknown_percentage = (height_unknown_count / height_total_count) * 100

# 計算 `level` 欄位中 "UNKNOWN" 的比例
level_unknown_count = df['LEVEL'].str.upper().eq("UNKNOWN").sum()
level_total_count = df['LEVEL'].count()
level_unknown_percentage = (level_unknown_count / level_total_count) * 100

print(f"Height Total: {height_total_count}, UNKNOWN: {height_unknown_count} ({height_unknown_percentage:.2f}%)")
print(f"Level Total: {level_total_count}, UNKNOWN: {level_unknown_count} ({level_unknown_percentage:.2f}%)")

# %%
# 將 `LEVEL` 欄位在 `HEIGHT` 有值的情況下，即使是 "UNKNOWN" 也視為非 "UNKNOWN"
df.loc[df['HEIGHT'].str.upper() != "UNKNOWN", 'LEVEL'] = df.loc[df['HEIGHT'].str.upper() != "UNKNOWN", 'LEVEL'].apply(lambda x: x if x.upper() != "UNKNOWN" else "")

# 計算 `HEIGHT` 欄位中 "UNKNOWN" 的數量和總數
height_unknown_count = df['HEIGHT'].str.upper().eq("UNKNOWN").sum()
height_total_count = df['HEIGHT'].count()
height_unknown_percentage = (height_unknown_count / height_total_count) * 100

# 計算 `LEVEL` 欄位中 "UNKNOWN" 的數量和總數
level_unknown_count = df['LEVEL'].str.upper().eq("UNKNOWN").sum()
level_total_count = df['LEVEL'].count()
level_unknown_percentage = (level_unknown_count / level_total_count) * 100

# 顯示結果
print(f"Height Total: {height_total_count}, UNKNOWN: {height_unknown_count} ({height_unknown_percentage:.2f}%)")
print(f"Level Total: {level_total_count}, UNKNOWN: {level_unknown_count} ({level_unknown_percentage:.2f}%)")
