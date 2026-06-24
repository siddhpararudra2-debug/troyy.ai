-- Enable required extensions
create extension if not exists "uuid-ossp";
create extension if not exists "vector" with schema public;

-- Example Base Schema for the Engineering OS

-- 1. Users Profile (Extends Supabase Auth)
create table public.profiles (
  id uuid references auth.users on delete cascade not null primary key,
  email text unique not null,
  full_name text,
  role text default 'engineer' check (role in ('admin', 'engineer', 'viewer')),
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Enable RLS
alter table public.profiles enable row level security;

-- Profiles Policies
create policy "Public profiles are viewable by everyone." 
  on profiles for select using (true);

create policy "Users can insert their own profile." 
  on profiles for insert with check (auth.uid() = id);

create policy "Users can update own profile." 
  on profiles for update using (auth.uid() = id);

-- 2. Projects
create table public.projects (
  id uuid default uuid_generate_v4() primary key,
  name text not null,
  description text,
  status text default 'active',
  created_by uuid references public.profiles(id) not null,
  created_at timestamp with time zone default timezone('utc'::text, now()) not null,
  updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

alter table public.projects enable row level security;

create policy "Projects viewable by authenticated users." 
  on projects for select using (auth.role() = 'authenticated');

create policy "Projects insertable by authenticated users." 
  on projects for insert with check (auth.role() = 'authenticated');

create policy "Projects updateable by creator or admin." 
  on projects for update using (
    auth.uid() = created_by or 
    exists (select 1 from public.profiles where id = auth.uid() and role = 'admin')
  );

-- Function to handle new user creation
create or function public.handle_new_user() 
returns trigger as $$
begin
  insert into public.profiles (id, email, full_name)
  values (new.id, new.email, new.raw_user_meta_data->>'full_name');
  return new;
end;
$$ language plpgsql security definer;

-- Trigger for new user
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();
