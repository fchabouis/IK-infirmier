-- Remove duplicate infirmary rows sharing the same RPPS, keeping the smallest id.
delete from public.infirmary a
using public.infirmary b
where a.rpps is not null
  and a.rpps = b.rpps
  and a.id > b.id;

-- Prevent future duplicates. NULL rpps remain allowed (manually added entries).
alter table public.infirmary
  add constraint infirmary_rpps_key unique (rpps);
