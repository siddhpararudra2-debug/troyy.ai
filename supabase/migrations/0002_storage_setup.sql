-- Setup Storage Buckets for Engineering OS

-- 1. Create Buckets
insert into storage.buckets (id, name, public) values 
  ('cad-files', 'cad-files', false),
  ('pcb-files', 'pcb-files', false),
  ('simulation-files', 'simulation-files', false),
  ('research-files', 'research-files', false),
  ('reports', 'reports', true), -- Public access for sharing
  ('documents', 'documents', false),
  ('telemetry', 'telemetry', false)
on conflict (id) do nothing;

-- 2. Storage Policies for Authenticated Users (Private Buckets)

-- Allow authenticated users to view objects in private buckets
create policy "Authenticated users can view private files"
  on storage.objects for select
  using (
    bucket_id in ('cad-files', 'pcb-files', 'simulation-files', 'research-files', 'documents', 'telemetry') 
    and auth.role() = 'authenticated'
  );

-- Allow authenticated users to insert objects
create policy "Authenticated users can upload files"
  on storage.objects for insert
  with check (
    bucket_id in ('cad-files', 'pcb-files', 'simulation-files', 'research-files', 'documents', 'telemetry') 
    and auth.role() = 'authenticated'
  );

-- Allow users to update their own objects
create policy "Users can update their own files"
  on storage.objects for update
  using (
    bucket_id in ('cad-files', 'pcb-files', 'simulation-files', 'research-files', 'documents', 'telemetry') 
    and auth.uid() = owner
  );

-- Allow users to delete their own objects
create policy "Users can delete their own files"
  on storage.objects for delete
  using (
    bucket_id in ('cad-files', 'pcb-files', 'simulation-files', 'research-files', 'documents', 'telemetry') 
    and auth.uid() = owner
  );

-- 3. Storage Policies for Public Buckets ('reports')

create policy "Public Reports are viewable by everyone"
  on storage.objects for select
  using (bucket_id = 'reports');

create policy "Authenticated users can upload reports"
  on storage.objects for insert
  with check (bucket_id = 'reports' and auth.role() = 'authenticated');

create policy "Users can update their own reports"
  on storage.objects for update
  using (bucket_id = 'reports' and auth.uid() = owner);

create policy "Users can delete their own reports"
  on storage.objects for delete
  using (bucket_id = 'reports' and auth.uid() = owner);
