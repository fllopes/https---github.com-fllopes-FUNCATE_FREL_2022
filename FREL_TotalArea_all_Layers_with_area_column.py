# Project: FUNCATE / Frel
# author: filipe.lopes@funcate.org.br
# date: 06/09/2022
# Description: calcula a área total de todos os layers que possuem camada de área


layers = QgsProject.instance().mapLayers().values()

possiveis_colunas_de_area = {'area_m2', 'km2'}

for layer in layers:

    print(layer.name())
    
    fields_list = {f.name() for f in layer.fields()}
    
    print(fields_list)
    
    for field_name in fields_list.intersection(possiveis_colunas_de_area):

        area_total = 0

        for feat in layer.getFeatures():
    
            area_total += feat[field_name]
    
        print('Area total em ', field_name, ' : ', area_total)