# Project: FUNCATE / Frel
# author: filipe.lopes@funcate.org.br
# date: 04/09/2022
# Description: lista a contagem de geometrias das camadas desejadas visando a conferência de mosaicos.



layers = QgsProject.instance().mapLayers().values()

for layer in layers:
    
    if str(layer.name())[:3] == 'AMZ':
        
        print(layer.name(), layer.featureCount())
        
    else: pass