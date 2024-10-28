# How variables handle mutable objects (like `lists`, `dicts`, and `DataFrames`) in Python
## Question 1
- python 函數中的變數為何也會更改到原始變數?在以下例子中，gdf被新增了面積及面積區間欄位。
```python
def calculate_area(geom):
    return abs(geod.geometry_area_perimeter(geom)[0])

def area_interval_gcs(gdf):
    # 計算每個 geometry 的面積，結果是平方米
    gdf['area_m2'] = gdf['geometry'].apply(calculate_area)
    # 定義區間
    bins = [0, 25, 50, 100, 150, 200, 250, float('inf')]
    labels = ['0-25 m²',  '25-50 m²', '50-100 m²', '100-150 m²', '150-200 m²', '200-250 m²', '>250 m²']
    # 將面積劃分到不同區間
    gdf['area_interval'] = pd.cut(gdf['area_m2'], bins=bins, labels=labels, include_lowest=True)
    # 統計每個區間的幾何數量
    interval_counts = gdf['area_interval'].value_counts().sort_index()
    # 計算每個區間所佔的百分比
    interval_percentage = (interval_counts / interval_counts.sum()) * 100
    # 將數量和百分比結合在一起
    result = pd.DataFrame({
        'Count': interval_counts,
        'Percentage': interval_percentage
    })
    # 顯示統計結果
    return result, gdf
interval_stats, gdf_update = area_interval_gcs(gdf)
print(interval_stats)
```
## Answer 1
In Python, understanding how variables handle mutable objects (like `lists`, `dicts`, and `DataFrames`) is key to understanding how changes propagate. Here’s a more in-depth explanation:

### 1. **Variable Assignment and References**
In Python, when you assign a variable to a mutable object (such as a `list`, `dict`, or `DataFrame`), the variable doesn't hold the actual object itself, but rather a **reference** to the object. This means that multiple variables can reference the same object in memory.

#### Example:
```python
a = [1, 2, 3]  # List is mutable
b = a  # b now references the same list object as a

b.append(4)  # Modify the list through b

print(a)  # Output: [1, 2, 3, 4]
```
In this example, modifying `b` also modifies `a` because they both refer to the **same list in memory**.

### 2. **Mutable vs. Immutable Objects**
- **Mutable objects**: These can be changed after they are created. Examples include `list`, `dict`, `set`, `DataFrame`, `GeoDataFrame`, etc.
- **Immutable objects**: These cannot be changed after creation. Examples include `int`, `float`, `tuple`, `str`, etc.

For **immutable** objects like strings, if you attempt to modify the object, Python creates a new object rather than modifying the original one.

#### Example (Immutable Objects):
```python
x = 5  # Integer is immutable
y = x
y += 1  # y now references a new object (6), x remains unchanged

print(x)  # Output: 5
print(y)  # Output: 6
```

In this case, modifying `y` does not affect `x` because integers are immutable. A new object is created instead.

### 3. **Passing Mutable Objects to Functions**
When you pass a mutable object (like a `GeoDataFrame`) to a function, the function receives a **reference** to the original object. This means that changes made to the object within the function affect the original object outside the function unless you explicitly create a copy of it.

#### Example (Passing a Mutable Object):
```python
def modify_list(my_list):
    my_list.append(4)  # Modify the list in place

lst = [1, 2, 3]
modify_list(lst)

print(lst)  # Output: [1, 2, 3, 4]
```
Here, `lst` is modified within the `modify_list` function because the list is mutable, and the function modifies the original object.

### 4. **Creating Copies to Prevent Unintended Changes**
If you don’t want changes to propagate to the original object, you need to create a **copy**. For mutable objects like `DataFrame` or `GeoDataFrame`, you can use `.copy()` to create a shallow copy.

#### Example (Using `copy()`):
```python
import pandas as pd

df = pd.DataFrame({'A': [1, 2, 3]})
df_copy = df.copy()  # Create a copy of the DataFrame

df_copy['A'] = df_copy['A'] + 10  # Modify the copy

print(df)  # Original DataFrame remains unchanged
# Output: 
#    A
# 0  1
# 1  2
# 2  3

print(df_copy)  # The copy is changed
# Output: 
#     A
# 0  11
# 1  12
# 2  13
```

Without `.copy()`, both `df` and `df_copy` would point to the same object, and changes in one would affect the other.

### 5. **Deep Copy vs. Shallow Copy**
- **Shallow copy** (`.copy()`): Creates a new object, but elements inside the object still reference the same objects. In case of complex data structures, like a `list` of `lists`, inner objects are not copied.
- **Deep copy** (`copy.deepcopy()`): Creates a completely new, independent copy of the entire structure, including any nested objects.

#### Example (Shallow Copy):
```python
import copy

a = [[1, 2], [3, 4]]
b = a.copy()  # Shallow copy

b[0].append(5)

print(a)  # Output: [[1, 2, 5], [3, 4]] - Inner list is modified
```

To avoid this, you can use a **deep copy**:
```python
b = copy.deepcopy(a)
```

### 6. **GeoDataFrame Example (Copy vs. Reference)**
Consider the following GeoDataFrame example, where the original data is modified inside the function because of passing by reference:

```python
import geopandas as gpd

def modify_gdf(gdf):
    gdf['new_column'] = gdf['geometry'].area

gdf = gpd.read_file('example.geojson')
modify_gdf(gdf)

print(gdf.head())  # 'new_column' is now in the original GeoDataFrame
```

To prevent this, use `.copy()`:

```python
def modify_gdf(gdf):
    gdf = gdf.copy()  # Now changes are made only to this copy
    gdf['new_column'] = gdf['geometry'].area
    return gdf
```

### Key Takeaways:
- **Mutable objects** (like `GeoDataFrame`, `DataFrame`, lists, etc.) are passed by reference, so changes inside a function affect the original object.
- To prevent modifying the original object, **make a copy** (`.copy()`).
- Immutable objects (like integers, strings) are passed by value, so they don't affect the original variable.

By keeping these behaviors in mind, you can control how your functions interact with mutable data and prevent unwanted side effects!

## Question 2
- why the last line `gdf_update = gdf_update[gdf_update['area_m2'] >= 100]` only change gdf_update but not gdf since you mentioned:
- In Python, when you assign a variable to a mutable object (such as a list, dict, or DataFrame), the variable doesn't hold the actual object itself, but rather a reference to the object.
```python
def calculate_area(geom):
    return abs(geod.geometry_area_perimeter(geom)[0])

def area_interval_gcs(gdf):
    # 計算每個 geometry 的面積，結果是平方米
    gdf['area_m2'] = gdf['geometry'].apply(calculate_area)
    # 定義區間
    bins = [0, 25, 50, 100, 150, 200, 250, float('inf')]
    labels = ['0-25 m²',  '25-50 m²', '50-100 m²', '100-150 m²', '150-200 m²', '200-250 m²', '>250 m²']
    # 將面積劃分到不同區間
    gdf['area_interval'] = pd.cut(gdf['area_m2'], bins=bins, labels=labels, include_lowest=True)
    # 統計每個區間的幾何數量
    interval_counts = gdf['area_interval'].value_counts().sort_index()
    # 計算每個區間所佔的百分比
    interval_percentage = (interval_counts / interval_counts.sum()) * 100
    # 將數量和百分比結合在一起
    result = pd.DataFrame({
        'Count': interval_counts,
        'Percentage': interval_percentage
    })
    # 顯示統計結果
    return result, gdf

interval_stats, gdf_update = area_interval_gcs(gdf)
print(interval_stats)

gdf_update = gdf_update[gdf_update['area_m2'] >= 100]
```
## Answer 2
Great question! Let's dive into why this line only changes `gdf_update` and not the original `gdf`:

```python
gdf_update = gdf_update[gdf_update['area_m2'] >= 100]
```

### Key Concept: Variable Assignment Creates a New Reference

When you execute this line of code:

```python
gdf_update = gdf_update[gdf_update['area_m2'] >= 100]
```

You are **re-assigning** the `gdf_update` variable to a **new subset** of the original `gdf_update` DataFrame where the `area_m2` values are greater than or equal to 100.

Here’s what happens step by step:

1. **Initial Reference**:
   When you return `gdf_update` from the `area_interval_gcs` function, both `gdf` and `gdf_update` still refer to the same underlying object (the same GeoDataFrame) at this point.

2. **New DataFrame Creation**:
   When you run this line:
   ```python
   gdf_update = gdf_update[gdf_update['area_m2'] >= 100]
   ```
   A **new DataFrame** is created. It contains only the rows where `area_m2 >= 100`. This new DataFrame is assigned to the variable `gdf_update`.

3. **Variable Reassignment**:
   The variable `gdf_update` now holds a reference to this new filtered DataFrame. This assignment **does not modify** the original `gdf` GeoDataFrame because the assignment only affects `gdf_update`'s reference. 

4. **Original Object Unaffected**:
   Since `gdf` still points to the original GeoDataFrame, and `gdf_update` now points to a new object (the filtered DataFrame), any subsequent changes to `gdf_update` will not affect `gdf`.

In summary:
- `gdf_update = gdf_update[gdf_update['area_m2'] >= 100]` filters and reassigns `gdf_update` to a new, smaller DataFrame, but **does not affect** the original `gdf`.
- If you wanted to modify the original `gdf` object itself, you would need to assign the result directly to `gdf` like this:
  ```python
  gdf = gdf[gdf['area_m2'] >= 100]
  ```

### Why Doesn’t `gdf` Change Automatically?
Because Python doesn’t automatically link a new assignment (like `gdf_update = ...`) to other variables that previously referred to the same object. After reassigning `gdf_update`, only `gdf_update` refers to the filtered DataFrame, while `gdf` remains as it was.

This distinction allows you to freely modify subsets of your data (as `gdf_update`) without impacting the original data (in `gdf`).

# steps to set up a system for processing multiple GeoJSON files using two separate Python files:
## 1. **Create `main_process.py`**
   - **Purpose**: Contains the core logic to process a single GeoJSON file.
   - **Function**: Define a function (e.g., `process_geojson(input_file, output_file)`) that takes the input GeoJSON file path and the output TSV file path as parameters.
   - **Content**: Include all necessary imports and the processing logic for reading the GeoJSON file, performing calculations, and saving the results as a TSV file.

## Example Structure of `main_process.py`
```python
import geopandas as gpd

def process_geojson(input_file, output_file):
    # Load the GeoJSON file
    gdf = gpd.read_file(input_file)
    
    # Perform processing (calculations, transformations, etc.)
    
    # Save the result to a TSV file
    gdf.to_csv(output_file, sep='\t', index=False)

# Optionally include a main block for testing
if __name__ == "__main__":
    process_geojson('example.geojson', 'output.tsv')
```

## 2. **Create `batch_processor.py`**
   - **Purpose**: Loops through all the GeoJSON files in a specified directory and calls the processing function from `main_process.py` for each file.
   - **Directory Setup**: Define input and output directories for the GeoJSON and processed files.
   - **File Loop**: Use `os.listdir()` to iterate through the files in the input directory, check for `.geojson` extensions, and call the processing function.

## Example Structure of `batch_processor.py`
```python
import os
from main_process import process_geojson  # Import the processing function

# Define directories
input_dir = '/path/to/your/geojson/files/'  # Directory with GeoJSON files
output_dir = '/path/to/save/processed/files/'  # Directory to save TSV files

# Create output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Process each GeoJSON file in the input directory
for file_name in os.listdir(input_dir):
    if file_name.endswith('.geojson'):
        input_file = os.path.join(input_dir, file_name)
        output_file = os.path.join(output_dir, file_name.replace('.geojson', '_processed.tsv'))
        
        # Call the process_geojson function
        process_geojson(input_file, output_file)

        print(f"Finished processing: {input_file}")
```

## Summary Steps
1. **Define processing logic in `main_process.py`**:
   - Write a function to process a single GeoJSON file.
   - Include the necessary logic to handle the GeoDataFrame and save it as a TSV file.

2. **Set up batch processing in `batch_processor.py`**:
   - Import the processing function.
   - Set up input and output directories.
   - Loop through the files, process each GeoJSON, and save the results.

3. **Run `batch_processor.py`**:
   - This script will process all GeoJSON files in the specified directory and save the results in the output directory. 

By organizing your code in this way, you can maintain a clean separation of concerns while making it easy to process multiple files efficiently.