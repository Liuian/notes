# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 10:02:53 2020

@author: sheldon
"""

import numpy as np
import geopandas as gpd
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import shapely.wkt as wkt
from shapely.ops import linemerge, nearest_points
import pyproj
import os
import warnings
from Hofn import date
from file_IO import *
warnings.filterwarnings(action='ignore', category=UserWarning)
warnings.filterwarnings('error', r'SettingWithCopyWarning')
import configparser
config = configparser.ConfigParser()
config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini')
config.read(config_file)
log_path = config['PATH']['log_path']
import logging
logging.basicConfig(level=logging.INFO,
                    format = '%(asctime)s [%(levelname)s] %(message)s',
                    datefmt = '%Y-%m-%d %H:%M:%S',
                    handlers = [logging.FileHandler(f'{log_path}{date}.log', 'a', 'utf-8'), logging.StreamHandler()])

region_dict = {'NR':'PU_ID', 'LTE':'PU_ID', 'UMTS':'RNC_ID', 'GSM':'BSC_ID'}
site_dict = {'NR':'GNODEB_ID', 'LTE':'ENODEB_ID', 'UMTS':'SITE_ID', 'GSM':'LAC'}
type_dict = {'NR':'GNODEB_TYPE', 'LTE':'ENODEB_TYPE', 'UMTS':'SITE_TYPE', 'GSM':'BTS_TYPE'}

def Poly1(dfcircles,geom1,tech):
    try:
        # logging.info(f'\tPoly1 process started (task pid:{os.getpid()})')
        region, site = region_dict[tech], site_dict[tech]
        if len(dfcircles)==0:
            return gpd.GeoDataFrame(None)
        dfcircles_extended = dfcircles.copy(deep=True)
        dfcircles_extended['geometry'] = dfcircles_extended['geometry'].buffer(10000/3.1415926/6378137*180)
        geom1_geoseries     = gpd.GeoSeries(geom1.geometry)
        dfcircles_geoseries = gpd.GeoSeries(dfcircles_extended.geometry)
        sidx = dfcircles_geoseries.sindex.query_bulk(geom1_geoseries, predicate="intersects")
        dfcircles_result    = dfcircles_extended.loc[sidx[1]][[region, site, 'CELL_ID']].reset_index(drop=True)
        geom1_result        = geom1.loc[sidx[0]][['POLYGON_ID', 'POLYGON_STR', 'HOFN_TYPE', 'ROAD_LEVEL']].reset_index(drop=True)
        assert len(geom1_result)==len(dfcircles_result)
        hofn1 = pd.concat([dfcircles_result, geom1_result], axis=1)
   
        if (len(hofn1)==0):
            return hofn1
        else:
            hofn1['POS_TYPE'] = 5
            hofn1['POS_INDOOR_TYPE'] = 0
            hofn1['DIST_MAX'] = 0
            hofn1['DIST_MIN'] = 0
            hofn1 = hofn1[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL']]
            hofn1['POLYGON_STR'] = ''
            hofn1 = hofn1.drop_duplicates(keep='first')
            return hofn1
    except Exception as e:
        logging.error(e,exc_info=True)
    

def Poly2(dfcircles,geom2,tech):
    try:
        # logging.info(f'\tPoly2 process started (task pid:{os.getpid()})')
        region, site = region_dict[tech], site_dict[tech]
        if len(dfcircles)==0:
            return gpd.GeoDataFrame(None)
        dfcircles_extended = dfcircles.copy(deep=True)
        dfcircles_extended['geometry'] = dfcircles_extended['geometry'].buffer(10000/3.1415926/6378137*180)
        geom2_geoseries     = gpd.GeoSeries(geom2.geometry)
        dfcircles_geoseries = gpd.GeoSeries(dfcircles_extended.geometry)
        sidx = dfcircles_geoseries.sindex.query_bulk(geom2_geoseries, predicate="intersects")
        dfcircles_result    = dfcircles_extended.loc[sidx[1]][[region, site, 'CELL_ID']].reset_index(drop=True)
        geom2_result        = geom2.loc[sidx[0]][['POLYGON_ID', 'POLYGON_STR', 'HOFN_TYPE', 'ROAD_LEVEL']].reset_index(drop=True)
        assert len(geom2_result)==len(dfcircles_result)
        hofn2 = pd.concat([dfcircles_result, geom2_result], axis=1)
        
        if (len(hofn2)==0):
            return hofn2
        else:
            names = locals()
            num = 1
            names[f'split{num}'] = []
            main_list = []
            for i in range(len(geom2)-1):
                id = geom2.loc[i, 'POLYGON_ID']
                names[f'split{num}'].append(id)
                line1 = geom2.loc[i, 'geometry']
                line2 = geom2.loc[i+1, 'geometry']
                line = linemerge([line1, line2])
                if (line.geom_type=='MultiLineString'):
                    if (len(names[f'split{num}'])>1):
                        names[f'main_df{num}'] = geom2[geom2['POLYGON_ID'].isin(names[f'split{num}'])].reset_index(drop=True)
                        names[f'main_df{num}']['id'] = names[f'main_df{num}'].index.values
                        names[f'main_df{num}_island'] = True if (names[f'main_df{num}'].loc[0, 'geometry'].intersects(names[f'main_df{num}'].loc[len(names[f'main_df{num}'])-1, 'geometry'])) else False
                        main_list.append((names[f'main_df{num}'], names[f'main_df{num}_island']))
                        num += 1
                    names[f'split{num}'] = []
                elif ((line.geom_type=='LineString') & (i==len(geom2)-2)): #for situation with main coastline sequence at the end of GEO file
                    id = geom2.loc[i+1, 'POLYGON_ID']
                    names[f'split{num}'].append(id)
                    names[f'main_df{num}'] = geom2[geom2['POLYGON_ID'].isin(names[f'split{num}'])].reset_index(drop=True)
                    names[f'main_df{num}']['id'] = names[f'main_df{num}'].index.values
                    names[f'main_df{num}_island'] = True if (names[f'main_df{num}'].loc[0, 'geometry'].intersects(names[f'main_df{num}'].loc[len(names[f'main_df{num}'])-1, 'geometry'])) else False
                    main_list.append((names[f'main_df{num}'], names[f'main_df{num}_island']))
                    
            def previous_coastline(hofn2, df_main, island_check):
                hofn2_previous = hofn2.copy(deep=True)
                hofn2_previous = hofn2_previous[[region, site, 'CELL_ID', 'POLYGON_ID']]
                hofn2_previous = hofn2_previous.merge(df_main, on='POLYGON_ID')
                hofn2_previous['id_previous'] = hofn2_previous['id']-1
                if (island_check==True):
                    hofn2_previous['id_previous'] = hofn2_previous['id_previous'].apply(lambda x: len(df_main)-1 if x==-1 else x)
                elif (island_check==False):
                    hofn2_previous = hofn2_previous[hofn2_previous['id_previous']>=0]
                hofn2_previous = hofn2_previous[[region, site, 'CELL_ID', 'id_previous']]
                hofn2_previous = hofn2_previous.merge(df_main, left_on='id_previous', right_on='id')
                hofn2_previous = hofn2_previous[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE']]
                return hofn2_previous
            
            def next_coastline(hofn2, df_main, island_check):
                hofn2_next = hofn2.copy(deep=True)
                hofn2_next = hofn2_next[[region, site, 'CELL_ID', 'POLYGON_ID']]
                hofn2_next = hofn2_next.merge(df_main, on='POLYGON_ID')
                hofn2_next['id_next'] = hofn2_next['id']+1
                if (island_check==True):
                    hofn2_next['id_next'] = hofn2_next['id_next'].apply(lambda x: 0 if x==len(df_main) else x)
                elif (island_check==False):
                    hofn2_next = hofn2_next[hofn2_next['id_next']<len(df_main)]
                hofn2_next = hofn2_next[[region, site, 'CELL_ID', 'id_next']]
                hofn2_next = hofn2_next.merge(df_main, left_on='id_next', right_on='id')
                hofn2_next = hofn2_next[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE']]
                return hofn2_next
                    
            hofn2 = hofn2.reset_index(drop=True)
            for mainline in main_list:
                hofn2_previous = previous_coastline(hofn2, mainline[0], mainline[1])
                hofn2_next = next_coastline(hofn2, mainline[0], mainline[1])
                hofn2 = pd.concat([hofn2, hofn2_previous, hofn2_next], axis=0)
                
            hofn2['POS_TYPE'] = 4
            hofn2['POS_INDOOR_TYPE'] = 0
            hofn2['DIST_MAX'] = 0
            hofn2['DIST_MIN'] = 0
            hofn2['ROAD_LEVEL'] = 0
            hofn2 = hofn2[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL']]
            hofn2['POLYGON_STR'] = ''
            hofn2 = hofn2.drop_duplicates(keep='first')
            return hofn2
    except Exception as e:
        logging.error(e,exc_info=True)

def Poly3(Mcell,geom3,tech):
    try:
        # logging.info(f'\tPoly3 process started (task pid:{os.getpid()})')
        region, site, sitetype = region_dict[tech], site_dict[tech], type_dict[tech]
        if len(Mcell)==0:
            return gpd.GeoDataFrame(None)
        Mcell_extended = Mcell[Mcell[sitetype]==3]
        Mcell_extended['geometry'] = Mcell_extended['geometry'].buffer(200/3.1415926/6378137*180)
        geom3_geoseries = gpd.GeoSeries(geom3.geometry)
        Mcell_geoseries = gpd.GeoSeries(Mcell_extended.geometry)
        sidx = Mcell_geoseries.sindex.query_bulk(geom3_geoseries, predicate="intersects")
        Mcell_result    = Mcell_extended.loc[sidx[1]][[region, site, 'CELL_ID']].reset_index(drop=True)
        geom3_result    = geom3.loc[sidx[0]][['POLYGON_ID', 'POLYGON_STR', 'HOFN_TYPE', 'ROAD_LEVEL']].reset_index(drop=True)
        assert len(geom3_result)==len(Mcell_result)
        hofn3 = pd.concat([Mcell_result, geom3_result], axis=1)
            
        if (len(hofn3)==0):
            return hofn3
        else:
            hofn3['POS_TYPE'] = 7
            hofn3['POS_INDOOR_TYPE'] = 1
            hofn3['DIST_MAX'] = 0
            hofn3['DIST_MIN'] = 0
            hofn3 = hofn3[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL']]
            hofn3['POLYGON_STR'] = ''
            hofn3 = hofn3.drop_duplicates(keep='first')
            return hofn3
    except Exception as e:
        logging.error(e,exc_info=True)
    
def Poly5(dfcircles,geom5,tech):
    try:
        # logging.info(f'\tPoly5 process started (task pid:{os.getpid()})')
        region, site = region_dict[tech], site_dict[tech]
        if len(dfcircles)==0:
            return gpd.GeoDataFrame(None)
        geom5_geoseries     = gpd.GeoSeries(geom5.geometry)
        dfcircles_geoseries = gpd.GeoSeries(dfcircles.geometry)
        sidx = dfcircles_geoseries.sindex.query_bulk(geom5_geoseries, predicate="intersects")
        dfcircles_result    = dfcircles.loc[sidx[1]][[region, site, 'CELL_ID']].reset_index(drop=True)
        geom5_result        = geom5.loc[sidx[0]][['POLYGON_ID', 'POLYGON_STR', 'HOFN_TYPE', 'ROAD_LEVEL']].reset_index(drop=True)
        assert len(geom5_result)==len(dfcircles_result)
        hofn5 = pd.concat([dfcircles_result, geom5_result], axis=1)
        
        if (len(hofn5)==0):
            return hofn5
        else:
            hofn5['POS_TYPE'] = 3
            hofn5['POS_INDOOR_TYPE'] = 0
            hofn5['DIST_MAX'] = 0
            hofn5['DIST_MIN'] = 0
            hofn5 = hofn5[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL']]
            hofn5['POLYGON_STR'] = ''
            hofn5 = hofn5.drop_duplicates(keep='first')
            return hofn5
    except Exception as e:
        logging.error(e,exc_info=True)
    
def Poly6(Tcells,geom6,tech):
    try:
        # logging.info(f'\tPoly6 process started (task pid:{os.getpid()})')
        region, site, sitetype = region_dict[tech], site_dict[tech], type_dict[tech]
        if len(Tcells)==0:
            return gpd.GeoDataFrame(None)
        buffer_dist = 100 if (5 in np.unique(Tcells[sitetype])) else 50
        Tcells_extended = Tcells.copy(deep=True)
        Tcells_extended['geometry'] = Tcells_extended['geometry'].buffer(buffer_dist/3.1415926/6378137*180)
        geom6_geoseries  = gpd.GeoSeries(geom6.geometry)
        Tcells_geoseries = gpd.GeoSeries(Tcells_extended.geometry)
        sidx = Tcells_geoseries.sindex.query_bulk(geom6_geoseries, predicate="intersects")
        Tcells_result    = Tcells.loc[sidx[1]][[region, site, 'CELL_ID']].reset_index(drop=True)
        geom6_result     = geom6.loc[sidx[0]][['POLYGON_ID', 'POLYGON_STR', 'HOFN_TYPE', 'ROAD_LEVEL']].reset_index(drop=True)
        assert len(geom6_result)==len(Tcells_result)
        hofn6 = pd.concat([Tcells_result, geom6_result], axis=1)
        
        if (len(hofn6)==0):
            return hofn6
        else:
            hofn6['POS_TYPE'] = 7
            hofn6['POS_INDOOR_TYPE'] = 1
            hofn6['DIST_MAX'] = 0
            hofn6['DIST_MIN'] = 0
            hofn6 = hofn6[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL']]
            hofn6['POLYGON_STR'] = ''
            hofn6 = hofn6.drop_duplicates(keep='first')
            return hofn6
    except Exception as e:
        logging.error(e,exc_info=True)

def Poly7(dfcircles,geom7,tech):
    try:
        # logging.info(f'\tPoly7 process started (task pid:{os.getpid()})')
        region, site= region_dict[tech], site_dict[tech]
        if len(dfcircles)==0:
            return gpd.GeoDataFrame(None)
        geom7_geoseries     = gpd.GeoSeries(geom7.geometry)
        dfcircles_geoseries = gpd.GeoSeries(dfcircles.geometry)
        sidx = dfcircles_geoseries.sindex.query_bulk(geom7_geoseries, predicate="intersects")
        dfcircles_result    = dfcircles.loc[sidx[1]][[region, site, 'CELL_ID']].reset_index(drop=True)
        geom7_result        = geom7.loc[sidx[0]][['POLYGON_ID', 'POLYGON_STR', 'HOFN_TYPE', 'ROAD_LEVEL']].reset_index(drop=True)
        assert len(geom7_result)==len(dfcircles_result)
        hofn7 = pd.concat([dfcircles_result, geom7_result], axis=1)
        
        if (len(hofn7)==0):
            return hofn7
        else:
            hofn7['POS_TYPE'] = 1
            hofn7['POS_INDOOR_TYPE'] = 0
            hofn7['DIST_MAX'] = 0
            hofn7['DIST_MIN'] = 0
            hofn7 = hofn7[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL']]
            hofn7['POLYGON_STR'] = ''
            hofn7 = hofn7.drop_duplicates(keep='first')
            return hofn7
    except Exception as e:
        logging.error(e,exc_info=True)
    
def Poly9(incell,geom9,tech):
    try:
        # logging.info(f'\tPoly9 process started (task pid:{os.getpid()})')
        region, site, sitetype = region_dict[tech], site_dict[tech], type_dict[tech]
        IBcell = incell[incell[sitetype]==6]
        IBcells_extended = IBcell.copy(deep=True)
        IBcells_extended['geometry'] = IBcells_extended['geometry'].buffer(10/3.1415926/6378137*180)
        geom9_geoseries  = gpd.GeoSeries(geom9.geometry)
        IBcell_geoseries = gpd.GeoSeries(IBcells_extended.geometry)
        sidx = IBcell_geoseries.sindex.query_bulk(geom9_geoseries, predicate="intersects")
        IBcell_result   = IBcell.loc[sidx[1]][[region, site, 'CELL_ID']].reset_index(drop=True)
        geom9_result     = geom9.loc[sidx[0]][['POLYGON_ID', 'POLYGON_STR', 'HOFN_TYPE', 'ROAD_LEVEL']].reset_index(drop=True)
        assert len(geom9_result)==len(IBcell_result)
        hofn9 = pd.concat([IBcell_result, geom9_result], axis=1)
    
        if (len(hofn9)==0):
            logging.info(f'\t\tPoly9 process finished (task pid:{os.getpid()}), result lines count:0')
            return hofn9
        else:
            hofn9 = hofn9.reset_index(drop=True)
            hofn9['POS_TYPE'] = 2
            hofn9['POS_INDOOR_TYPE'] = 0
            hofn9['DIST_MAX'] = 0
            hofn9['DIST_MIN'] = 0
            hofn9 = hofn9[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL']]
            hofn9['POLYGON_STR'] = ''
            hofn9 = hofn9.drop_duplicates(keep='first')
            return hofn9
    except Exception as e:
        logging.error(e,exc_info=True)
    
def Poly10(dfcircles,geom10,tech):
    try:
        # logging.info(f'\tPoly1 process started (task pid:{os.getpid()})')
        region, site = region_dict[tech], site_dict[tech]
        if len(dfcircles)==0:
            return gpd.GeoDataFrame(None)
        
        geom10_geoseries    = gpd.GeoSeries(geom10.geometry)
        dfcircles_geoseries = gpd.GeoSeries(dfcircles.geometry)
        sidx = dfcircles_geoseries.sindex.query_bulk(geom10_geoseries, predicate="intersects")
        dfcircles_result    = dfcircles.loc[sidx[1]][[region, site, 'CELL_ID']].reset_index(drop=True)
        geom10_result       = geom10.loc[sidx[0]][['POLYGON_ID', 'POLYGON_STR', 'HOFN_TYPE', 'ROAD_LEVEL']].reset_index(drop=True)
        assert len(geom10_result)==len(dfcircles_result)
        hofn10 = pd.concat([dfcircles_result, geom10_result], axis=1)
        
        if (len(hofn10)==0):
            return hofn10
        else:
            hofn10['POS_TYPE'] = 3
            hofn10['POS_INDOOR_TYPE'] = 0
            hofn10['DIST_MAX'] = 0
            hofn10['DIST_MIN'] = 0
            hofn10 = hofn10[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL']]
            hofn10['POLYGON_STR'] = ''
            hofn10 = hofn10.drop_duplicates(keep='first')
            return hofn10
    except Exception as e:
        logging.error(e,exc_info=True)
    
def Poly10_line(dfcircles,geom10,tech):
    try:
        # logging.info(f'\tPoly1 process started (task pid:{os.getpid()})')
        region, site = region_dict[tech], site_dict[tech]
        if len(dfcircles)==0:
            return gpd.GeoDataFrame(None)
        
        dfcircles_extended = dfcircles.copy(deep=True)
        dfcircles_extended['geometry'] = dfcircles_extended['geometry'].buffer(30000/3.1415926/6378137*180)
        geom10_geoseries    = gpd.GeoSeries(geom10.geometry)
        dfcircles_geoseries = gpd.GeoSeries(dfcircles_extended.geometry)
        sidx = dfcircles_geoseries.sindex.query_bulk(geom10_geoseries, predicate="intersects")
        dfcircles_result    = dfcircles.loc[sidx[1]][[region, site, 'CELL_ID']].reset_index(drop=True)
        geom10_result       = geom10.loc[sidx[0]][['POLYGON_ID', 'POLYGON_STR', 'HOFN_TYPE', 'ROAD_LEVEL']].reset_index(drop=True)
        assert len(geom10_result)==len(dfcircles_result)
        hofn10 = pd.concat([dfcircles_result, geom10_result], axis=1)
        
        if (len(hofn10)==0):
            return hofn10
        else:
            hofn10 = hofn10.reset_index(drop=True)
            hofn10['POS_TYPE'] = 1
            hofn10['POS_INDOOR_TYPE'] = 0
            hofn10['DIST_MAX'] = 0
            hofn10['DIST_MIN'] = 0
            hofn10 = hofn10[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL']]
            hofn10['POLYGON_STR'] = ''
            hofn10 = hofn10.drop_duplicates(keep='first')
            return hofn10
    except Exception as e:
        logging.error(e,exc_info=True)
    
def Poly11(dfcircles,geom11,tech):
    try:
        # logging.info(f'\tPoly11 process started (task pid:{os.getpid()})')
        region, site = region_dict[tech], site_dict[tech]
        dfcircles_rural = dfcircles.copy(deep=True)
        dfcircles_rural = dfcircles_rural[dfcircles_rural['SITE_DENSITY_TYPE'].isin([4,5])].reset_index(drop=True)
        if len(dfcircles_rural)==0:
            return gpd.GeoDataFrame(None)
        
        geom11_geoseries     = gpd.GeoSeries(geom11.geometry)
        dfcircles_geoseries  = gpd.GeoSeries(dfcircles_rural.geometry)
        sidx = dfcircles_geoseries.sindex.query_bulk(geom11_geoseries, predicate="intersects")
        dfcircles_result     = dfcircles_rural.loc[sidx[1]][[region, site, 'CELL_ID', 'LOCATION', 'PATHLOSS_DISTANCE']].reset_index(drop=True)
        geom11_result        = geom11.loc[sidx[0]][['POLYGON_ID', 'POLYGON_STR', 'HOFN_TYPE', 'ROAD_LEVEL']].reset_index(drop=True)
        assert len(geom11_result)==len(dfcircles_result)
        hofn11 = pd.concat([dfcircles_result, geom11_result], axis=1)
        
        if (len(hofn11)==0):
            return hofn11
        else:
            hofn11 = hofn11.reset_index(drop=True)
            hofn11['POS_TYPE'] = 2
            hofn11['POS_INDOOR_TYPE'] = 0
            
            def find_max_dist(point_str, polygon_str):
                geod = pyproj.Geod(ellps='WGS84')
                point = wkt.loads(point_str)
                point_lon = list(point.coords)[0][0]
                point_lat = list(point.coords)[0][1]
                polygon = wkt.loads(polygon_str)
                polygon_coords = list(polygon.exterior.coords)
                dist = [ geod.inv(point_lon, point_lat, x[0], x[1])[2] for x in polygon_coords]
                max_dist = max(dist) + 1000
                max_dist = round(max_dist, 2)
                return max_dist
            
            def find_min_dist(point_str, polygon_str):
                geod = pyproj.Geod(ellps='WGS84')
                point = wkt.loads(point_str)
                point_lon = list(point.coords)[0][0]
                point_lat = list(point.coords)[0][1]
                polygon = wkt.loads(polygon_str)
                nearest_point = nearest_points(point, polygon)[1]
                nearest_point_lon = list(nearest_point.coords)[0][0]
                nearest_point_lat = list(nearest_point.coords)[0][1]
                min_dist = geod.inv(point_lon, point_lat, nearest_point_lon, nearest_point_lat)[2]
                min_dist = round(min_dist, 2)
                return min_dist
            
            hofn11 = hofn11.assign(DIST_MIN =lambda x: list(map(find_min_dist,x['LOCATION'].astype(str), x['POLYGON_STR'].astype(str))))
            hofn11 = hofn11[hofn11.apply(lambda x: x.DIST_MIN>max(1000,x.PATHLOSS_DISTANCE), axis=1)]
            if (len(hofn11)==0):
                return hofn11
            hofn11 = hofn11.assign(DIST_MAX =lambda x: list(map(find_max_dist,x['LOCATION'].astype(str), x['POLYGON_STR'].astype(str))))
            hofn11 = hofn11[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL']]
            hofn11['POLYGON_STR'] = ''
            hofn11 = hofn11.drop_duplicates(keep='first')
            return hofn11
    except Exception as e:
        logging.error(e,exc_info=True)

def Poly14(dfcircles,geom14,tech):
    try:
        # logging.info(f'\tPoly14 process started (task pid:{os.getpid()})')
        region, site = region_dict[tech], site_dict[tech]
        if len(dfcircles)==0:
            return gpd.GeoDataFrame(None)
    
        geom14_geoseries     = gpd.GeoSeries(geom14.geometry)
        dfcircles_geoseries  = gpd.GeoSeries(dfcircles.geometry)
        sidx = dfcircles_geoseries.sindex.query_bulk(geom14_geoseries, predicate="intersects")
        dfcircles_result     = dfcircles.loc[sidx[1]][[region, site, 'CELL_ID']].reset_index(drop=True)
        geom14_result        = geom14.loc[sidx[0]][['POLYGON_ID', 'POLYGON_STR', 'HOFN_TYPE', 'ROAD_LEVEL']].reset_index(drop=True)
        assert len(geom14_result)==len(dfcircles_result)
        hofn14 = pd.concat([dfcircles_result, geom14_result], axis=1)
    
        if (len(hofn14)==0):
            return hofn14
        else:
            hofn14['POS_TYPE'] = 1
            hofn14['POS_INDOOR_TYPE'] = 0
            hofn14['DIST_MAX'] = 0
            hofn14['DIST_MIN'] = 0
            hofn14 = hofn14[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL']]
            hofn14['POLYGON_STR'] = ''
            hofn14 = hofn14.drop_duplicates(keep='first')
            return hofn14
    except Exception as e:
        logging.error(e,exc_info=True)
    
def Poly15(dfcircles,geom15,tech):
    try:
        region, site = region_dict[tech], site_dict[tech]
        if len(dfcircles)==0:
            return gpd.GeoDataFrame(None)
    
        geom15_geoseries     = gpd.GeoSeries(geom15.geometry)
        dfcircles_geoseries  = gpd.GeoSeries(dfcircles.geometry)
        sidx = dfcircles_geoseries.sindex.query_bulk(geom15_geoseries, predicate="intersects")
        dfcircles_result     = dfcircles.loc[sidx[1]][[region, site, 'CELL_ID']].reset_index(drop=True)
        geom15_result        = geom15.loc[sidx[0]][['POLYGON_ID', 'POLYGON_STR', 'HOFN_TYPE', 'ROAD_LEVEL']].reset_index(drop=True)
        assert len(geom15_result)==len(dfcircles_result)
        hofn15 = pd.concat([dfcircles_result, geom15_result], axis=1)
    
        if (len(hofn15)==0):
            return hofn15
        else:
            hofn15['POS_TYPE'] = 3
            hofn15['POS_INDOOR_TYPE'] = 0
            hofn15['DIST_MAX'] = 0
            hofn15['DIST_MIN'] = 0
            hofn15 = hofn15[[region, site, 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL']]
            hofn15['POLYGON_STR'] = ''
            hofn15 = hofn15.drop_duplicates(keep='first')
            return hofn15
    except Exception as e:
        logging.error(e,exc_info=True)