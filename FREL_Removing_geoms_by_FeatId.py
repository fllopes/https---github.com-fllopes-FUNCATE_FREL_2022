# Project: FUNCATE / Frel
# author: filipe.lopes@funcate.org.br
# date: 16/09/2022
# Description: remove as geometrias em uma faixa de feat.id()



layer = iface.activeLayer()

print(layer.name())

caps = layer.dataProvider().capabilities()

data = [feat.id() for feat in layer.getFeatures()]

featIds_to_delete = data[6005393 - 40001:]

if caps & QgsVectorDataProvider.DeleteFeatures:

    res = layer.dataProvider().deleteFeatures(featIds_to_delete)

    
print('Contagem final de geometrias: ', layer.featureCount())