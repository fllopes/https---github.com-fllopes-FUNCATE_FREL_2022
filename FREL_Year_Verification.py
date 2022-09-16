# Project: FUNCATE / Frel
# author: filipe.lopes@funcate.org.br
# date: 16/09/2022
# Description: verifica se há alguma geometria com o ano diferente do esperado


layer = iface.activeLayer()

print(layer.name())
ok = 0
nao_ok = 0

for feat in layer.getFeatures():
    
    if feat['data_pas'][:4] == '2019':
        
        ok += 1
        
    else:
        
        nao_ok += 1
        
print('Ok: ', ok, '/ Não ok: ', nao_ok)
