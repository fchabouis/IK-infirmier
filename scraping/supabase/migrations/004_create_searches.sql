-- Create the searches table to log user searches
create table public.searches (
  id bigint generated always as identity primary key,
  query text not null,
  position geography(Point, 4326) not null,
  searched_at timestamptz not null default now()
);

-- Spatial index for displaying searches on a map
create index idx_searches_position on public.searches using gist (position);

-- Index for time-based queries
create index idx_searches_searched_at on public.searches (searched_at);

-- Enable Row Level Security
alter table public.searches enable row level security;

-- Public read access
create policy "Public read access" on public.searches
  for select using (true);

-- Public insert access (anonymous users can log searches)
create policy "Public insert access" on public.searches
  for insert with check (true);
