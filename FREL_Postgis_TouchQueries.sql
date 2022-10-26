-- Project: FUNCATE / Frel
-- author: filipe.lopes@funcate.org.br
-- date: 12/10/2022
-- Description: consultas em SQL utilizando funcionalidades do postgis



-- 1. Seleciona geometrias que se tocam, mas que tem classes diferentes
-- Resultado: todos os polígonos que tocam outros com classes diferentes, porém multiplicados, pois parece pegar a ida e a volta da operação. Centenas de polígonos repetidos. Foi necessário eliminar as repetições através de script em python no console do qgis.
create table public.amazonia_carbono_vegetacao_1_touch as

        select s.c_pretorig, s.gid, s.geom

                from 	public.amazonia_carbono_vegetacao_1 as s,
                        public.amazonia_carbono_vegetacao_1 as r

                where st_touches (s.geom, r.geom) and s.c_pretorig != r.c_pretorig;

alter table public.amazonia_carbono_vegetacao_1_touch add column id serial primary key;

select * from public.amazonia_carbono_vegetacao_1_touch limit 5



-- 2. Seleciona geometrias com sobreposição no mesmo layer, independente da classe
-- a.geom && b.geom: retorna true se houver intersecção entre o box das entradas. Tira proveito do índice espacial, ganhando eficiência na execução.
-- ST_Relate(a.geom, b.geom, '2********'): condição de que os polígonos devem satisfazer a condição '2********' (padrão DE-9IM), isto é, a intersecção dos polígonos deve formar um polígono.
-- Resultado: 
create table public.amazonia_carbono_vegetacao_1_sobreps as

        select a.c_pretorig, a.gid, a.geom
        
                from amazonia_carbono_vegetacao_1 a

                        inner join amazonia_carbono_vegetacao_1 b on (a.geom && b.geom and ST_Relate(a.geom, b.geom, '2********'))

                        where a.ctid != b.ctid;

alter table public.amazonia_carbono_vegetacao_1_sobreps add column id serial primary key;

select * from public.amazonia_carbono_vegetacao_1_sobreps limit 5



-- 3. Seleciona geometrias com sobreposição no mesmo layer com polígonos da mesma classe
-- a.geom && b.geom: retorna true se houver intersecção entre o box das entradas. Tira proveito do índice espacial, ganhando eficiência na execução.
-- ST_Relate(a.geom, b.geom, '2********'): condição de que os polígonos devem satisfazer a condição '2********' (padrão DE-9IM), isto é, a intersecção dos polígonos deve formar um polígono.
-- Resultado: 
create table public.amazonia_carbono_vegetacao_1_sobreps_iguais as

        select a.gid, a.c_pretorig, a.c_pretvizi, a.categorig, a.categvizi, a.tipo, a.cdw, a.clitter, a.ctotal4inv, a.cagb, a.cbgb,  a.geom
        
                from amazonia_carbono_vegetacao_1 a

                        inner join amazonia_carbono_vegetacao_1 b on (a.geom && b.geom and ST_Relate(a.geom, b.geom, '2********'))

                        where a.ctid != b.ctid
                                and a.c_pretorig = b.c_pretorig
                                and a.c_pretvizi = b.c_pretvizi
                                and a.categorig = b.categorig
                                and a.categvizi = b.categvizi
                                and a.tipo = b.tipo
                                --and a.cdw = b.cdw
                                --and a.clitter = b.clitter
                                --and a.cagb = b.cagb
                                --and a.cbgb = b.cbgb
                                ;

alter table public.amazonia_carbono_vegetacao_1_sobreps_iguais add column id serial primary key;

select * from public.amazonia_carbono_vegetacao_1_sobreps_iguais limit 5



-- 4. Seleciona as geometrias iguais. Não são polígonos iguais, mas sim geometrias, portanto as classes podem ser diferentes.
-- Resultado: exatamente os polígonos sobrepostos, independente da classe.
create table public.amazonia_carbono_vegetacao_1_geoms_iguais as

        select a.gid, a.c_pretorig, a.c_pretvizi, a.categorig, a.categvizi, a.tipo, a.cdw, a.clitter, a.ctotal4inv, a.cagb, a.cbgb,  a.geom
        
                from amazonia_carbono_vegetacao_1 a

                        inner join amazonia_carbono_vegetacao_1 b on
						
                                (a.geom && b.geom and ST_Equals(a.geom, b.geom))

                        where a.ctid != b.ctid;

alter table public.amazonia_carbono_vegetacao_1_geoms_iguais add column id serial primary key;

select * from public.amazonia_carbono_vegetacao_1_geoms_iguais limit 5

select count(*) from public.amazonia_carbono_vegetacao_1_geoms_iguais



-- 5. Dissolve polígonos com mesmas classes
-- Resultado: dissolve realizado. Removendo a função ST_Dump, o resultado é o mesmo, mas com um multipolygon para cada conjunto de polígonos com classes iguais.
create table public.amazonia_carbono_vegetacao_1_dissolved as

        select a.c_pretorig, a.c_pretvizi, a.categorig, a.categvizi, a.tipo, (ST_Dump(ST_MemUnion(a.geom))).geom as geom
        
                from amazonia_carbono_vegetacao_1 a

                group by a.c_pretorig, a.c_pretvizi, a.categorig, a.categvizi, a.tipo;

alter table public.amazonia_carbono_vegetacao_1_dissolved add column id serial primary key;

select * from public.amazonia_carbono_vegetacao_1_dissolved limit 5



-- 6. Seleciona geometrias com sobreposição no mesmo layer com valores diferentes na coluna "tipo" ("natural" ou "antropizada")
-- a.geom && b.geom: retorna true se houver intersecção entre o box das entradas. Tira proveito do índice espacial, ganhando eficiência na execução.
-- ST_Relate(a.geom, b.geom, '2********'): condição de que os polígonos devem satisfazer a condição '2********' (padrão DE-9IM), isto é, a intersecção dos polígonos deve formar um polígono.
-- Resultado: 
create table public.amazonia_carbono_vegetacao_1_sobreps_tipos_difs_v4 as

        select a.gid, a.c_pretorig, a.c_pretvizi, a.categorig, a.categvizi, a.tipo, a.cdw, a.clitter, a.ctotal4inv, a.cagb, a.cbgb,  a.geom
        
                from amazonia_carbono_vegetacao_1 a

                        inner join amazonia_carbono_vegetacao_1_dissolved_v2 b on (a.geom && b.geom and ST_Relate(a.geom, b.geom, '2********'))

                        where a.tipo = 'ANTROPIZADA' and a.tipo != b.tipo;

alter table public.amazonia_carbono_vegetacao_1_sobreps_tipos_difs_v4 add column id serial primary key;

select * from public.amazonia_carbono_vegetacao_1_sobreps_tipos_difs_v4 limit 5