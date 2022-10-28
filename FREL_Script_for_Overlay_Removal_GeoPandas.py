import geopandas as gpd
from shapely.geometry import Polygon, MultiPolygon, mapping
import matplotlib.pyplot as plt
from pathlib import Path
import datetime
from datetime import datetime
# from datetime import date


class Script_Configs:
    
    def __init__(self):
    
        self.input_path = 'C:\\Users\\user\\Documents\\2_Projetos\\Frel_2022\\Dados\\Amazonia\\SIRENE\\'
    
        self.output_path = 'C:\\Users\\user\\Documents\\2_Projetos\\Frel_2022\\Dados\\Amazonia\\SIRENE\\GeoPandas\\'
        
        self.file_extention = '.shp'
        
        self.plot = True
        
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
    
    trigger_algorithm(configs, files)
    
    log.close_log()



def trigger_algorithm(configs, files):
    
    log = process_log('trigger_algorithm', 'Runnig the algorithm on all the files sequencially.')
    
    for i, file in enumerate(files):
        
        print('\nProcessing file ({}/{} - {}%): '.format(i + 1, len(files), round((i + 1) * 100 / len(files), 1)), file.stem)


        input_data = get_data(file)
        
        if input_data == None:
            
            return None
        
        else:
        
            try:
    
                input_data_exp = multipol_to_pol(input_data)
        
                print('\n  2. Multipolygon conversion to polygon: success. ', str(datetime.now() - log.Start_time))
                
            except:
                
                print('\n  2. Multipolygon conversion to polygon: error. Skipping to the next file.\n')
                
                break
    
    
            try:
                
                remove_dimension_z(input_data_exp)
            
                print('\n  3. Removal of dimension z: success. ', str(datetime.now() - log.Start_time))
            
            except:
                
                print('\n  3. Removal of dimension z: error. Skipping to the next file.\n')
                
                break
    
    
            # diss = input_data_exp.dissolve(by = ['C_PRETORIG', 'C_PRETVIZI', 'CATEGORIG', 'CATEGVIZI', 'TIPO', 'CDW', 'CLITTER', 'CTOTAL4INV', 'CAGB', 'CBGB'], as_index=False)
            
            # print('  Dissolve: success. ', str(datetime.now() - log.Start_time))
            
            # export(diss, configs, file.stem)
            
                    
        
            try:
                
                union = gpd.overlay(input_data_exp, input_data_exp, how = 'union', keep_geom_type = False)
                
                if 'MultiLineString' in geometry_type_check(union):
                    
                    multilines_into_pols(union)
                    
                else: pass
            
                print('\n  4. Union: success. ', str(datetime.now() - log.Start_time))
                
            except Exception as e:
                
                print('\n  4. Union: error: ', e, '\nSkipping to the next file.\n')
                            
                break
                        
            
            export(union, '_un', configs, file.stem, log)
            
            
            # natural_only = union[ union.TIPO_1 == 'NATURAL', union.TIPO_2 == 'NATURAL' ]
    
            # antropic_only = union[ union.TIPO_1 == 'ANTROPIZADA', union.TIPO_2 == 'ANTROPIZADA']
            
            # print('  Natural only: ', len(natural_only), 'Antropic only: ', len(antropic_only))
        
        
            if configs.plot: plot_data(union)
            
            else: pass
        
        break

    log.close_log()



def get_data(file):
    
    print('\n  1. Load file:')
        
    try:
    
        input_data = gpd.read_file( file )
    
        print('\n    success (', str(datetime.now() - log.Start_time), ')')
        
        return input_data
        
    except Exception as e:
        
        print('\n    Error: ', e, '\nSkipping to the next file.\n')
        
        return False
        


def multipol_to_pol(data):
    
    distinct_types = geometry_type_check(data)
        
    if 'MultiPolygon' in distinct_types:
            
        new_data = data.explode()
                
        multipol_to_pol(new_data)
            
    else: new_data = data
        
    return new_data



def geometry_type_check(data):
    
    distinct_types = []

    for pol in data.iterfeatures():
        
        if pol['geometry']['type'] not in distinct_types:
            
            distinct_types.append(pol['geometry']['type'])
            
        else: pass
    
    print('      Geometry types in file: ', distinct_types)
    
    return distinct_types



def remove_dimension_z(data):   

    new_geo = []
    
    for pol in data.geometry:
        
        if pol.has_z:
            
            if pol.geom_type == 'Polygon':
                                
                lines = [xy[:2] for xy in list(pol.exterior.coords)]
                
                new_p = Polygon(lines)
                
                new_geo.append(new_p)
                
    data.geometry = new_geo    



def multilines_into_pols(data):
    
    try:
    
        data['geometry'] = [Polygon(mapping(x)['coordinates']) for x in data.geometry]
        
    except Exception as e:
        
        raise
        
    
    if 'MultiLineString' in geometry_type_check(data):
        
        multilines_into_pols(data)
        
    else: pass
    
    print('      Conversão de linhas em polígonos: sucesso')
    
    return data



def export(data_to_export, operation, configs, original_file_name, log):
    
    try:

        data_to_export.to_file(str(configs.output_path + original_file_name + operation + '.shp'), driver = 'ESRI Shapefile')
        
        print('    Export: success', str(datetime.now() - log.Start_time))
        
    except RuntimeError as e:
    
        print('Error message: ', e)



def plot_data(*args):
    
    fig, ax = plt.subplots(figsize = (10,8))
    
    for data in args:
        
        data.plot(ax = ax)



class process_log:

    def __init__(self, process, description):
        
        self.Process = process
        self.Description = description
        self.Start_time = datetime.now()

        print(str('\n[Log] Processo "' + self.Process + '": ' + self.Description + '\n' + '[Log] Início "' + self.Process + '": ' + str(self.Start_time)))

    def close_log(self):

        end_time = datetime.now()

        print(str('[Log] Fim "' + self.Process + '": ' + str(end_time) + '\n        Duração: ' + str(datetime.now() - self.Start_time)))



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








