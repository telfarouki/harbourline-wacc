-- Harbourline WACC — weekly reference data (run once in Supabase > SQL Editor)
create table if not exists public.market_snapshots (
  week        text primary key,              -- e.g. 2026-W46
  as_of       date not null,
  global      jsonb not null,
  countries   jsonb not null,                -- { "AGO": {...}, ... } see research/SCHEMA.md
  changes     jsonb not null default '[]',
  source_file text,
  imported_at timestamptz not null default now()
);
alter table public.market_snapshots enable row level security;
drop policy if exists "signed-in users read snapshots" on public.market_snapshots;
create policy "signed-in users read snapshots" on public.market_snapshots
  for select to authenticated using (true);
-- Writes are done only by the import Action (service key) and the engine; no insert/update policy on purpose.
