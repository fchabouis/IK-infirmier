create or replace function nearby_infirmaries(lat float, lng float, limit_n int default 10)
returns table (
  id bigint, rpps text, nom text, prenom text,
  adresse text, rue text, code_postal text, ville text,
  departement text, region text, visites_domicile boolean,
  distance_m float
)
language sql
set search_path = ''
as $$
  select
    id, rpps, nom, prenom, adresse, rue,
    code_postal, ville, departement, region,
    visites_domicile,
    extensions.st_distance(position, extensions.st_setsrid(extensions.st_makepoint(lng, lat), 4326)::extensions.geography) as distance_m
  from public.infirmary
  where position is not null
  order by position operator(extensions.<->) extensions.st_setsrid(extensions.st_makepoint(lng, lat), 4326)::extensions.geography
  limit limit_n;
$$;