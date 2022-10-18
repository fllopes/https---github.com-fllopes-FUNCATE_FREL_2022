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

    output_layer1_name = str(initial_layer.name() + '_sobreps_iguais_script')

    success1 = db_writer(initial_layer.name(), output_layer1_name)

    if not success1:

        log.close_log()

        return None

    else:

        output_layer1 = load_output_layer(output_layer1_name)

        if output_layer1 == False:

            log.close_log()

            return None

        else:

            success2 = layer_duplicate_removal(output_layer1)

            if not success2:

                log.close_log()

                return None

            else:

                pass

    log.close_log()

    



def db_writer(initial_layer, layer_to_create):

    log = process_log('db_writer', 'Criando layer "{}" contendo os polígonos que tocam outros de mesmos c_pretorig, c_pretvizi, categorig, categvizi, tipo'.format(layer_to_create))

    success = True

    try:

        conn = psycopg2.connect(dbname='ta_qgis_python', user='postgres', password='postgres', host='localhost', port='5432')

        cur = conn.cursor()

        cur.execute("create table public.{} as select a.gid, a.c_pretorig, a.c_pretvizi, a.categorig, a.categvizi, a.tipo, a.cdw, a.clitter, a.ctotal4inv, a.cagb, a.cbgb,  a.geom from {} a inner join {} b on (a.geom && b.geom and ST_Relate(a.geom, b.geom, '2********')) where a.ctid != b.ctid and a.c_pretorig = b.c_pretorig and a.c_pretvizi = b.c_pretvizi and a.categorig = b.categorig and a.categvizi = b.categvizi and a.tipo = b.tipo;".format(layer_to_create, initial_layer, initial_layer))

        cur.execute("alter table public.{} add column id serial primary key;".format(layer_to_create))

        conn.commit()

        cur.close()

        conn.close()

    except: raise

    log.close_log()

    return success



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





