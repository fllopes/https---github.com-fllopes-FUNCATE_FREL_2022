# Project: FUNCATE / Frel
# author: filipe.lopes@funcate.org.br
# date: 12/10/2022
# Description: remove as geometrias repetidas com base em id proveniente de layer original



layer = iface.activeLayer()

print(layer.name())

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

    print('Falta a capabilities "DeleteFeatures".')

print('Finalizado.')
