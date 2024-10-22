# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 16:15:55 2020

@author: sheldon
"""

import os
import sys
version = 39.1
if (len(sys.argv)==2):
    if (sys.argv[1]=='-v'):
        print(f'Hofn Version: {version}')
        exit(0)
    elif (sys.argv[1]=='-h'):
        print(f'Hofn Version: {version}, Needs Parameters: input filepath (Hilo output), output file path (Hofn)')
        exit(0)
else:
    pass

################################################################################################################################
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning)
warnings.filterwarnings(action='ignore', category=FutureWarning)
warnings.filterwarnings('error', r'SettingWithCopyWarning')
import configparser
import numpy as np
import pandas as pd
import time
date = [int(x) for x in sys.argv[1].split('/') if ((x.startswith('20')) & (len(x)==8))]
date = date[0] if len(date)==1 else 'hofn'
from file_IO import *
from poly_process_cell import *
config = configparser.ConfigParser()
config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini')
config.read(config_file)
debug_mode = config['DEFAULT'].getboolean('DebugMode')
gen_pu_building = False if config['DEFAULT'].getboolean('gen_PU_Building')==None else config['DEFAULT'].getboolean('gen_PU_Building')
ship_route_line = False if config['DEFAULT'].getboolean('ship_route_line')==None else config['DEFAULT'].getboolean('ship_route_line')
GEO_path = config['PATH']['GEO_path']
log_path = config['PATH']['log_path']
import logging
logging.basicConfig(level=logging.INFO,
                    format = '%(asctime)s [%(levelname)s] %(message)s',
                    datefmt = '%Y-%m-%d %H:%M:%S',
                    handlers = [logging.FileHandler(f'{log_path}{date}.log', 'a', 'utf-8'), logging.StreamHandler()])

# processes = int(np.where(mp.cpu_count()>25, 25, mp.cpu_count()-1))

class bcolors: #ANSI escape sequences
    BOLD = '\033[1m'
    BrightCyan = '\033[96m'
    Cyan = '\033[36m'
    Green = '\033[32m'
    Blue = '\033[34m'
    END = '\033[0m'

def Hofn_Cellbased():
    logging.info(f"{bcolors.BOLD}{bcolors.Green}A new task has been detected, Hofn will generate the relation between Cell coverage & geometries.{bcolors.END}")
    
    ### NT2_GEO_POLYGON data ready
    OSM_path = f'{GEO_path}NT2_GEO_POLYGON.tsv'
    gdf_geom = loadOSMfile(OSM_path)
    if (gdf_geom.empty):
        logging.error('No geometry data detected, Hofn task will be canceled')
        sys.exit(1)
    
    for tech in ['NR','LTE','UMTS','GSM']:
        if config['DEFAULT'].getboolean(f'{tech}process')==True:
            logging.info(f"{bcolors.BOLD}{tech} program start! Let's go bae!{bcolors.END}")
            NTcell_path = f'{sys.argv[1]}'
            
        ### show output_mode status
            output_mode = 1 if config['DEFAULT'].getint(f'{tech}output')==None else config['DEFAULT'].getint(f'{tech}output')
            
            output_mode_dict = {1:'undisplay', 2:'remove'}
            logging.info(f"POLYGON_STR column: {output_mode_dict[output_mode]}")
            logging.info("---")
            
        ### cells data ready
            cell = HOFN_CELL_INFO(NTcell_path, tech)
            if (cell.empty):
                logging.warning(f'HOFN_CELL_INFO_{tech} is empty, Hofn task will be canceled')
                sys.exit(1)
            logging.info("---")
            
        ### define outdoor cells coverage
            gdf_coverage = outcell_process(cell, tech)
            if (gdf_coverage.empty):
                continue
            logging.info("---")
            
        ### define indoor cells & special type cells location
            gdf_inpos, gdf_MRT_pos, gdf_tunnel_pos, gdf_IB_pos = indoor_and_special_cell_process(cell, tech)
            logging.info("---")
            
        ### set NT2_CELL_POLYGON header
            set_Hofn_title_cell(tech)
                
        ### Hofn process for geodata without roads
            def Hofn_process(gdf_geom, gdf_coverage, gdf_inpos, gdf_MRT_pos, gdf_tunnel_pos, gdf_IB_pos):
                hofn_project = np.unique(gdf_geom['HOFN_TYPE'])
                logging.info('Hofn module process starting')
                for hofn in hofn_project:
                    geom = gdf_geom[gdf_geom['HOFN_TYPE']==hofn].reset_index(drop=True)
                    if (hofn == 1):
                        result = Poly1(gdf_coverage,geom,tech)
                    elif (hofn == 2):
                        result = Poly2(gdf_coverage,geom,tech)
                    elif (hofn == 3):
                        result = Poly3(gdf_MRT_pos,geom,tech)
                    elif (hofn == 5):
                        result = Poly5(gdf_coverage,geom,tech)
                    elif (hofn == 6):
                        if (len(gdf_tunnel_pos)!=0):
                            result = Poly6(gdf_tunnel_pos,geom,tech)
                        else:
                            result = Poly6(gdf_inpos,geom,tech)
                    elif (hofn == 7):
                        result = Poly7(gdf_coverage,geom,tech)
                    elif (hofn == 10):
                        if ship_route_line:
                            if not all(geom['POLYGON_STR'].str.startswith('LINESTRING')):
                                raise Exception('only support LineString grom type for ship route with enabling ship_route_line')
                            result = Poly10_line(gdf_coverage,geom,tech)
                        else:
                            if not all(geom['POLYGON_STR'].str.startswith('POLYGON')):
                                raise Exception('only support Polygon grom type for ship route with disabling ship_route_line')
                            result = Poly10(gdf_coverage,geom,tech)
                    elif (hofn == 11):
                        result = Poly11(gdf_coverage,geom,tech)
                    elif (hofn == 14):
                        result = Poly14(gdf_coverage,geom,tech)
                    elif (hofn == 15):
                        result = Poly15(gdf_coverage,geom,tech)
                    line_num = len(result)
                    logging.info(f'\t{tech} HOFN_{hofn} process finished! result lines count: {line_num}')
                    result.to_csv(f'{sys.argv[2]}NT2_CELL_POLYGON_{tech}.tsv',mode='a',header=False,sep='\t',index=False)
            
        ### run Hofn process
            Hofn_process(gdf_geom, gdf_coverage, gdf_inpos, gdf_MRT_pos, gdf_tunnel_pos, gdf_IB_pos)
            if ship_route_line:
                remove_ship_route_without_coastline(tech)
            logging.info(f'NT2_CELL_POLYGON_{tech}.tsv data output has finished\n')
        else:
            continue
    
def PU_Building():
    import shutil
    from shapely import wkt
    import geopandas as gpd
    
    logging.info(f"{bcolors.BOLD}{bcolors.Green}A new task has been detected, Hofn will generate the relation between PU polygon & buildings (tile based).{bcolors.END}")
    NTcell_path = f'{sys.argv[1]}'
    if os.path.isdir(f'{sys.argv[2]}pu_building'):
        shutil.rmtree(f'{sys.argv[2]}pu_building')
    os.mkdir(f'{sys.argv[2]}pu_building')
    
    with open(f'{GEO_path}all_buildings.tsv', 'rb') as f:
        num_lines = sum(1 for _ in f)-1
    logging.info(f"all_buildings tile number: {num_lines}")
    
    for tech in ['NR','LTE']:
        if config['DEFAULT'].getboolean(f'{tech}process')==True:
            pu_df = pd.read_csv(f'{NTcell_path}/NT2_PU_POLYGON_{tech}.tsv',sep='\t')
            pu_df['geometry'] = pu_df['POLYGON_STR'].apply(wkt.loads)
            logging.info(f"{tech} pu number: {len(pu_df)}")
            pu_geoseries = gpd.GeoSeries(pu_df['geometry'])
            pu_index_mapping = { i:pu for i, pu in zip(pu_df.index, pu_df.PU_ID) }
            
            task_split_num = 20
            process_ranges = np.array_split(range(num_lines), task_split_num)
            percentage_switch = False
            sentinel_count = 0
            for process_range in process_ranges:
                m = buildings_processing(process_range, pu_geoseries)
                for i, df in m.items():
                    puid = pu_index_mapping[i]
                    file_path = f'{sys.argv[2]}pu_building/NT2_{puid}_Building_{tech}.tsv'
                    if not os.path.exists(file_path):
                        pd.DataFrame(columns=['tile_ID','lon','lat']).to_csv(file_path, sep='\t', index=False, line_terminator='\n')
                    df.to_csv(file_path, mode='a', header=False, sep='\t', index=False, line_terminator='\n')
                sentinel_count += 1
                if (sentinel_count/task_split_num)==1 and percentage_switch:
                    logging.info('\t100% task completed')
                    break # we are done
                elif 1>(sentinel_count/task_split_num)>=0.75 and not percentage_switch:
                    logging.info('\t75% task completed')
                    percentage_switch = True
                elif 0.75>(sentinel_count/task_split_num)>=0.50 and percentage_switch:
                    logging.info('\t50% task completed')
                    percentage_switch = False
                elif 0.50>(sentinel_count/task_split_num)>=0.25 and not percentage_switch:
                    logging.info('\t25% task completed')
                    percentage_switch = True
            pu_used = sum(1 for x in os.listdir(f'{sys.argv[2]}pu_building') if tech in x)
            logging.info(f'{tech} PU_Building data output has finished, file number: {pu_used}\n')
    
def main():
    logging.info(f"{bcolors.BOLD}{bcolors.BrightCyan}Hi, I'm Hofn v{version}. Now time is {time.ctime(time.time())}. Glad to be at your service{bcolors.END}")
    time.sleep(1)
    start = time.time()
    # logging.info(f'Your device has {mp.cpu_count()} cores, multiprocessing will use {processes} cores\n')
    try:
        Hofn_Cellbased()
        if gen_pu_building:
            PU_Building()
    except Exception as e:
        logging.error(e, exc_info=True)
        sys.exit(1)
    modify_log(f'{log_path}{date}.log')
    end = time.time()
    logging.info(f'Run time: {(end-start):4.3f}s')
    
if __name__ == "__main__":
    main()