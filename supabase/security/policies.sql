-- =============================================
-- Personal Engineering OS - RLS Policies
-- Single User Access (Supabase Free Tier)
-- =============================================

-- Enable RLS on all tables
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        EXECUTE 'ALTER TABLE ' || quote_ident(r.tablename) || ' ENABLE ROW LEVEL SECURITY;
    END LOOP;
END
$$ LANGUAGE plpgsql;

-- =============================================
-- Single User Policies (Allow All Access for Authenticated User)
-- =============================================

DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT tablename FROM pg_tables WHERE schemaname = 'public'
    LOOP
        -- Allow all for SELECT
        EXECUTE 'CREATE POLICY "' || r.tablename || '_select_all ON ' || quote_ident(r.tablename) || 
                ' FOR SELECT USING (auth.uid() IS NOT NULL';
        -- Allow all for INSERT
        EXECUTE 'CREATE POLICY "' || r.tablename || '_insert_all ON ' || quote_ident(r.tablename) || 
                ' FOR INSERT WITH CHECK (auth.uid() IS NOT NULL)';
        -- Allow all for UPDATE
        EXECUTE 'CREATE POLICY "' || r.tablename || '_update_all ON ' || quote_ident(r.tablename) || 
                ' FOR UPDATE USING (auth.uid() IS NOT NULL)';
        -- Allow all for DELETE
        EXECUTE 'CREATE POLICY "' || r.tablename || '_delete_all ON ' || quote_ident(r.tablename) || 
                ' FOR DELETE USING (auth.uid() IS NOT NULL)';
    END LOOP;
END
$$ LANGUAGE plpgsql;
