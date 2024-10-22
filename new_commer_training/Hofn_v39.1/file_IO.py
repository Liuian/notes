# -*- coding: utf-8 -*-
"""
Created on Wed Sep  2 23:41:30 2020

@author: sheldon
"""

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point
from shapely import wkt
import time
import math
import os
from pygc import great_circle
from Hofn import date
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning)
warnings.filterwarnings(action='ignore', category=FutureWarning)
warnings.filterwarnings('error', r'SettingWithCopyWarning')
import configparser
config = configparser.ConfigParser()
config_file = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.ini')
config.read(config_file)
debug_mode = config['DEFAULT'].getboolean('DebugMode')
GEO_path = config['PATH']['GEO_path']
log_path = config['PATH']['log_path']
import sys
import logging
logging.basicConfig(level=logging.INFO,
                    format = '%(asctime)s [%(levelname)s] %(message)s',
                    datefmt = '%Y-%m-%d %H:%M:%S',
                    handlers = [logging.FileHandler(f'{log_path}{date}.log', 'a', 'utf-8'), logging.StreamHandler()])

mcc = {202:'Greece',204:'Netherlands',206:'Belgium',208:'France',212:'Monaco',213:'Andorra',214:'Spain',216:'Hungary',218:'Bosnia and Herzegov',219:'Croatia',220:'Serbia',222:'Italy',226:'Romania',228:'Switzerland',230:'Czech Republic',231:'Slovakia',232:'Austria',234:'United Kingdom',235:'United Kingdom',238:'Denmark',240:'Sweden',242:'Norway',244:'Finland',246:'Lithuania',247:'Latvia',248:'Estonia',250:'Russian Federation',255:'Ukraine',257:'Belarus',259:'Moldova',260:'Poland',262:'Germany',266:'Gibraltar',268:'Portugal',270:'Luxembourg',272:'Ireland',274:'Iceland',276:'Albania',278:'Malta',280:'Cyprus',282:'Georgia',283:'Armenia',284:'Bulgaria',286:'Turkey',288:'Faroe Islands',289:'Abkhazia',290:'Greenland',292:'San Marino',294:'Macedonia',295:'Liechtenstein',297:'Montenegro',302:'Canada',308:'St. Pierre and Miquelon',310:'United States',311:'United States',312:'United States',313:'United States',316:'United States',330:'Puerto Rico',334:'Mexico',338:'Jamaica',340:'French Guiana',342:'Barbados',344:'Antigua and Barbuda',346:'Cayman Islands',348:'British Virgin Islands',350:'Bermuda',352:'Grenada',354:'Montserrat',356:'Saint Kitts and Nevis',358:'Saint Lucia',360:'Saint Vincent and the Grenadines',362:'Curacao',363:'Aruba',364:'Bahamas',365:'Anguilla',366:'Dominica',368:'Cuba',370:'Dominican Republic',372:'Haiti',374:'Trinidad and Tobago',376:'Turks and Caicos Islands',400:'Azerbaijan',401:'Kazakhstan',402:'Bhutan',404:'India',405:'India',410:'Pakistan',412:'Afghanistan',413:'Sri Lanka',414:'Myanmar (Burma)',415:'Lebanon',416:'Jordan',417:'Syrian Arab Republic',418:'Iraq',419:'Kuwait',420:'Saudi Arabia',421:'Yemen',422:'Oman',424:'United Arab Emirates',425:'Israel',426:'Bahrain',427:'Qatar',428:'Mongolia',429:'Nepal',430:'United Arab Emirates',431:'United Arab Emirates',432:'Iran',434:'Uzbekistan',436:'Tajikistan',437:'Kyrgyzstan',438:'Turkmenistan',440:'Japan',441:'Japan',450:'Korea South',452:'Viet Nam',454:'Hongkong',455:'Macao',456:'Cambodia',457:'Laos',460:'China',466:'Taiwan',467:'Korea North',470:'Bangladesh',472:'Maldives',502:'Malaysia',505:'Australia',510:'Indonesia',514:'Timor-Leste',515:'Philippines',520:'Thailand',525:'Singapore',528:'Brunei Darussalam',530:'New Zealand',537:'Papua New Guinea',539:'Tonga',540:'Solomon Islands',541:'Vanuatu',542:'Fiji',544:'American Samoa',545:'Kiribati',546:'New Caledonia',547:'French Polynesia',548:'Cook Islands',549:'Samoa',550:'Micronesia',552:'Palau Republic',553:'Tuvalu',555:'Niue',602:'Egypt',603:'Algeria',604:'Morocco',605:'Tunisia',606:'Libya',607:'Gambia',608:'Senegal',609:'Mauritania',610:'Mali',611:'Guinea',612:'Ivory Coast',613:'Burkina Faso',614:'Niger',615:'Togo',616:'Benin',617:'Mauritius',618:'Liberia',619:'Sierra Leone',620:'Ghana',621:'Nigeria',622:'Chad',623:'Central African Republic',624:'Cameroon',625:'Cape Verde',626:'Sao Tome and Principe',627:'Equatorial Guinea',628:'Gabon',629:'Congo Republic',630:'Congo Democratic Republic',631:'Angola',632:'Guinea Bissau',633:'Seychelles',634:'Sudan',635:'Rwanda',636:'Ethiopia',637:'Somalia',638:'Djibouti',639:'Kenya',640:'Tanzania',641:'Uganda',642:'Burundi',643:'Mozambique',645:'Zambia',646:'Madagascar',647:'Reunion',648:'Zimbabwe',649:'Namibia',650:'Malawi',651:'Lesotho',652:'Botswana',653:'Swaziland',654:'Comoros',655:'South Africa',657:'Eritrea',659:'South Sudan Republic ',702:'Belize',704:'Guatemala',706:'El Salvador',708:'Honduras',710:'Nicaragua',712:'Costa Rica',714:'Panama',716:'Peru',722:'Argentina Republic',724:'Brazil',730:'Chile',732:'Colombia',734:'Venezuela',736:'Bolivia',738:'Guyana',740:'Ecuador',744:'Paraguay',746:'Suriname',748:'Uruguay',750:'Falkland Islands (Malvinas)',901:'International Networks'}
    
class bcolors: #ANSI escape sequences
    BrightRed = '\033[91m'
    END = '\033[0m'
    
region_dict = {'NR':'PU_ID', 'LTE':'PU_ID', 'UMTS':'RNC_ID', 'GSM':'BSC_ID'}
site_dict = {'NR':'GNODEB_ID', 'LTE':'ENODEB_ID', 'UMTS':'SITE_ID', 'GSM':'LAC'}
type_dict = {'NR':'GNODEB_TYPE', 'LTE':'ENODEB_TYPE', 'UMTS':'SITE_TYPE', 'GSM':'BTS_TYPE'}

def HOFN_CELL_INFO(NTcell_path, tech):
    
    def cell_info_decorator(func):
        def wrapper(NTcell_path):
            tech = (func.__name__).split('_')[0]
            start = time.time()
            logging.info(f'HOFN_CELL_INFO_{tech} process starting')
            cell = func(NTcell_path)
            cell.to_csv(f'{sys.argv[2]}HOFN_CELL_INFO_{tech}.csv', index=False)
            
            cell = pd.concat( [
            cell.select_dtypes( include=['object'] ),
            cell.select_dtypes( include=['integer'] ).apply( pd.to_numeric, downcast='signed' ),
            cell.select_dtypes( include=['float'] ).apply( pd.to_numeric, downcast='float' ),
            ], 
            axis=1
            )
            cell['LOCATION'] = [ Point(xy).wkt for xy in zip(cell.LONGITUDE, cell.LATITUDE) ]
        
            end = time.time()
            runtime = end-start
            logging.info(f'HOFN_CELL_INFO_{tech}.csv file has been generated, run time: {runtime:4.3f}s, total cells number : {len(cell)}')
            return cell
        return wrapper
    
    @cell_info_decorator
    def NR_cell_info_maker(NTcell_path):
        cell_header = ['PU_ID', 'GNODEB_ID', 'CELL_ID', 'INDOOR', 'GNODEB_TYPE', 'NBR_DISTANCE_VORONOI', 'SERVING_TYPE', 'SITE_DENSITY_TYPE']
        if os.path.isfile(f'{NTcell_path}/NT2_CELL_NR.csv'):
            nt2cell = pd.read_csv(f'{NTcell_path}/NT2_CELL_NR.csv', engine='python', usecols=cell_header)
        else:
            logging.error("NT2_CELL_NR file does not exist. Please check that!\n")
            sys.exit(1)

        antenna_header = ['PU_ID', 'GNODEB_ID', 'CELL_ID', 'ANTENNA_ID', 'LONGITUDE', 'LATITUDE', 'AZIMUTH', 'BEAMWIDTH_H', 'PATHLOSS_DISTANCE']
        if os.path.isfile(f'{NTcell_path}/NT2_ANTENNA_NR.csv'):
            nt2antenna = pd.read_csv(f'{NTcell_path}/NT2_ANTENNA_NR.csv', engine='python', usecols=antenna_header)
        else:
            logging.error("NT2_ANTENNA_NR file does not exist. Please check that!\n")
            sys.exit(1)

        nbr_header = ['GNODEB_ID', 'CELL_ID', 'NBR_GNODEB_ID', 'REFINE_DISTANCE']
        if os.path.isfile(f'{NTcell_path}/NT2_NBR_VORONOI_LOC_NR.csv'):
            nt2nbr = pd.read_csv(f'{NTcell_path}/NT2_NBR_VORONOI_LOC_NR.csv', low_memory=False, encoding='utf-8', usecols=nbr_header)
            nt2nbr = nt2nbr.drop_duplicates()
        elif os.path.isfile(f'{NTcell_path}/NT2_NBR_VORONOI_CELL_NR.csv'):
            nt2nbr = pd.read_csv(f'{NTcell_path}/NT2_NBR_VORONOI_CELL_NR.csv', low_memory=False, encoding='utf-8', usecols=nbr_header)
            nt2nbr = nt2nbr.drop_duplicates()
        else:
            logging.error("NT2_NBR_VORONOI_LOC_NR(or NT2_NBR_VORONOI_CELL_NR) file does not exist. Please check that!\n")
            sys.exit(1)
        
        data = pd.merge(nt2cell, nt2antenna, how='inner', on=['PU_ID','GNODEB_ID','CELL_ID'])
        nbr_tier1 = nt2nbr.groupby(by=['GNODEB_ID','CELL_ID'], as_index=False).agg({'REFINE_DISTANCE':'max'})
        nbr_tier2 = nt2nbr.merge(nbr_tier1, how='outer', left_on='NBR_GNODEB_ID', right_on='GNODEB_ID')
        # nbr_tier2 = nt2nbr.merge(nt2nbr, how='outer', left_on='NBR_ENODEB_ID', right_on='ENODEB_ID')
        nbr_tier2 = nbr_tier2[['GNODEB_ID_x','CELL_ID_x','REFINE_DISTANCE_x','REFINE_DISTANCE_y']].reset_index(drop=True)
        nbr_tier2 = nbr_tier2[~(nbr_tier2['GNODEB_ID_x'].isnull()) & (nbr_tier2['GNODEB_ID_x']!='\\N')]
        nbr_tier2 = nbr_tier2[~(nbr_tier2['CELL_ID_x'].isnull()) & (nbr_tier2['CELL_ID_x']!='\\N')]
        nbr_tier2['REFINE_DISTANCE_y'] = nbr_tier2['REFINE_DISTANCE_y'].fillna(method='ffill', downcast='infer')
        nbr_tier2['GNODEB_ID_x'] = nbr_tier2['GNODEB_ID_x'].astype(np.int64)
        nbr_tier2['CELL_ID_x'] = nbr_tier2['CELL_ID_x'].astype(int)
        nbr_tier2['FINAL_DISTANCE'] = nbr_tier2['REFINE_DISTANCE_x'] + nbr_tier2['REFINE_DISTANCE_y']
        nbr_max = nbr_tier2.groupby(by=['GNODEB_ID_x','CELL_ID_x'], as_index=False).agg({'FINAL_DISTANCE':'max'})
        nbr_max = nbr_max.rename(columns={'GNODEB_ID_x':'GNODEB_ID', 'CELL_ID_x':'CELL_ID'})
        cell = pd.merge(data, nbr_max, how='left',on=['GNODEB_ID','CELL_ID'])
        cell = cell.fillna(0)
        
        ### Reduce memory usage
        
        cell['PU_ID'] = cell['PU_ID'].astype(int)
        cell['ANTENNA_ID'] = cell['ANTENNA_ID'].astype(int)
        cell['AZIMUTH'] = cell['AZIMUTH'].astype(int)
        cell['INDOOR'] = cell['INDOOR'].astype(int)
        cell['GNODEB_TYPE'] = cell['GNODEB_TYPE'].astype(int)
        cell['SERVING_TYPE'] = cell['SERVING_TYPE'].astype(int)
        cell['BEAMWIDTH_H'] = cell['BEAMWIDTH_H'].astype(int)
        
        return cell
    
    @cell_info_decorator
    def LTE_cell_info_maker(NTcell_path):
        cell_header = ['PU_ID', 'ENODEB_ID', 'CELL_ID', 'INDOOR', 'ENODEB_TYPE', 'NBR_DISTANCE_VORONOI', 'SERVING_TYPE', 'SITE_DENSITY_TYPE']
        if os.path.isfile(f'{NTcell_path}/NT2_CELL_LTE.csv'):
            nt2cell = pd.read_csv(f'{NTcell_path}/NT2_CELL_LTE.csv', engine='python', usecols=cell_header)
        else:
            logging.error("NT2_CELL_LTE file does not exist. Please check that!\n")
            sys.exit(1)

        antenna_header = ['PU_ID', 'ENODEB_ID', 'CELL_ID', 'ANTENNA_ID', 'LONGITUDE', 'LATITUDE', 'AZIMUTH', 'BEAMWIDTH_H', 'PATHLOSS_DISTANCE']
        if os.path.isfile(f'{NTcell_path}/NT2_ANTENNA_LTE.csv'):
            nt2antenna = pd.read_csv(f'{NTcell_path}/NT2_ANTENNA_LTE.csv', engine='python', usecols=antenna_header)
        else:
            logging.error("NT2_ANTENNA_LTE file does not exist. Please check that!\n")
            sys.exit(1)

        nbr_header = ['ENODEB_ID', 'CELL_ID', 'NBR_ENODEB_ID', 'REFINE_DISTANCE']
        if os.path.isfile(f'{NTcell_path}/NT2_NBR_VORONOI_LOC_LTE.csv'):
            nt2nbr = pd.read_csv(f'{NTcell_path}/NT2_NBR_VORONOI_LOC_LTE.csv', low_memory=False, encoding='utf-8', usecols=nbr_header)
            nt2nbr = nt2nbr.drop_duplicates()
        elif os.path.isfile(f'{NTcell_path}/NT2_NBR_VORONOI_CELL_LTE.csv'):
            nt2nbr = pd.read_csv(f'{NTcell_path}/NT2_NBR_VORONOI_CELL_LTE.csv', low_memory=False, encoding='utf-8', usecols=nbr_header)
            nt2nbr = nt2nbr.drop_duplicates()
        else:
            logging.error("NT2_NBR_VORONOI_LOC_LTE(or NT2_NBR_VORONOI_CELL_LTE) file does not exist. Please check that!\n")
            sys.exit(1)
        
        data = pd.merge(nt2cell, nt2antenna, how='inner', on=['PU_ID','ENODEB_ID','CELL_ID'])
        nbr_tier1 = nt2nbr.groupby(by=['ENODEB_ID','CELL_ID'], as_index=False).agg({'REFINE_DISTANCE':'max'})
        nbr_tier2 = nt2nbr.merge(nbr_tier1, how='outer', left_on='NBR_ENODEB_ID', right_on='ENODEB_ID')
        # nbr_tier2 = nt2nbr.merge(nt2nbr, how='outer', left_on='NBR_ENODEB_ID', right_on='ENODEB_ID')
        nbr_tier2 = nbr_tier2[['ENODEB_ID_x','CELL_ID_x','REFINE_DISTANCE_x','REFINE_DISTANCE_y']].reset_index(drop=True)
        nbr_tier2 = nbr_tier2[~(nbr_tier2['ENODEB_ID_x'].isnull()) & (nbr_tier2['ENODEB_ID_x']!='\\N')]
        nbr_tier2 = nbr_tier2[~(nbr_tier2['CELL_ID_x'].isnull()) & (nbr_tier2['CELL_ID_x']!='\\N')]
        nbr_tier2['REFINE_DISTANCE_y'] = nbr_tier2['REFINE_DISTANCE_y'].fillna(method='ffill', downcast='infer')
        nbr_tier2['ENODEB_ID_x'] = nbr_tier2['ENODEB_ID_x'].astype(np.int64)
        nbr_tier2['CELL_ID_x'] = nbr_tier2['CELL_ID_x'].astype(int)
        nbr_tier2['FINAL_DISTANCE'] = nbr_tier2['REFINE_DISTANCE_x'] + nbr_tier2['REFINE_DISTANCE_y']
        nbr_max = nbr_tier2.groupby(by=['ENODEB_ID_x','CELL_ID_x'], as_index=False).agg({'FINAL_DISTANCE':'max'})
        nbr_max = nbr_max.rename(columns={'ENODEB_ID_x':'ENODEB_ID', 'CELL_ID_x':'CELL_ID'})
        cell = pd.merge(data, nbr_max, how='left',on=['ENODEB_ID','CELL_ID'])
        cell = cell.fillna(0)
        
        ### Reduce memory usage
        
        cell['PU_ID'] = cell['PU_ID'].astype(int)
        cell['ANTENNA_ID'] = cell['ANTENNA_ID'].astype(int)
        cell['AZIMUTH'] = cell['AZIMUTH'].astype(int)
        cell['INDOOR'] = cell['INDOOR'].astype(int)
        cell['ENODEB_TYPE'] = cell['ENODEB_TYPE'].astype(int)
        cell['SERVING_TYPE'] = cell['SERVING_TYPE'].astype(int)
        cell['BEAMWIDTH_H'] = cell['BEAMWIDTH_H'].astype(int)
        
        return cell
    
    @cell_info_decorator
    def UMTS_cell_info_maker(NTcell_path):
        cell_header = ['RNC_ID', 'SITE_ID', 'CELL_ID', 'INDOOR', 'SITE_TYPE', 'NBR_DISTANCE_VORONOI', 'SERVING_TYPE', 'SITE_DENSITY_TYPE']
        if os.path.isfile(f'{NTcell_path}/NT2_CELL_UMTS.csv'):
            nt2cell = pd.read_csv(f'{NTcell_path}/NT2_CELL_UMTS.csv', engine='python', usecols=cell_header)
        else:
            logging.error("NT2_CELL_UMTS file does not exist. Please check that!\n")
            sys.exit(1)
    
        antenna_header = ['RNC_ID', 'CELL_ID', 'ANTENNA_ID', 'LONGITUDE', 'LATITUDE', 'AZIMUTH', 'BEAMWIDTH_H', 'PATHLOSS_DISTANCE']
        if os.path.isfile(f'{NTcell_path}/NT2_ANTENNA_UMTS.csv'):
            nt2antenna = pd.read_csv(f'{NTcell_path}/NT2_ANTENNA_UMTS.csv', engine='python', usecols=antenna_header)
        else:
            logging.error("NT2_ANTENNA_UMTS file does not exist. Please check that!\n")
            sys.exit(1)
    
        nbr_header = ['RNC_ID', 'SITE_ID', 'CELL_ID', 'NBR_RNC_ID', 'NBR_SITE_ID', 'REFINE_DISTANCE']
        if os.path.isfile(f'{NTcell_path}/NT2_NBR_VORONOI_LOC_UMTS.csv'):
            nt2nbr = pd.read_csv(f'{NTcell_path}/NT2_NBR_VORONOI_LOC_UMTS.csv', low_memory=False, encoding='utf-8', usecols=nbr_header)
            nt2nbr = nt2nbr.drop_duplicates()
        elif os.path.isfile(f'{NTcell_path}/NT2_NBR_VORONOI_CELL_UMTS.csv'):
            nt2nbr = pd.read_csv(f'{NTcell_path}/NT2_NBR_VORONOI_CELL_UMTS.csv', low_memory=False, encoding='utf-8', usecols=nbr_header)
            nt2nbr = nt2nbr.drop_duplicates()
        else:
            logging.error("NT2_NBR_VORONOI_LOC_UMTS(or NT2_NBR_VORONOI_CELL_UMTS) file does not exist. Please check that!\n")
            sys.exit(1)
        
        data = pd.merge(nt2cell, nt2antenna, how='inner', on=['RNC_ID','CELL_ID'])
        nbr_tier1 = nt2nbr.groupby(by=['RNC_ID','SITE_ID','CELL_ID'], as_index=False).agg({'REFINE_DISTANCE':'max'})
        nbr_tier2 = nt2nbr.merge(nbr_tier1, how='outer', left_on=['NBR_RNC_ID','NBR_SITE_ID'], right_on=['RNC_ID','SITE_ID'])
        # nbr_tier2 = nt2nbr.merge(nt2nbr, how='outer', left_on=['NBR_RNC_ID','NBR_SITE_ID'], right_on=['RNC_ID','SITE_ID'])
        nbr_tier2 = nbr_tier2[['RNC_ID_x','SITE_ID_x','CELL_ID_x','REFINE_DISTANCE_x','REFINE_DISTANCE_y']].reset_index(drop=True)
        nbr_tier2 = nbr_tier2[~(nbr_tier2['RNC_ID_x'].isnull()) & (nbr_tier2['RNC_ID_x']!='\\N')]
        nbr_tier2 = nbr_tier2[~(nbr_tier2['CELL_ID_x'].isnull()) & (nbr_tier2['CELL_ID_x']!='\\N')]
        nbr_tier2['REFINE_DISTANCE_y'] = nbr_tier2['REFINE_DISTANCE_y'].fillna(method='ffill', downcast='infer')
        nbr_tier2['RNC_ID_x'] = nbr_tier2['RNC_ID_x'].astype(int)
        nbr_tier2['CELL_ID_x'] = nbr_tier2['CELL_ID_x'].astype(int)
        nbr_tier2['FINAL_DISTANCE'] = nbr_tier2['REFINE_DISTANCE_x'] + nbr_tier2['REFINE_DISTANCE_y']
        nbr_max = nbr_tier2.groupby(by=['RNC_ID_x','CELL_ID_x'], as_index=False).agg({'FINAL_DISTANCE':'max'})
        nbr_max = nbr_max.rename(columns={'RNC_ID_x':'RNC_ID', 'CELL_ID_x':'CELL_ID'})
        cell = pd.merge(data, nbr_max, how='left',on=['RNC_ID','CELL_ID'])
        cell = cell.fillna(0)
        
        ### Reduce memory usage
        
        cell['RNC_ID'] = cell['RNC_ID'].astype(int)
        try:
            cell['SITE_ID'] = cell['SITE_ID'].astype(int)
        except ValueError:
            pass
        cell['ANTENNA_ID'] = cell['ANTENNA_ID'].astype(int)
        cell['AZIMUTH'] = cell['AZIMUTH'].astype(int)
        cell['INDOOR'] = cell['INDOOR'].astype(int)
        cell['SITE_TYPE'] = cell['SITE_TYPE'].astype(int)
        cell['SERVING_TYPE'] = cell['SERVING_TYPE'].astype(int) 
        cell['BEAMWIDTH_H'] = cell['BEAMWIDTH_H'].astype(int)
        return cell
    
    @cell_info_decorator
    def GSM_cell_info_maker(NTcell_path):
        cell_header = ['BSC_ID', 'LAC', 'CELL_ID', 'INDOOR', 'BTS_TYPE', 'NBR_DISTANCE_VORONOI', 'SERVING_TYPE', 'SITE_DENSITY_TYPE']
        if os.path.isfile(f'{NTcell_path}/NT2_CELL_GSM.csv'):
            nt2cell = pd.read_csv(f'{NTcell_path}/NT2_CELL_GSM.csv', engine='python', usecols=cell_header)
        else:
            logging.error("NT2_CELL_GSM file does not exist. Please check that!\n")
            sys.exit(1)
    
        antenna_header = ['BSC_ID', 'LAC', 'CELL_ID', 'ANTENNA_ID', 'LONGITUDE', 'LATITUDE', 'AZIMUTH', 'BEAMWIDTH_H', 'PATHLOSS_DISTANCE']
        if os.path.isfile(f'{NTcell_path}/NT2_ANTENNA_GSM.csv'):
            nt2antenna = pd.read_csv(f'{NTcell_path}/NT2_ANTENNA_GSM.csv', engine='python', usecols=antenna_header)
        else:
            logging.error("NT2_ANTENNA_GSM file does not exist. Please check that!\n")
            sys.exit(1)
    
        nbr_header = ['BSC_ID', 'LAC', 'SITE_ID', 'CELL_ID', 'NBR_BSC_ID', 'NBR_LAC', 'NBR_SITE_ID', 'REFINE_DISTANCE']
        if os.path.isfile(f'{NTcell_path}/NT2_NBR_VORONOI_LOC_GSM.csv'):
            nt2nbr = pd.read_csv(f'{NTcell_path}/NT2_NBR_VORONOI_LOC_GSM.csv', low_memory=False, encoding='utf-8', usecols=nbr_header)
            nt2nbr = nt2nbr.drop_duplicates()
        elif os.path.isfile(f'{NTcell_path}/NT2_NBR_VORONOI_CELL_GSM.csv'):
            nt2nbr = pd.read_csv(f'{NTcell_path}/NT2_NBR_VORONOI_CELL_GSM.csv', low_memory=False, encoding='utf-8', usecols=nbr_header)
            nt2nbr = nt2nbr.drop_duplicates()
        else:
            logging.error("NT2_NBR_VORONOI_LOC_GSM(or NT2_NBR_VORONOI_CELL_GSM) file does not exist. Please check that!\n")
            sys.exit(1)
        
        data = pd.merge(nt2cell, nt2antenna, how='inner', on=['BSC_ID','LAC','CELL_ID'])
        nbr_tier1 = nt2nbr.groupby(by=['BSC_ID','LAC','SITE_ID','CELL_ID'], as_index=False).agg({'REFINE_DISTANCE':'max'})
        nbr_tier2 = nt2nbr.merge(nbr_tier1, how='outer', left_on=['NBR_BSC_ID','NBR_LAC','NBR_SITE_ID'], right_on=['BSC_ID','LAC','SITE_ID'])
        # nbr_tier2 = nt2nbr.merge(nt2nbr, how='outer', left_on=['NBR_BSC_ID','NBR_LAC','NBR_SITE_ID'], right_on=['BSC_ID','LAC','SITE_ID'])
        nbr_tier2 = nbr_tier2[['BSC_ID_x','LAC_x','SITE_ID_x','CELL_ID_x','REFINE_DISTANCE_x','REFINE_DISTANCE_y']].reset_index(drop=True)
        nbr_tier2 = nbr_tier2[~(nbr_tier2['BSC_ID_x'].isnull()) & (nbr_tier2['BSC_ID_x']!='\\N')]
        nbr_tier2 = nbr_tier2[~(nbr_tier2['LAC_x'].isnull()) & (nbr_tier2['LAC_x']!='\\N')]
        nbr_tier2 = nbr_tier2[~(nbr_tier2['CELL_ID_x'].isnull()) & (nbr_tier2['CELL_ID_x']!='\\N')]
        nbr_tier2['REFINE_DISTANCE_y'] = nbr_tier2['REFINE_DISTANCE_y'].fillna(method='ffill', downcast='infer')
        nbr_tier2['BSC_ID_x'] = nbr_tier2['BSC_ID_x'].astype(np.int64)
        nbr_tier2['LAC_x'] = nbr_tier2['LAC_x'].astype(np.int64)
        nbr_tier2['CELL_ID_x'] = nbr_tier2['CELL_ID_x'].astype(int)
        nbr_tier2['FINAL_DISTANCE'] = nbr_tier2['REFINE_DISTANCE_x'] + nbr_tier2['REFINE_DISTANCE_y']
        nbr_max = nbr_tier2.groupby(by=['BSC_ID_x','LAC_x','CELL_ID_x'], as_index=False).agg({'FINAL_DISTANCE':'max'})
        nbr_max = nbr_max.rename(columns={'BSC_ID_x':'BSC_ID','LAC_x':'LAC', 'CELL_ID_x':'CELL_ID'})
        cell = pd.merge(data, nbr_max, how='left',on=['BSC_ID','LAC','CELL_ID'])
        cell = cell.fillna(0)
        
        ### Reduce memory usage
        
        cell['BSC_ID'] = cell['BSC_ID'].astype(int)
        cell['LAC'] = cell['LAC'].astype(int)
        cell['ANTENNA_ID'] = cell['ANTENNA_ID'].astype(int)
        cell['AZIMUTH'] = cell['AZIMUTH'].astype(int)
        cell['INDOOR'] = cell['INDOOR'].astype(int)
        cell['BTS_TYPE'] = cell['BTS_TYPE'].astype(int)
        cell['SERVING_TYPE'] = cell['SERVING_TYPE'].astype(int)
        cell['BEAMWIDTH_H'] = cell['BEAMWIDTH_H'].astype(int)
        
        return cell
    
    if (tech == 'NR'):
        cell = NR_cell_info_maker(NTcell_path)
    elif (tech == 'LTE'):
        cell = LTE_cell_info_maker(NTcell_path)
    elif (tech == 'UMTS'):
        cell = UMTS_cell_info_maker(NTcell_path)
    elif (tech == 'GSM'):
        cell = GSM_cell_info_maker(NTcell_path)
    
    return cell
    
def outcell_process(cell, tech):
    logging.info('outdoor cells process starting')
    start = time.time()
    region, site = region_dict[tech], site_dict[tech]
    
    ### set condition
    outcell = cell[ (cell["INDOOR"] == 0) ].reset_index(drop=True)
    outcell['FINAL_DISTANCE'] = outcell.apply(lambda x: x['NBR_DISTANCE_VORONOI']*2 if x['FINAL_DISTANCE']==0 else x['FINAL_DISTANCE'], axis=1)
    outcell['FINAL_DISTANCE'] = outcell['FINAL_DISTANCE'].apply(lambda x: 30000 if x>30000 else x) # limit coverage radius not over 30km
    
    ### find the center of circle and draw the coverage
    def movecell(D,a,lat,lon):
        pos = great_circle(distance=D*0.4, azimuth=a, latitude=lat, longitude=lon)
        center = Point(pos['longitude'], pos['latitude'])
        circle = center.buffer(D/math.pi/6378137*180, resolution=4)
        return circle
    outcell = outcell.assign(geometry = lambda x: list(map(movecell, x.FINAL_DISTANCE, x.AZIMUTH, x.LATITUDE, x.LONGITUDE)))
    
    ### establish geodataframe
    boundcircle =  pd.DataFrame(outcell[[f'{region}', f'{site}', 'CELL_ID', 'LOCATION', 'SITE_DENSITY_TYPE', 'PATHLOSS_DISTANCE', 'geometry']])
    gdf_circle = gpd.GeoDataFrame(boundcircle, geometry='geometry', crs=4326)
    # consider multi antenna condition
    d_rows = gdf_circle[gdf_circle.duplicated(subset=[f'{region}', f'{site}', 'CELL_ID'],keep='first')]
    if (len(d_rows)!=0):
        logging.info(f'Multi-antenna condition detected, cells number: {len(d_rows)}')
        gdf_circle = gdf_circle.dissolve(by=[f'{region}',f'{site}','CELL_ID'], aggfunc='first', as_index=False)
        gdf_circle = gdf_circle.reset_index(drop=True)
    
    end = time.time()
    runtime = end-start
    logging.info(f"boundcircle GeoDataFrame has been established, run time: {runtime:4.3f}s, outdoor cells number : {len(gdf_circle)}")
    return gdf_circle
    
def indoor_and_special_cell_process(cell, tech):
    logging.info("indoor cells process starting")
    start = time.time()
    region, site, type = region_dict[tech], site_dict[tech], type_dict[tech]
    df_pos = pd.DataFrame(cell[[f'{region}', f'{site}', 'CELL_ID', 'INDOOR', f'{type}', 'LOCATION']])
    df_pos['geometry'] = df_pos['LOCATION'].apply(wkt.loads)
    gdf_pos = gpd.GeoDataFrame(df_pos, geometry='geometry', crs="EPSG:4326")
    gdf_inpos = gdf_pos[gdf_pos['INDOOR']==1].reset_index(drop=True)
    gdf_MRT_pos = gdf_pos[(gdf_pos[f'{type}']==3) & (gdf_pos['INDOOR']==1)].reset_index(drop=True)
    gdf_tunnel_pos = gdf_pos[gdf_pos[f'{type}']==5].reset_index(drop=True)
    gdf_IB_pos = gdf_pos[gdf_pos[f'{type}']==6].reset_index(drop=True)
    end = time.time()
    runtime = end-start
    logging.info(f"location GeoDataFrame has been established, run time: {runtime:4.3f}s")
    logging.info(f"indoor cells number: {len(gdf_inpos)}, MRT cells number: {len(gdf_MRT_pos)}, tunnel cells number: {len(gdf_tunnel_pos)}, IB cells number: {len(gdf_IB_pos)}")
    return gdf_inpos, gdf_MRT_pos, gdf_tunnel_pos, gdf_IB_pos
    
def loadOSMfile(OSM_path):
    if os.path.isfile(OSM_path):
        logging.info('OSM file loading...')
        geom = pd.read_csv(OSM_path, sep='\t', encoding='utf-8')
        mcc_searching = np.unique(geom['POLYGON_ID'].apply(lambda x: f'{x}'[:3]).tolist())
        if (len(mcc_searching)>1):
            country = '(Multiple mcc in file)'
        else:
            try:
                country = mcc[int(mcc_searching[0])]
            except KeyError:
                country = 'UNKNOWN'
        
        geom_dict = geom.groupby('HOFN_TYPE')['POLYGON_ID'].nunique().to_dict()
        hofn_dict = {1:'water', 2:'coastline', 3:'MRT_underground', 5:'island', 6:'tunnel', 7:'road', 9:'building', 10:'ship road', 11:'village', 14:'railway', 15:'funicular'}
        source_dict = {1:'from OSM', 2:'from customer', 3:'from Research team'}
        for s in geom_dict:
            try:
                temp = geom[geom['HOFN_TYPE']==s]
                temp['POLYGON_ID'] = temp['POLYGON_ID'].apply(lambda x: f'{x}'[4])
                source_num = temp.groupby('POLYGON_ID')['POLYGON_STR'].nunique().to_dict()
                geometry_type = np.unique([x[0].strip() for x in temp.POLYGON_STR.str.split('(')])
                assert len(geometry_type)==1
                logging.info(f'Hofn_type {s}({hofn_dict[s]}) detected, {geometry_type[0].capitalize()} number: {geom_dict[s]}')
                if (s==99):
                    continue
                for ss in source_num:
                    source_percentage = round((source_num[ss]/geom_dict[s])*100,1)
                    logging.info(f'\t{source_percentage} % {source_dict[int(ss)]}')
            except KeyError:
                continue
        logging.info(f'GEO GeoDataFrame has been established, geometries number: {len(geom)}, country: {country}\n')
        
        geom['geometry'] = geom['POLYGON_STR'].apply(wkt.loads)
        gdf_geom = gpd.GeoDataFrame(geom, geometry='geometry', crs="EPSG:4326")
        return gdf_geom
    else:
        logging.error(f"{bcolors.BrightRed}NT2_GEO_POLYGON.tsv file does not exist. Please check that!{bcolors.END}")
        return gpd.GeoDataFrame(None)
    
def remove_ship_route_without_coastline(tech):
    cell_polygon = pd.read_csv(f'{sys.argv[2]}NT2_CELL_POLYGON_{tech}.tsv', sep='\t', dtype=str)
    raw_cell_polygon_len = len(cell_polygon)
    cell_type_group = cell_polygon.groupby([region_dict[tech], site_dict[tech],'CELL_ID'])['HOFN_TYPE'].agg(set)
    cell_type_group_only10 = cell_type_group[cell_type_group.apply(lambda x: '10' in x and '2' not in x)]
    cell_polygon = cell_polygon[~((cell_polygon[[region_dict[tech], site_dict[tech],'CELL_ID']].apply(tuple, axis=1).isin(cell_type_group_only10.index)) & (cell_polygon['HOFN_TYPE']=='10'))]
    new_cell_polygon_len = len(cell_polygon)
    logging.info(f'removed {raw_cell_polygon_len-new_cell_polygon_len} ship route relation')
    cell_polygon.to_csv(f'{sys.argv[2]}NT2_CELL_POLYGON_{tech}.tsv', sep='\t',index=False)
    
def set_Hofn_title_cell(tech):
    output_mode = config['DEFAULT'].getint(f'{tech}output')
    if (tech=='NR' and output_mode!=2):
        title = pd.DataFrame(columns=['PU_ID', 'GNODEB_ID', 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL'])
    elif (tech=='NR' and output_mode==2):
        title = pd.DataFrame(columns=['PU_ID', 'GNODEB_ID', 'CELL_ID', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL'])
    elif (tech=='LTE' and output_mode!=2):
        title = pd.DataFrame(columns=['PU_ID', 'ENODEB_ID', 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL'])
    elif (tech=='LTE' and output_mode==2):
        title = pd.DataFrame(columns=['PU_ID', 'ENODEB_ID', 'CELL_ID', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL'])
    elif(tech=='UMTS' and output_mode!=2):
        title = pd.DataFrame(columns=['RNC_ID', 'SITE_ID', 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL'])
    elif(tech=='UMTS' and output_mode==2):
        title = pd.DataFrame(columns=['RNC_ID', 'SITE_ID', 'CELL_ID', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL'])
    elif(tech=='GSM' and output_mode!=2):
        title = pd.DataFrame(columns=['BSC_ID', 'LAC', 'CELL_ID', 'POLYGON_STR', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL'])
    elif(tech=='GSM' and output_mode==2):   
        title = pd.DataFrame(columns=['BSC_ID', 'LAC', 'CELL_ID', 'POLYGON_ID', 'HOFN_TYPE', 'POS_TYPE', 'POS_INDOOR_TYPE', 'DIST_MIN', 'DIST_MAX', 'ROAD_LEVEL'])
    title.to_csv(f'{sys.argv[2]}NT2_CELL_POLYGON_{tech}.tsv',sep="\t",index=False)
                
            
def buildings_processing(process_range, pu_geoseries):
    try:
        buildings = pd.read_csv(f'{GEO_path}all_buildings.tsv',sep='\t', skiprows=list(range(process_range[0]+1)), header=None, nrows=len(process_range), names=['tile_ID','lon','lat'])
        buildings['geometry'] = [ Point(xy) for xy in zip(buildings.lon, buildings.lat) ]
        buildings_geoseries = gpd.GeoSeries(buildings.geometry)
        sidx = pu_geoseries.sindex.query_bulk(buildings_geoseries, predicate="intersects")
        return { i:buildings.loc[sidx[0][np.where(sidx[1]==i)].tolist()][['tile_ID','lon','lat']] for i in np.unique(sidx[1]) }
    except Exception as e:
        logging.error(e,exc_info=True)

def modify_log(log_file):
    f = open(log_file, 'r')
    words = f.read()
    import re
    words1 = re.sub(r'\[\d+m','',words)
    words2 = re.sub(r'\x1b','',words1)
    f.close()
    f = open(log_file, 'w')
    f.write(words2)
    f.close()
