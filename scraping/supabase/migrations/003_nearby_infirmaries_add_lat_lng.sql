-- Add latitude and longitude to nearby_infirmaries return type
drop function if exists public.nearby_infirmaries(double precision, double precision, integer);

create or replace function public.nearby_infirmaries(lat double precision, lng double precision, limit_n integer default 10)
  returns table(
    id bigint,
    rpps text,
    nom text,
    prenom text,
    adresse text,
    rue text,
    code_postal text,
    ville text,
    departement text,
    region text,
    visites_domicile boolean,
    distance_m double precision,
    latitude double precision,
    longitude double precision
  )
  language sql
  set search_path to ''
as $$
  select
    id, rpps, nom, prenom, adresse, rue,
    code_postal, ville, departement, region,
    visites_domicile,
    extensions.st_distance(position, extensions.st_setsrid(extensions.st_makepoint(lng, lat), 4326)::extensions.geography) as distance_m,
    extensions.st_y(position::extensions.geometry) as latitude,
    extensions.st_x(position::extensions.geometry) as longitude
  from public.infirmary
  where position is not null
  order by position operator(extensions.<->) extensions.st_setsrid(extensions.st_makepoint(lng, lat), 4326)::extensions.geography
  limit limit_n;
$$;
