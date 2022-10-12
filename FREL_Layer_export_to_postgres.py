# Project: FUNCATE / Frel
# author: filipe.lopes@funcate.org.br
# date: 11/10/2022
# Description: copia um layer local para o banco de dados postgis (tem que ser potgis). Não aceita dados multipolygon.



project = QgsProject.instance()

layer = project.mapLayersByName('amz_yearlu_dsm_16a21_idt_vp_rmolv_rec22864')[0]

uri = 'dbname=\'ta_qgis_python\' host=localhost port=5432 user=\'postgres\' password=\'postgres\' type=POLYGON sslmode=disable table="public"."imported_data" (geometry) key=\'uid\' '

err = QgsVectorLayerExporter.exportLayer(layer, uri, "postgres", layer.crs() )

if err[0] != QgsVectorLayerExporter.NoError:

    print('Import layer {} failed with error {}'.format( layer.name(), err) )

else:

    print('Layer {} import ok'.format( layer.name() ) )
