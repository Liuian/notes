## why do this experiment?
| area | Raw Data | Buffer (10 meter) + Filter (100 m²) | Merged |
| ------|----------|--------------------------------------|--------|
| New Zealand(wellington) |![alt text](./image/image-4.png) | ![alt text](./image/image-5.png) |![alt text](./image/image-6.png)  |

- Africa Tanzania building after filter atill have 3,000,000 (3 million) buildings

## implimentation

### choosed methods
1. sindex + DFS
2. sindex + BFS
3. R-tree + DFS
4. R-tree + BFS

### summary
| method |**sindex**|**R-tree**|
|-----|-----|-----|
|**DFS**|9m 9.1s|26m 16.2s|
|**BFS**|9m 19.6s|23m 44.9s|

### detail
1. sindex + DFS
    - ![alt text](./image/research_pu_building-1.png)
    - each section's time
        - ![alt text](./image/research_pu_building-2.png)
2. sindex + BFS
    - ![alt text](./image/research_pu_building.png)

3. R-tree + DFS
    - ![alt text](./image/research_pu_building-6.png)
    - each section's time
        - ![alt text](./image/research_pu_building-4.png)
    - ![alt text](./image/research_pu_building-3.png)

4. R-tree + BFS
    - Leaf Capacity: 100
    - ![alt text](./image/research_pu_building-5.png)
    - ![alt text](./image/research_pu_building-3.png)

## 講解
1. DFS
    - ![alt text](./image/DFS-on-Graph-0.webp)
    - ![alt text](./image/DFS-on-Graph-1.webp)
    - ![alt text](./image/DFS-on-Graph-2.webp)
    - ![alt text](./image/DFS-on-Graph-3.webp)
    - ![alt text](./image/DFS-on-Graph-4.webp)
    - ![alt text](./image/DFS-on-Graph-5.webp)
    - references:
        - https://www.geeksforgeeks.org/depth-first-search-or-dfs-for-a-graph/
2. BFS
    - ![alt text](./image/BFS-on-Graph-1.webp)
    - ![alt text](./image/BFS-on-Graph-2.webp)
    - ![alt text](./image/BFS-on-Graph-3.webp)
    - ![alt text](./image/BFS-on-Graph-4.webp)
    - ![alt text](./image/BFS-on-Graph-5.webp)
    - ![alt text](./image/BFS-on-Graph-6.webp)
    - ![alt text](./image/BFS-on-Graph-7.webp)
    - references
        - https://www.geeksforgeeks.org/breadth-first-search-or-bfs-for-a-graph/

3. sindex
    - sindex output:
        - shape: (2, 11568726)
        - ![alt text](./image/research_pu_building-8.png)
    - transfer output into graph
        - ![alt text](./image/research_pu_building-7.png)

4. R-tree
    - ![alt text](./image/R-tree-1.png)
    - ![alt text](./image/R-tree-2.png)
    - references:
        - https://www.geeksforgeeks.org/introduction-to-r-tree/
        - https://youtu.be/Jd8F2hVnGtQ?si=keCwh-J9LqoXYeZh

## possiable reason for time of 'DFS' < 'BFS'
### 時間效率
- DFS (深度優先搜索)
    - 優點：在某些情況下，DFS 可以更快地找到解決方案，尤其是當建築物的結構較深或有很多分支時。由於其遞歸特性，它能夠迅速深入到建築物的細節中。
    - 缺點：如果搜尋空間很大，DFS 可能需要較長的時間來回溯，這可能會導致較慢的整體效率。

- BFS (廣度優先搜索)
    - 優點：BFS 在尋找最短路徑或最小合併步驟方面通常表現較好，因為它是層級式搜索，會先處理同一層的所有節點。
    - 缺點：BFS 可能需要更多的時間來處理大量的節點，特別是當每個建築物都有多個連結時，會造成更高的運算時間。

### 空間效率
- DFS (深度優先搜索)
    - 優點：空間效率通常較高，因為它只需儲存當前路徑上的節點（通常為 O(h)，h 是樹的高度），這使得它在空間上相對輕量。
    - 缺點：在最壞情況下，如果樹的高度很高，可能會導致堆疊溢出或較高的空間消耗。

- BFS (廣度優先搜索)
    - 優點：在某些情況下，BFS 可以更快地找到解決方案，因為它同時擴展多個節點。
    - 缺點：BFS 需要存儲所有節點（即所有同一層的節點），因此在空間上的需求較高，通常為 O(w)，w 是樹的最大寬度，這在大型建築物或高連結度的情況下會造成大量的記憶體消耗。

- ![alt text](./image/81068-7.png)
## possiable reason for time of 'sindex + DFS' << 'R-tree + DFS'
1. R-tree 索引構建成本： 雖然 R-tree 在空間查詢時能提升效率，但構建索引本身需要花費時間。對於非常大的資料集，建立 R-tree 可能會耗費相當多的時間，這會讓初始計算變慢。
    - sindex + DFS: ![alt text](./image/research_pu_building-2.png)
    - r-tree + DFS: ![alt text](./image/research_pu_building-4.png)

2. 範圍查詢(r-tree) vs 精確查詢(sindex)： R-tree 的運作方式是基於幾何邊界盒 (bounding box)，因此它只查找可能的相交幾何。即使兩個幾何體的邊界盒重疊，也不一定意味著實際幾何相交。因此，R-tree 查詢後仍需要進一步的幾何相交判斷，這增加了額外的計算量，尤其在碰到複雜幾何時。
    - ![alt text](./image/research_pu_building-9.png)

3. 原是資料相交測試次數增加： 雖然 R-tree 可以幫助篩選可能相交的幾何體，但若幾何體過於密集（有大量相交的情況），每次查詢可能會返回很多潛在的相交對象，導致後續的相交測試次數顯著增加，從而降低效率。
    - ![alt text](./image/81068-7.png)

#TODO: 從sindex套件中間截斷r-tree繼續做
#TODO: 全部相交的找完再一次合併union