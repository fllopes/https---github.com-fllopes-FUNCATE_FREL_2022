# Project: FUNCATE / Frel
# author: filipe.lopes@funcate.org.br
# date: 19/08/2022
# Description: lista o nome de todas as colunas da camada ativa


layer = iface.activeLayer()

print(layer.name())

for field in layer.fields():
    
    print(field.name())