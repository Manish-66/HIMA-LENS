-- ====================================================================
-- HIMA-LENS: Supabase Database & Storage Setup Script
-- ====================================================================
-- Instructions:
-- 1. Go to your Supabase Dashboard: https://supabase.com/dashboard
-- 2. Open your project, click on "SQL Editor" in the left sidebar
-- 3. Click "New Query", paste this entire script, and click "Run" (green button)
-- ====================================================================

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
    created_at TIMESTAMPTZ DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- 2. Enable Row Level Security (RLS)
ALTER TABLE public.community_reports ENABLE ROW LEVEL SECURITY;

-- 3. Allow anyone (public/anon) to read reports (for explore map & feeds)
DROP POLICY IF EXISTS "Allow public read access" ON public.community_reports;
CREATE POLICY "Allow public read access"
ON public.community_reports
FOR SELECT
TO public, anon, authenticated
USING (true);

-- 4. Allow anyone (public/anon) to submit a new report
DROP POLICY IF EXISTS "Allow public insert access" ON public.community_reports;
CREATE POLICY "Allow public insert access"
ON public.community_reports
FOR INSERT
TO public, anon, authenticated
WITH CHECK (true);

-- 5. Create the public Storage Bucket for landslide photos
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

-- 6. Storage Policies: Allow everyone to view photos
DROP POLICY IF EXISTS "Allow public read report images" ON storage.objects;
CREATE POLICY "Allow public read report images"
ON storage.objects
FOR SELECT
TO public, anon, authenticated
USING (bucket_id = 'report-images');

-- 7. Storage Policies: Allow anyone to upload photos
DROP POLICY IF EXISTS "Allow public upload report images" ON storage.objects;
CREATE POLICY "Allow public upload report images"
ON storage.objects
FOR INSERT
TO public, anon, authenticated
WITH CHECK (bucket_id = 'report-images');

-- 8. Storage Policies: Allow overwrite/upsert if needed
DROP POLICY IF EXISTS "Allow public update report images" ON storage.objects;
CREATE POLICY "Allow public update report images"
ON storage.objects
FOR UPDATE
TO public, anon, authenticated
USING (bucket_id = 'report-images');
