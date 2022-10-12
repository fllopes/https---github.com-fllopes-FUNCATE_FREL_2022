-- Project: FUNCATE / Frel
-- author: filipe.lopes@funcate.org.br
-- date: 12/10/2022
-- Description: seleciona as geometrias que tocam geometrias com classes diferentes



create table public.amazonia_carbono_vegetacao_1_touch as

    select s.c_pretorig, s.gid, s.geom

        from 	public.amazonia_carbono_vegetacao_1 as s,
                public.amazonia_carbono_vegetacao_1 as r

        where st_touches (s.geom, r.geom) and s.c_pretorig != r.c_pretorig;

alter table public.amazonia_carbono_vegetacao_1_touch add column id serial primary key;

select * from public.amazonia_carbono_vegetacao_1_touch limit 5