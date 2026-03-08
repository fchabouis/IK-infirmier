-- Enable PostGIS extension for geographic data
create extension if not exists postgis with schema extensions;

-- Create the infirmary table
create table public.infirmary (
  id bigint generated always as identity primary key,
  rpps text,
  nom text,
  prenom text,
  adresse text,
  rue text,
  code_postal text,
  ville text,
  departement text,
  region text,
  position geography(Point, 4326),
  visites_domicile boolean
);

-- Index on RPPS (national unique identifier for health professionals)
create index idx_infirmary_rpps on public.infirmary (rpps) where rpps is not null;

-- Spatial index for geographic queries (nearest nurse, radius search)
create index idx_infirmary_position on public.infirmary using gist (position);

-- Index for common filters
create index idx_infirmary_code_postal on public.infirmary (code_postal);
create index idx_infirmary_departement on public.infirmary (departement);
create index idx_infirmary_region on public.infirmary (region);
create index idx_infirmary_ville on public.infirmary (ville);

-- Enable Row Level Security
alter table public.infirmary enable row level security;

-- Public read access (directory data is public)
create policy "Public read access" on public.infirmary
  for select using (true);

comment on table public.infirmary is 'Directory of nurses (infirmières) from sante.fr';
comment on column public.infirmary.rpps is 'RPPS national identifier for health professionals';
comment on column public.infirmary.position is 'Geographic location (SRID 4326 / WGS84)';
