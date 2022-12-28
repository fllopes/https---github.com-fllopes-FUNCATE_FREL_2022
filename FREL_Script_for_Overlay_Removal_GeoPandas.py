import geopandas as gpd
import numpy
from shapely.geometry import shape, Polygon, MultiPolygon, LineString, MultiLineString, mapping
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime
import pandas as pd
import psycopg2
from sqlalchemy import create_engine
import platform

data_for_outside_use = []

class Script_Configs:
    
    def __init__(self):
    
        self.input_path = 'C:\\Users\\user\\Documents\\2_Projetos\\Frel_2022\\Dados\\Amazonia\\SIRENE\\' if platform.system() == 'Windows' else '/mnt/c/Users/user/Documents/2_Projetos/Frel_2022/Dados/Amazonia/SIRENE/'
    
        self.output_path = 'C:\\Users\\user\\Documents\\2_Projetos\\Frel_2022\\Dados\\Amazonia\\SIRENE\\GeoPandas\\' if platform.system() == 'Windows' else '/mnt/c/Users/user/Documents/2_Projetos/Frel_2022/Dados/Amazonia/SIRENE/GeoPandas/'
        
        self.user_triggered = True

        self.file_extention = '.shp'

        self.load_to_postgis = False

        self.postgis_url = 'postgresql://postgres:postgres@localhost:5432/ta_qgis_python'
        
        self.plot = True

        self.export_intermediary = True

        self.report_to_file = True

        self.script_version = '1.3'

        self.run_date = datetime.now().strftime('%d_%m_%Y_%Hh_%Mm_%Ss')

        self.report_file_name = str(self.output_path + 'Relatorio_Script_GeoPandas_v' + self.script_version + '_DtExec_' + self.run_date + '.txt')
        
    def input_pth( self, file_name ):
        
        return str( self.input_path + file_name ), str( self.input_path + file_name )


# List all files in directory using pathlib
def locate_files(folder, extension):

    located_files = [entry for entry in Path(folder).iterdir() if entry.is_file() and entry.suffix == extension]

    return located_files


def main():
    
    configs = Script_Configs()
        
    log = process_log('main', 'Início', configs)
    
    files = locate_files(configs.input_path, configs.file_extention)
    
    conditional_print('\nFREL- FUNCATE\nRelatório do Script de Remoção de Sobreposições\nData de Execução: {}\nSistema Operacional: {}\n\nNúmero de arquivos agrupados para processamento: {}\n'.format(configs.run_date, platform.system(), len(files)), configs)

    for i, file in enumerate(files):
                
        success = trigger_algorithm(configs, file, i + 1, len(files), round((i + 1) * 100 / len(files), 1))

        if configs.user_triggered:

            next_file = input('\nPassar para o próximo arquivo (y/n)? Utilize "t" para executar todos os demais arquivos.\n')

            if next_file == 'y' or next_file == 't':

                if next_file == 't':

                    configs.user_triggered = False

                continue

            else: break

        else: break

        # if success == None:

        #     conditional_print('O arquivo "{}" não foi completamente processado.'.format(file.stem), configs)

        # else: break

    # if configs.report_to_file: report.push(configs.output_path)
    
    log.close_log()


def trigger_algorithm(configs, file, file_count, total_files_count, progress):
    
    log = process_log('trigger_algorithm', '\n\n--------------\n({}/{} - {}%) Processando o arquivo: "{}"\n'.format(file_count, total_files_count, progress, file.stem), configs)
    
    loaded_data, success = get_data(file, file_count, log, configs)
        
    if success == False:
        
        return None
    
    else:

        if configs.export_intermediary:
    
            export(loaded_data.file_data, '1Val', configs, file.stem, log)

        else: pass
    
        overlay, success = self_overlay(loaded_data.file_data, log, configs)

        if success == False:
    
            return None

        else:

            if configs.export_intermediary:
    
                export(overlay, '2Ovr', configs, file.stem, log)

            else: pass


        # diss = input_data_exp.dissolve(by = ['C_PRETORIG', 'C_PRETVIZI', 'CATEGORIG', 'CATEGVIZI', 'TIPO', 'CDW', 'CLITTER', 'CTOTAL4INV', 'CAGB', 'CBGB'], as_index=False)
        
        # print('  Dissolve: success. ', str(datetime.now() - log.Start_time))
        
        # export(diss, configs, file.stem)

        # natural_only = union[ union.TIPO_1 == 'NATURAL', union.TIPO_2 == 'NATURAL' ]

        # antropic_only = union[ union.TIPO_1 == 'ANTROPIZADA', union.TIPO_2 == 'ANTROPIZADA']
        
        # print('  Natural only: ', len(natural_only), 'Antropic only: ', len(antropic_only))
    
    
        # if configs.plot: plot_data(union)
        
    log.close_log()


def get_data(file, file_count, log, configs):
    
    conditional_print('\n  {}.1. Carregando o arquivo:'.format(file_count), configs)
    
    class Loaded_data:

        def __init__(self, file_data):
            
            self.file_data = file_data
            self.postgis_data = None

    try:
    
        raw_input_data = gpd.read_file( file )

        data_for_outside_use.append(raw_input_data)

        validated_data = data_validator(raw_input_data, log, configs)

        data_for_outside_use.append(validated_data)

        loaded_data_class = Loaded_data(validated_data)

        if configs.load_to_postgis:
        
            postgis_data = load_to_postgis(validated_data, file, configs)

            loaded_data_class.postgis_data = postgis_data

        conditional_print('\n     Successo: {}'.format(log.subprocess()), configs)
            
        return loaded_data_class, True
        
    except Exception as e:
        
        conditional_print('\n     [get_data] Erro: {}\nPassando para o próximo arquivo.\n'.format(e), configs)
        
        return None, False


def load_to_postgis(data, file, configs):

    try:

        engine = create_engine(configs.postgis_url)

        table_name = str(file.stem + '_' + configs.run_date[:-4])

        data.to_postgis(table_name, engine)

        conditional_print('\n     [load_to_postgis] Dado carregado com sucesso para o postgis. Tabela: "{}".\n'.format(table_name), configs)

        return data, True, table_name
        
    except Exception as e:
        
        conditional_print('\n     [load_to_postgis] Erro ao copiar o dado "{}" para o banco postgis: {}\nPassando para o próximo arquivo.\n'.format(file.stem, e), configs)

        return None, False


def data_validator(data, log, configs):

    conditional_print('\n     [data_validator] Validando geometrias:', configs)

    conditional_print('\n        Número de geometrias no arquivo original: {}'.format(len(data)), configs)

    data = remove_empty_geoms(data, log, configs)

    data = remove_non_pol_geoms(data, log, configs)

    data = remove_repeated_geoms(data, log, configs)

    data = multipol_to_pol(data, log, configs)

    data = remove_dimension_z(data, log, configs)

    conditional_print('\n        Número de geometrias no arquivo após a validação: {}\n'.format(len(data)), configs)

    conditional_print('\n        [data_validator] Sucesso. {}'.format(log.subprocess()), configs)

    return data


def remove_empty_geoms(data, log, configs):

    geoms_to_be_removed_count = len(data[data.geometry == None])

    filtered_data = data

    if geoms_to_be_removed_count != 0:

        filtered_data = data[data.geometry != None]

        count_check(len(data), geoms_to_be_removed_count, len(filtered_data), configs)

    conditional_print('\n        [remove_empty_geoms] Removendo {} geometrias vazias. {}'.format(geoms_to_be_removed_count, log.subprocess()), configs)

    return filtered_data


def count_check(initial_count, geoms_to_be_removed_count, final_count, configs):

    if geoms_to_be_removed_count != 0:

        if final_count == initial_count - geoms_to_be_removed_count:

            conditional_print('\n          [count_check] Contagem de geometrias: ok', configs)

        else:

            conditional_print('\n          [count_check] WARNING - Contagem de geometrias: inconsistente. Encontradas {}, esperando {}.'.format(final_count, initial_count - geoms_to_be_removed_count), configs)


def remove_non_pol_geoms(data, log, configs):

    distinct_types = geometry_type_check(data)

    initial_geoms_count = len(data)

    removed_geoms = {}

    removed_geoms_count = 0

    for geom_type in distinct_types:

        if geom_type != 'Polygon' and geom_type != 'MultiPolygon':

            count = len(data[data.geometry.type == geom_type])

            removed_geoms[geom_type] = count

            removed_geoms_count += count

            data = data[data.geometry.type != geom_type]

    conditional_print('\n        [remove_non_pol_geoms] Removendo {} geometrias que não são polígonos. {} {}'.format(removed_geoms_count, ([str(k + ':' + str(v) + '.') for k, v in removed_geoms.items()] if len(removed_geoms) > 0 else ''), log.subprocess()), configs)

    count_check(initial_geoms_count, removed_geoms_count, len(data), configs)

    return data


def multipol_to_pol(data, log, configs):

    distinct_types = geometry_type_check(data)
        
    if 'MultiPolygon' in distinct_types:

        multipol_data = data[data.geometry.type == 'MultiPolygon']

        data_exp = data.explode(ignore_index=True)

        multipol_data_exp = multipol_data.explode(ignore_index=True)

        conditional_print('\n        [multipol_to_pol] Convertendo {} Multipolygons para {} Polygons. {}'.format(len(multipol_data), len(multipol_data_exp), log.subprocess()), configs)
        
        count_check(len(data), len(multipol_data) - len(multipol_data_exp), len(data_exp), configs)
       
        return data_exp

    else: return data


def geometry_type_check(data):
    
    distinct_types = []

    for pol in data.iterfeatures():
        
        if pol['geometry']['type'] not in distinct_types:
            
            distinct_types.append(pol['geometry']['type'])
                    
    return distinct_types


def remove_dimension_z(data, log, configs):   

    new_geo = []
    
    for pol in data.geometry:
        
        if pol.has_z and pol.geom_type == 'Polygon':
                                
            lines = [xy[:2] for xy in list(pol.exterior.coords)]
            
            new_p = Polygon(lines)
            
            new_geo.append(new_p)

    if len(new_geo):
                
        data.geometry = new_geo

    if len(new_geo) == 0:
        
        conditional_print('\n        [remove_dimension_z] Removendo a dimensão "z" das geometrias: não foi necessário. {}'.format(log.subprocess()), configs)

    else:

        conditional_print('\n        [remove_dimension_z] Removendo a dimensão "z" das geometrias: ok. {}'.format(log.subprocess()), configs)

    return data 


def remove_repeated_geoms(data, log, configs):

    initial_count = len(data)

    data = data.drop_duplicates(ignore_index=True)  # Remove elementos com todas as colunas iguais, mantendo apenas o primeiro deles. Para especificar colunas, informar uma lista: drop_duplicates(['C_PRETORIG'])

    final_count = len(data)

    conditional_print('\n        [remove_repeated_geoms] Removendo {} itens duplicados (geometrias e classes idênticas). {}'.format(initial_count - final_count, log.subprocess()), configs)

    return data


def self_overlay(data, log, configs):

    conditional_print('\n  2. União:', configs)
    
    try:
        
        raw_overlay = gpd.overlay(data, data, how = 'intersection', keep_geom_type = False)

        # raw_sjoin = data.sjoin(data, how="inner", predicate='intersects')

        conditional_print('\n     [self_union] Successo. {}'.format(log.subprocess()), configs)
            
        validated_overlay = data_validator(raw_overlay, log, configs)

        global data_for_outside_use

        data_for_outside_use.append(validated_overlay)

        ready_overlay = data_cleaner(validated_overlay, log, configs)

        data_for_outside_use.append(ready_overlay)

        return ready_overlay, True
        
    except Exception as e:

        raise
        
        conditional_print('\n     [self_union] Erro: "{}"\nPassando para o próximo arquivo.\n'.format(e), configs)

        return None, False


def data_cleaner(data, log, configs):

    conditional_print('\n     [data_cleaner] Limpando o output:', configs)

    single_geoms = data.drop_duplicates(['geometry']).geometry

    for geom in single_geoms:

        data = same_geom_cleaner(data[data.geometry == geom], data, log, configs)

    conditional_print('\n     [data_cleaner] Successo. {}'.format(log.subprocess()), configs)


def same_geom_cleaner(filtered_data, data, log, configs):

    conditional_print('\n       [same_geom_cleaner] Tratando casos com geometrias idênticas:', configs)

    class Pol_geoseries:

        def __init__(self, pol):

            self.pol = pol
            self.index_left = pol.name
            self.left_attrs = Pol_attrs(pol, True)
            self.right_attrs = Pol_attrs(pol, False)
            self.index_right = pol.index_righ
            self.same_left_right_attrs_check = True if ((self.left_attrs.C_PRETORIG == self.right_attrs.C_PRETORIG) & (self.left_attrs.C_PRETVIZI == self.right_attrs.C_PRETVIZI) & (self.left_attrs.CATEGORIG == self.right_attrs.CATEGORIG) & (self.left_attrs.CATEGVIZI == self.right_attrs.CATEGVIZI) & (self.left_attrs.TIPO == self.right_attrs.TIPO) & (self.left_attrs.CDW == self.right_attrs.CDW) & (self.left_attrs.CLITTER == self.right_attrs.CLITTER) & (self.left_attrs.CTOTAL4INV == self.right_attrs.CTOTAL4INV) & (self.left_attrs.CAGB == self.right_attrs.CAGB) & (self.left_attrs.CBGB == self.right_attrs.CBGB)) else False
            self.cross_attrs_indexes = []
            self.delete = False
   

    class Pol_attrs:

        def __init__(self, pol, left_side):

            self.C_PRETORIG = pol.C_PRETORIG if left_side else pol.C_PRETOR_1
            self.C_PRETVIZI = pol.C_PRETVIZI if left_side else pol.C_PRETVI_1
            self.CATEGORIG = pol.CATEGORIG_ if left_side else pol.CATEGORI_1
            self.CATEGVIZI = pol.CATEGVIZI_ if left_side else pol.CATEGVIZ_1
            self.TIPO = pol.TIPO_left if left_side else pol.TIPO_right
            self.CDW = (None if numpy.isnan(pol.CDW_left) else pol.CDW_left) if left_side else (None if numpy.isnan(pol.CDW_right) else pol.CDW_right)
            self.CLITTER = (None if numpy.isnan(pol.CLITTER_le) else pol.CLITTER_le) if left_side else (None if numpy.isnan(pol.CLITTER_ri) else pol.CLITTER_ri)
            self.CTOTAL4INV = (None if numpy.isnan(pol.CTOTAL4INV) else pol.CTOTAL4INV) if left_side else (None if numpy.isnan(pol.CTOTAL4I_1) else pol.CTOTAL4I_1)
            self.CAGB = (None if numpy.isnan(pol.CAGB_left) else pol.CAGB_left) if left_side else (None if numpy.isnan(pol.CAGB_right) else pol.CAGB_right)
            self.CBGB = (None if numpy.isnan(pol.CBGB_left) else pol.CBGB_left) if left_side else (None if numpy.isnan(pol.CBGB_right) else pol.CBGB_right)

    same_left_right_attrs_pols = []

    dif_left_right_attrs_pols = []

    for idx in filtered_data.index:

        pol_geos = Pol_geoseries(filtered_data.iloc[idx])

        if pol_geos.same_left_right_attrs_check == True:

            same_left_right_attrs_pols.append(pol_geos)

        else:

            dif_left_right_attrs_pols.append(pol_geos)

    data = crossed_attrs_cleaner(dif_left_right_attrs_pols, data, log, configs)

    conditional_print('\n       [same_geom_cleaner] Successo. {}'.format(log.subprocess()), configs)

    return data


def crossed_attrs_cleaner(dif_left_right_attrs_pols, data, log, configs):

    conditional_print('\n           [crossed_attrs_cleaner] Tratando casos com atributos idênticos, porém cruzados:', configs)

    for i, pol_geos in enumerate(dif_left_right_attrs_pols):

        while j := (i + 1) <= (len(dif_left_right_attrs_pols) - 1):

            left_right = left_right_equality(pol_geos, dif_left_right_attrs_pols[j])

            if left_right == True:

                right_left = left_right_equality(dif_left_right_attrs_pols[j], pol_geos)

                if right_left == True:

                    pol_geos.cross_attrs_indexes.append(dif_left_right_attrs_pols[j].index_left)

                    dif_left_right_attrs_pols[j].delete == True

                    conditional_print('\n              [crossed_attrs_cleaner] Index principal: {}. Index marcado para deleção: {}'.format(pol_geos.index_left, dif_left_right_attrs_pols[j].index_left), configs)
                    
                    data = data[data.index != dif_left_right_attrs_pols[j].index_left]

    conditional_print('\n           [crossed_attrs_cleaner] Successo. {}'.format(log.subprocess()), configs)

    return data


def left_right_equality(pol_geos_1, pol_geos_2):

    if ((pol_geos_1.left_attrs.C_PRETORIG == pol_geos_2.right_attrs.C_PRETORIG) & (pol_geos_1.left_attrs.C_PRETVIZI == pol_geos_2.right_attrs.C_PRETVIZI) & (pol_geos_1.left_attrs.CATEGORIG == pol_geos_2.right_attrs.CATEGORIG) & (pol_geos_1.left_attrs.CATEGVIZI == pol_geos_2.right_attrs.CATEGVIZI) & (pol_geos_1.left_attrs.TIPO == pol_geos_2.right_attrs.TIPO) & (pol_geos_1.left_attrs.CDW == pol_geos_2.right_attrs.CDW) & (pol_geos_1.left_attrs.CLITTER == pol_geos_2.right_attrs.CLITTER) & (pol_geos_1.left_attrs.CTOTAL4INV == pol_geos_2.right_attrs.CTOTAL4INV) & (pol_geos_1.left_attrs.CAGB == pol_geos_2.right_attrs.CAGB) & (pol_geos_1.left_attrs.CBGB == pol_geos_2.right_attrs.CBGB)):

        return True

    else: return False



def export(data_to_export, operation, configs, original_file_name, log):
    
    try:

        file_name = str(configs.output_path + original_file_name + '_' + configs.run_date + '_' + operation + '.shp')

        data_to_export.to_file(file_name, driver = 'ESRI Shapefile')
        
        conditional_print('\n     [export] Exportando resultado intermeriário (arquivo: {}): successo {}\n'.format(file_name, log.subprocess()), configs)
        
    except RuntimeError as e:
    
        conditional_print('\n     [export] Erro na exportação do resultado intermeriário. Mensagem original:\n{}\n'.format(e), configs)


def plot_data(*args):
    
    fig, ax = plt.subplots(figsize = (10,8))
    
    for data in args:
        
        data.plot(ax = ax)


def conditional_print(something_to_print, conf):
        
    print(something_to_print)

    if conf.report_to_file:

        print(something_to_print, file=open(conf.report_file_name, 'a'))


class process_log:

    def __init__(self, process, description, conf):
        
        self.Process = process
        self.Description = description
        self.Start_time = datetime.now()
        self.Last_subprocess_stop_time = None
        self.configs = conf

        conditional_print(str('\n[Log] Processo "' + self.Process + '": ' + self.Description + '\n' + '[Log] Início "' + self.Process + '": ' + str(self.Start_time)), self.configs)

    def close_log(self):

        end_time = datetime.now()

        conditional_print(str('[Log] Fim "' + self.Process + '": ' + str(end_time) + '\n        Duração: ' + str(datetime.now() - self.Start_time)), self.configs)

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

#data1.plot( color = 'blue', edgecolor = 'black', alpha=0.5)

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

# data2_antrop = data1[(data1.TIPO == 'ANTROPIZADA') & (dado_uniao.C_PRETORIG == 'As')]

# data1_antrop.plot(cmap = 'hsv', column = 'TIPO' , figsize = (10,8))


# 3.4 Looping through items:

# for idx in data.index:

#    geom = data[data.index == idx].geometry
   


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








