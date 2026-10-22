-- ====================================================================
-- HIMA-LENS: Supabase Database & Storage Setup Script
-- ====================================================================
-- Instructions:
-- 1. Go to your Supabase Dashboard: https://supabase.com/dashboard
-- 2. Open your project, click on "SQL Editor" in the left sidebar
-- 3. Click "New Query", paste this entire script, and click "Run" (green button)
-- ====================================================================

-- 0. Enable PostGIS Extension (for spatial indexing & geospatial analysis)
CREATE EXTENSION IF NOT EXISTS postgis;

-- 1. Create the Community Landslide Reports table
CREATE TABLE IF NOT EXISTS public.community_reports (
    id TEXT PRIMARY KEY,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    district TEXT DEFAULT 'Unknown',
    incident_date TEXT,
    movement_type TEXT DEFAULT 'Unknown',
    severity TEXT DEFAULT 'Moderate',
    description TEXT,
    reporter_name TEXT DEFAULT 'Anonymous',
    photo_url TEXT,
    status TEXT DEFAULT 'active',
    is_hidden BOOLEAN DEFAULT false,
    ai_assessment JSONB,
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Migration safety for existing installations
ALTER TABLE public.community_reports ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'active';
ALTER TABLE public.community_reports ADD COLUMN IF NOT EXISTS is_hidden BOOLEAN DEFAULT false;
ALTER TABLE public.community_reports ADD COLUMN IF NOT EXISTS ai_assessment JSONB;

-- 2. Generated PostGIS Geometry column for fast spatial indexing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
          AND table_name = 'community_reports' 
          AND column_name = 'geom'
    ) THEN
        ALTER TABLE public.community_reports 
        ADD COLUMN geom geometry(Point, 4326) 
        GENERATED ALWAYS AS (ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)) STORED;
    END IF;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Skipping geom generation: %', SQLERRM;
END $$;

-- 3. Performance & Spatial Indexes
CREATE INDEX IF NOT EXISTS idx_community_reports_created_at ON public.community_reports (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_community_reports_status ON public.community_reports (status);
DO $$
BEGIN
    CREATE INDEX IF NOT EXISTS idx_community_reports_geom ON public.community_reports USING GIST(geom);
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Skipping GIST index creation: %', SQLERRM;
END $$;

-- 4. Enable Row Level Security (RLS)
ALTER TABLE public.community_reports ENABLE ROW LEVEL SECURITY;

-- 5. Allow anyone (public/anon) to read reports (for explore map & feeds)
DROP POLICY IF EXISTS "Allow public read access" ON public.community_reports;
CREATE POLICY "Allow public read access"
ON public.community_reports
FOR SELECT
TO public, anon, authenticated
USING (true);

-- 6. Allow anyone (public/anon) to submit a new report
DROP POLICY IF EXISTS "Allow public insert access" ON public.community_reports;
CREATE POLICY "Allow public insert access"
ON public.community_reports
FOR INSERT
TO public, anon, authenticated
WITH CHECK (true);

-- 7. Allow report updates (for persisting AI assessment dossiers & BOQ estimates)
DROP POLICY IF EXISTS "Allow public update access" ON public.community_reports;
CREATE POLICY "Allow public update access"
ON public.community_reports
FOR UPDATE
TO public, anon, authenticated
USING (true)
WITH CHECK (true);

-- 8. Create the public Storage Bucket for landslide photos
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
    'report-images',
    'report-images',
    true,
    16777216, -- 16 MB max file size
    ARRAY['image/jpeg', 'image/png', 'image/webp', 'image/gif']
)
ON CONFLICT (id) DO UPDATE 
SET public = true,
    file_size_limit = 16777216;

-- 9. Storage Policies: Allow everyone to view photos
DROP POLICY IF EXISTS "Allow public read report images" ON storage.objects;
CREATE POLICY "Allow public read report images"
ON storage.objects
FOR SELECT
TO public, anon, authenticated
USING (bucket_id = 'report-images');

-- 10. Storage Policies: Allow anyone to upload photos
DROP POLICY IF EXISTS "Allow public upload report images" ON storage.objects;
CREATE POLICY "Allow public upload report images"
ON storage.objects
FOR INSERT
TO public, anon, authenticated
WITH CHECK (bucket_id = 'report-images');

-- 11. Security Hardening: Ensure photo evidence is immutable (write-once)
-- Overwrite policy is intentionally dropped so uploaded photographic evidence cannot be replaced or deleted by third parties.
DROP POLICY IF EXISTS "Allow public update report images" ON storage.objects;

-- 12. (Optional) Seed existing initial community reports
INSERT INTO public.community_reports (id, latitude, longitude, district, incident_date, movement_type, severity, description, reporter_name, photo_url, status, is_hidden, created_at)
VALUES 
    ('HL-CR-6C5DBB52', 31.77271, 76.98416, 'Mandi', '2026-09-17T17:14', 'Creep / Subsidence', 'Low', 'Observed minor road edge subsidence.', 'Community Reporter', '', 'active', false, '2026-09-17 11:46:00+00'),
    ('HL-CR-B0B0D035', 31.77271, 76.98416, 'Mandi', '2026-09-17T17:13', 'Slide', 'Moderate', 'Debris sliding onto slope shoulder.', 'Community Reporter', '', 'active', false, '2026-09-17 11:44:40+00')
ON CONFLICT (id) DO NOTHING;
