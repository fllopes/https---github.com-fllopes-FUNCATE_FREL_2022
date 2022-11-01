import re
import geopandas as gpd
from shapely.geometry import shape, Polygon, MultiPolygon, LineString, MultiLineString, mapping
import matplotlib.pyplot as plt
from pathlib import Path
import datetime
from datetime import datetime
# from datetime import date
import pandas as pd


class Script_Configs:
    
    def __init__(self):
    
        self.input_path = 'C:\\Users\\user\\Documents\\2_Projetos\\Frel_2022\\Dados\\Amazonia\\SIRENE\\'
    
        self.output_path = 'C:\\Users\\user\\Documents\\2_Projetos\\Frel_2022\\Dados\\Amazonia\\SIRENE\\GeoPandas\\'
        
        self.file_extention = '.shp'
        
        self.plot = True

        self.export_intermediary = True
        
    def input_pth( self, file_name ):
        
        return str( self.input_path + file_name )



# List all files in directory using pathlib
def locate_files(folder, extension):

    located_files = [entry for entry in Path(folder).iterdir() if entry.is_file() and entry.suffix == extension]

    return located_files



def main():
    
    log = process_log('main', 'Início')
        
    configs = Script_Configs()
    
    files = locate_files(configs.input_path, configs.file_extention)
    
    print('\nNumber of files located and listed for processing: ', len(files))

    for i, file in enumerate(files):
                
        success = trigger_algorithm(configs, file, i + 1, len(files), round((i + 1) * 100 / len(files), 1))

        if success == None:

            print('File "{}" NOT fully PROCESSED.'.format(file.stem))

            continue

        else: break
    
    log.close_log()



def trigger_algorithm(configs, file, file_count, total_files_count, progress):
    
    log = process_log('trigger_algorithm', '\n\nProcessing file ({}/{} - {}%): {}'.format(file_count, total_files_count, progress, file.stem))
    
    input_data, success = get_data(file, log)
        
    if success == False:
        
        return None
    
    else:
    
        union, success = self_union(input_data, log)

        if success == False:
    
            return None

        else:

            if configs.export_intermediary:
    
                export(union, '_un', configs, file.stem, log)

            else: pass


        # diss = input_data_exp.dissolve(by = ['C_PRETORIG', 'C_PRETVIZI', 'CATEGORIG', 'CATEGVIZI', 'TIPO', 'CDW', 'CLITTER', 'CTOTAL4INV', 'CAGB', 'CBGB'], as_index=False)
        
        # print('  Dissolve: success. ', str(datetime.now() - log.Start_time))
        
        # export(diss, configs, file.stem)

        # natural_only = union[ union.TIPO_1 == 'NATURAL', union.TIPO_2 == 'NATURAL' ]

        # antropic_only = union[ union.TIPO_1 == 'ANTROPIZADA', union.TIPO_2 == 'ANTROPIZADA']
        
        # print('  Natural only: ', len(natural_only), 'Antropic only: ', len(antropic_only))
    
    
        if configs.plot: plot_data(union)
        
    log.close_log()



def get_data(file, log):
    
    print('\n  1. Load file:')
        
    try:
    
        raw_input_data = gpd.read_file( file )

        input_data = data_validator(raw_input_data, log)

        print('\n     Success: ', log.subprocess())
    
        print('\n     Number of geometries in the original file: {}'.format(len(input_data)))
        
        return input_data, True
        
    except Exception as e:
        
        print('\n     [get_data] Error: ', e, '\nSkipping to the next file.\n')
        
        return None, False
        


def data_validator(data, log):

    print('\n     Validating data:')

    print('\n     Number of geometries in the original file: {}'.format(len(data)))

    data = remove_empty_geoms(data, log)

    data = remove_non_pol_geoms(data, log)

    data = multipol_to_pol(data, log)

    data = remove_dimension_z(data)

    return data



def remove_empty_geoms(data, log):

    geoms_to_be_removed_count = len(data[data.geometry == None])

    print('\n        [remove_empty_geoms] Removing {} empty geometries.'.format(geoms_to_be_removed_count), log.subprocess())

    filtered_data = data[data.geometry != None]

    count_check(len(data), geoms_to_be_removed_count, len(filtered_data))

    return filtered_data



def count_check(initial_count, geoms_to_be_removed_count, final_count):

    if geoms_to_be_removed_count != 0:

        if final_count == initial_count - geoms_to_be_removed_count:

            print('\n          [count_check] Geometry count: ok')

        else:

            print('\n          [count_check] Geometry count: not matching. Got {}, expecting {}.'.format(final_count, initial_count - geoms_to_be_removed_count))



def remove_non_pol_geoms(data, log):

    distinct_types = geometry_type_check(data)

    initial_geoms_count = len(data)

    removed_geoms = 0

    for geom_type in distinct_types:

        if geom_type != 'Polygon' and geom_type != 'MultiPolygon':

            removed_geoms += len(data[data.geometry.type == geom_type])

            data = data[data.geometry.type != geom_type]

    print('\n        [remove_non_pol_geoms] Removing {} non-polygon geometries.'.format(removed_geoms), log.subprocess())

    count_check(initial_geoms_count, removed_geoms, len(data))

    return data



def multipol_to_pol(data, log):

    distinct_types = geometry_type_check(data)
        
    if 'MultiPolygon' in distinct_types:

        multipol_data = data[data.geometry.type == 'MultiPolygon']

        print('\n        [multipol_to_pol] Converting {} Multipolygons to polygon.'.format(len(multipol_data)), log.subprocess())

        data_exp = data.explode()

        multipol_data_exp = multipol_data.explode()
        
        geometry_type_check(data_exp)

        count_check(len(data), len(multipol_data) - len(multipol_data_exp), len(data_exp))
       
        return data_exp

    else: return data



def geometry_type_check(data):
    
    distinct_types = []

    for pol in data.iterfeatures():
        
        if pol['geometry']['type'] not in distinct_types:
            
            distinct_types.append(pol['geometry']['type'])
                
    print('\n           [geometry_type_check] Geometry types in file: ', distinct_types)
    
    return distinct_types



def remove_dimension_z(data):   

    new_geo = []
    
    for pol in data.geometry:
        
        if pol.has_z and pol.geom_type == 'Polygon':
                                
            lines = [xy[:2] for xy in list(pol.exterior.coords)]
            
            new_p = Polygon(lines)
            
            new_geo.append(new_p)
                
    data.geometry = new_geo

    return data 



def self_union(data, log):

    print('\n  2. Union:')
    
    try:
        
        # raw_union = gpd.overlay(data, data, how = 'union', keep_geom_type = False)

        raw_union = data.sjoin(data, how="inner", predicate='intersects')

        union = data_validator(raw_union, log)
            
        print('\n     Success. ', log.subprocess())

        return union, True
        
    except Exception as e:
        
        print('\n     [self_union] Error: ', e, '\nSkipping to the next file.\n')

        return None, False
    


def export(data_to_export, operation, configs, original_file_name, log):
    
    try:

        data_to_export.to_file(str(configs.output_path + original_file_name + operation + '.shp'), driver = 'ESRI Shapefile')
        
        print('     Export: success', log.subprocess())
        
    except RuntimeError as e:
    
        print('     [export] Error message: ', e)



def plot_data(*args):
    
    fig, ax = plt.subplots(figsize = (10,8))
    
    for data in args:
        
        data.plot(ax = ax)



class process_log:

    def __init__(self, process, description):
        
        self.Process = process
        self.Description = description
        self.Start_time = datetime.now()
        self.Last_subprocess_stop_time = None

        print(str('\n[Log] Processo "' + self.Process + '": ' + self.Description + '\n' + '[Log] Início "' + self.Process + '": ' + str(self.Start_time)))

    def close_log(self):

        end_time = datetime.now()

        print(str('[Log] Fim "' + self.Process + '": ' + str(end_time) + '\n        Duração: ' + str(datetime.now() - self.Start_time)))

    def subprocess(self):

        if self.Last_subprocess_stop_time == None:

            self.Last_subprocess_stop_time = datetime.now()

            return str(self.Last_subprocess_stop_time - self.Start_time)

        else:

            now = datetime.now()

            subprocess_duration = now - self.Last_subprocess_stop_time

            self.Last_subprocess_stop_time = now

            return str(subprocess_duration)



main()


# --------------------
# 1. READ AND WRITE DATA


# If the full path is not provided, the path to the python script is assumed.

# 1.1 Read:

# data1 = gpd.read_file(r'C:\Users\user\Documents\2_Projetos\Frel_2022\Dados\Amazonia\SIRENE\processados\amazonia_carbono_vegetacao_1_pol.shp')

# data2 = gpd.read_file(r'C:\Users\user\Documents\2_Projetos\Frel_2022\Dados\Amazonia\SIRENE\processados\amazonia_carbono_vegetacao_1_pol_aio.shp')

# 1.2 Write: (Export data / create new shapefile)

# data1_antrop.to_file('C:/Users/user/Documents/2_Projetos/Frel_2022/Dados/Amazonia/SIRENE/processados/antropizados.shp', driver = 'ESRI Shapefile')


# 1.3 Verifications

    # 1.3.1 Checking the columns:
        
# data1.columns

    # 1.3.2 Checking the coordinate System (CRS):
        
# data1.crs



# --------------------
# 2. PLOTTING DATA


# 2.1 Single plot:
    
    # 2.1.1 No customization:
        
# data1.plot()

    # 2.1.2 Some Customization:
        
#data1.plot(figsize=(10,8))

#data1.plot( color = 'blue', edgecolor = 'black')

#data1.plot(cmap = 'hsv', column = 'TIPO' , figsize = (10,8))


# 2.2 Multi data plotting (matplotlib)

# fig, ax = plt.subplots(figsize = (10,8))

# data1.plot(ax = ax, color = 'blue')

# data2.plot(ax = ax, color = 'red', edgecolor = 'none')



# --------------------
# 3. DATA MANIPULATION


# 3.1 Change the crs:
        
# data1.to_crs(epsg = 4326)


# 3.2 Create new field (attribute column):
    
# data1['new_attribute_column_name'] = value_to_insert_in_all_entries


# 3.3 Filtering:

# data1_antrop = data1[data1.TIPO == 'ANTROPIZADA']

#data1_antrop.plot(cmap = 'hsv', column = 'TIPO' , figsize = (10,8))
   


# --------------------
# 4. SPATIAL OPERATIONS


# 4.1 OVERLAY: how = intersection, union, difference, symmetric_difference

    # 4.1.1 Intersection:
        
# intersection = gpd.overlay(data1, data2, how = 'intersection')
# intersection.plot(ax = ax)

    # 4.1.2 Union
    
# union = gpd.overlay(data1, data2, how = 'union')
# union.plot(ax = ax)

    # 4.1.3 Difference
    
# dif = gpd.overlay(data1, data2, how = 'difference')
# dif.plot(ax = ax)

    # 4.1.4 Symmetric Difference
    
# sim_dif = gpd.overlay(data1, data2, how = 'symmetric_difference')
# sim_dif.plot(ax = ax)


# 4.2 Dissolve: to dissolve, first create the union to gather the data in the same dataframe

# union = gpd.overlay(data1[data1.TIPO == 'ANTROPIZADA'], data1[data1.TIPO == 'ANTROPIZADA'], how = 'union')
# diss = data1.dissolve(by = 'TIPO')
# diss.plot(ax = ax)


# 4.3 Buffer:
    
# buff = data1['geometry'].buffer(distance = 50000)
# buff.plot(ax = ax)


# 4.4 Centroid:
    
# buff = data1['geometry'].centroid
# buff.plot(ax = ax, color = 'black')

# 4.5 Spatial Join

# joint_data = gpd.sjoin(data1, data2, how = 'inner', predicate = 'intersects')

# intersected_data = joint_data[joint_data.aoi_name == 'filipe_aoi']

# joint_data.plot(ax = ax)

# intersected_data.plot(ax = ax)








