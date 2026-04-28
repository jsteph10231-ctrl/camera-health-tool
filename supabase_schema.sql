create table if not exists public.app_datasets (
  name text primary key,
  rows jsonb not null default '[]'::jsonb,
  updated_at timestamptz not null default now()
);

alter table public.app_datasets enable row level security;

create policy "Allow app reads for authenticated key"
on public.app_datasets
for select
using (true);

create policy "Allow app writes for authenticated key"
on public.app_datasets
for insert
with check (true);

create policy "Allow app updates for authenticated key"
on public.app_datasets
for update
using (true)
with check (true);
