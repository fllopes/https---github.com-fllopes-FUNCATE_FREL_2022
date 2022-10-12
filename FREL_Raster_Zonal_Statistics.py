# Project: FUNCATE / Frel
# author: filipe.lopes@funcate.org.br
# date: 10/10/2022
# Description: executa o algoritmo de estatística zonal em múltiplos rasters no QGis

layers = QgsProject.instance().mapLayers().values()

for layer in layers:
    
    if str(layer.name()).startswith('CarbonoVeg'):

        prefix = layer.name()[-5:]

        params = {
            
            'INPUT_RASTER': layer.name(),
            'RASTER_BAND': 1,
            'INPUT_VECTOR': 'amz_yearlu_dsm_16a21_idt_vp_rmolv_rec22864',
            'COLUMN_PREFIX': prefix + '_',
            'STATISTICS' : [2,5,6,11]
        
        }
        
        processing.run("qgis:zonalstatistics", params)
	  
print ('Finalizado')


# { 'INPUT' : 'C:/Users/user/Documents/2_Projetos/Frel_2022/Dados/Amazonia/Testes_desmatamento/amz_yearlu_dsm_16a21_idt_vp_rmolv_rec22864.shp',
# 'INPUT_RASTER' : 'C:/Users/user/Documents/2_Projetos/Frel_2022/Dados/Amazonia/Testes_desmatamento/CarbonoVeg_Amazonia_total_tiff_4inventario_rec22864.tif',
# 'OUTPUT' : 'TEMPORARY_OUTPUT' }
