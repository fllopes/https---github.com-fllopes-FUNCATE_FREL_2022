import geopandas as gpd
from sqlalchemy import create_engine
import platform

file_path = r'C:\\Users\\user\\Documents\\2_Projetos\\Frel_2022\\Dados\\Amazonia\\SIRENE\\amazonia_carbono_vegetacao_1.shp' if platform.system() == 'Windows' else r'/mnt/c/Users/user/Documents/2_Projetos/Frel_2022/Dados/Amazonia/SIRENE/amazonia_carbono_vegetacao_1.shp'

input_data = gpd.read_file( file_path )

engine = create_engine("postgresql://postgres:postgres@localhost:5432/ta_qgis_python")  

#input_data.to_postgis("my_table1", engine)

sql = 'select '
    
for col in input_data.columns:
    
    if col != 'geometry':
        
        sql += str(col + ', ')
        
sql += ' geometry as geom from my_table2'
    

df = gpd.read_postgis(('select "C_PRETVIZI", "geometry" as geom from my_table2'), engine)

df_As = df[df.C_PRETVIZI == 'As']

df_As.plot(figsize = (15,8))

print(df_As)