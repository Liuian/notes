# Sharing Report
## (OK) 0. Outline
1. What is PU_RULE?
2. Why do we need automatic clustering?
3. Results
4. What is herarchical Clustering?
5. About the program
6. Demonstration - QGIS.
7. Future work & improvements

## (OK) 1. What is PU_RULE?
- slide
    - ![pu_rule_vil](./image/pu_rule.jpg)
    - All site data within a polygon must run on one server.
    - Restrictions
        1. Polygons must cover the entire area withour overlaps.
        2. Traffic should be balanced.
        3. Polygons should be as round as possiable (avoid irregular shapes).
        4. Consider geographical constraints:
            - Avoid splitting along roads.
            - Consider water bodies.
            - ![geo_constraints](./image/geo_constraints.jpg)

## (OK) 2. Why do we need automatic clustering?
- slide 1
    - Manual clustering is time-consuming.
    - Nigeria has 147 PUs. Each split takes ~3 tries, totaling ~4 days.
    - ![pu_rule_nigeria](./image/pu_rule_nigeria_147-pus.jpg)

## (OK) 3. Results
- ![vil_mag](./image/vil_mag.jpg)
- ![vil_mum](./image/vil_mum.jpg)
<!-- - (optional) *Show a graph (STC)*   -->

## (OK) 4. What is herarchical Clustering
- Clustering
    1. ![alt text](./image/clustering-1.png) - [Hierarchical Clustering - Pyecontech](https://pyecontech.com/2020/06/12/hierarchical_clustering/)
    2. ![alt text](./image/clustering-2.png) - [Hierarchical Clustering - Pyecontech](https://pyecontech.com/2020/06/12/hierarchical_clustering/)
    3. ![alt text](./image/clustering-3.png) - [Hierarchical Clustering - Pyecontech](https://pyecontech.com/2020/06/12/hierarchical_clustering/)
    4. ![alt text](./image/clustering-4.png) - [Hierarchical Clustering - Pyecontech](https://pyecontech.com/2020/06/12/hierarchical_clustering/)
    5. ![alt text](./image/clustering-5.png) - [Hierarchical Clustering - Pyecontech](https://pyecontech.com/2020/06/12/hierarchical_clustering/)
- Groups
    1. ![alt text](./image/groups-1.png) - [Hierarchical Clustering - Pyecontech](https://pyecontech.com/2020/06/12/hierarchical_clustering/)
    2. Can be split into 1 ~ n-1 groups.
- Methods
    1. ![alt text](./image/methods-1.png) - [Hierarchical Clustering - Pyecontech](https://pyecontech.com/2020/06/12/hierarchical_clustering/)
    2. ![alt text](./image/methods-2.png) - [Sicket-learn - Clustering](https://scikit-learn.org/1.5/modules/clustering.html#adding-connectivity-constraints)

## (OK) 5. About program
- ![flow chart](./image/flowchart_auto_split_pu.jpg)
<!-- https://miro.com/app/board/uXjVLghSrsE=/?share_link_id=878699878928 -->

- How I extract groups with indicated traffic?
    1. ![dendrogram](./image/dendrogram-1.png)

- Example - VIL
    1. results:  
        
        1. 
            ```Best Method: average, Groups Found: 3
            Best Method: single, Groups Found: 3
            Best Method: ward, Groups Found: 1
            Best Method: average, Groups Found: 1
            Best Method: ward, Groups Found: 1
            Best Method: single, Groups Found: 1
            ```

        2. 
            ```Final Group RRC Sums:
            Group 1: RRC Sum = 380,742,957.0
            Group 2: RRC Sum = 391,271,196.0
            Group 3: RRC Sum = 381,593,076.0
            Group 4: RRC Sum = 400,449,884.0
            Group 5: RRC Sum = 419,666,424.0
            Group 6: RRC Sum = 392,971,329.0
            Group 7: RRC Sum = 397,741,592.0
            Group 8: RRC Sum = 393,110,610.0
            Group 9: RRC Sum = 412,846,580.0
            Group 10: RRC Sum = 381,585,537.0
            ```

        3. Maps of each step:
            1. ![map](./image/map-1.png)
            2. ![map](./image/map-2.png)
            3. ![map](./image/map-3.png)
            4. ![map](./image/map-4.png)
            5. ![map](./image/map-5.png)
            6. ![map](./image/map-6.png)


## (OK) 6. Demostraction - QGIS
- QGIS
    1. VIL
    2. STC

## (OK) 7. Future work
- Some clusters form around another cluster and need manual adjustment.
- Some remaining clusters have too much ot too little traffic, requiring manusl fixes.
- Improve the algorithm.
- Explore other clustering algorithms.

## (OK) 8. Final pages
- Any questions?

- References 
    - hierarchical clustering
        - [Hierarchical Clustering - Pyecontech](https://pyecontech.com/2020/06/12/hierarchical_clustering/)
        - [Sicket-learn - Clustering](https://scikit-learn.org/1.5/modules/clustering.html#adding-connectivity-constraints)
        - [YouTube - Hierarchical Clustering Explained](https://www.youtube.com/watch?v=uWf__KIKzPQ)
    - References - others
        - [K-Means Clustering](https://chih-sheng-huang821.medium.com/%E6%A9%9F%E5%99%A8%E5%AD%B8%E7%BF%92-%E9%9B%86%E7%BE%A4%E5%88%86%E6%9E%90-k-means-clustering-e608a7fe1b43)

- Thank you.