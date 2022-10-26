# Project: FUNCATE / Frel
# author: filipe.lopes@funcate.org.br
# date: 18/10/2022
# Description: script para identificação e remoção de dados sobrepostos


import psycopg2
import datetime
from datetime import datetime


def main():

    log = process_log('main', 'Início')

    initial_layer = QgsProject.instance().mapLayersByName("amazonia_carbono_vegetacao_1")[0]

    dissolved_layer_name = str(initial_layer.name() + '_diss_script')

    dissolved_layer = layer_dissolve(initial_layer.name(), dissolved_layer_name)

    if dissolved_layer == False:

        log.close_log()

        return None

    else:

        pass

        # success2 = layer_duplicate_removal(dissolved_layer)

        # if not success2:

        #     log.close_log()

        #     return None

        # else:

        #     pass

    log.close_log()


    
def layer_dissolve(input_layer, output_layer_name):

    log = process_log('same_class_touch', 'Criando layer "{}" contendo os polígonos que tocam outros de mesmos c_pretorig, c_pretvizi, categorig, categvizi, tipo'.format(output_layer_name))

    main_query = "create table public.{} as select a.c_pretorig, a.c_pretvizi, a.categorig, a.categvizi, a.tipo, (ST_Dump(ST_MemUnion(a.geom))).geom as geom from {} a group by a.c_pretorig, a.c_pretvizi, a.categorig, a.categvizi, a.tipo;".format(output_layer_name, input_layer)

    create_primary_key = "alter table public.{} add column id serial primary key;".format(output_layer_name)

    run_postgis_query(main_query, create_primary_key)

    log.close_log()

    return load_output_layer(output_layer_name)



def run_postgis_query(*queries):

    try:

        conn = psycopg2.connect(dbname='ta_qgis_python', user='postgres', password='postgres', host='localhost', port='5432')

        cur = conn.cursor()

        for query in queries:

            cur.execute(query)

        conn.commit()

        cur.close()

        conn.close()

    except: raise



def load_output_layer(layer_name):

    log = process_log('load_output_layer', 'Carregando layer "{}" para o QGis'.format(layer_name))

    uri = QgsDataSourceUri()

    uri.setConnection("localhost", "5432", "ta_qgis_python", "postgres", "postgres")

    uri.setDataSource("public", layer_name, "geom", "", "id")

    vlayer = QgsVectorLayer(uri.uri(False), layer_name, "postgres")

    if not vlayer.isValid():

        print("Layer failed to load!")

        log.close_log()

        return False

    else:
        
        QgsProject.instance().addMapLayer(vlayer)

    log.close_log()

    return vlayer


    
def layer_duplicate_removal(layer):

    log = process_log('layer_duplicate_removal', 'Remoção dos polígono duplicados com base no gid original.')

    caps = layer.dataProvider().capabilities()

    if caps & QgsVectorDataProvider.DeleteFeatures:

        first_feats = []

        extra_feats = []

        for feat in layer.getFeatures():

            if feat['gid'] not in [first_feat['gid'] for first_feat in first_feats]:

                first_feats.append(feat)

            else:

                extra_feats.append(feat.id())

        deletion = layer.dataProvider().deleteFeatures(extra_feats)

        print('Total de geometrias removidas: ', len(extra_feats))

    else:

        print('Não foi possível remover polígonos repetidos. Falta a capabilities "DeleteFeatures".')

        log.close_log()

        return False

    log.close_log()

    return True



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