-- Add region preference boolean columns to subscribers table
-- These columns track which regions each subscriber is interested in

ALTER TABLE public.subscribers
ADD COLUMN IF NOT EXISTS pref_north_america BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN IF NOT EXISTS pref_europe BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN IF NOT EXISTS pref_asia BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN IF NOT EXISTS pref_global BOOLEAN NOT NULL DEFAULT false;

-- Set default to Global for existing subscribers who don't have regions set
UPDATE public.subscribers
SET pref_global = true
WHERE (regions IS NULL OR regions = '{}' OR array_length(regions, 1) IS NULL)
  AND pref_global = false;

-- Migrate existing region data to boolean columns
UPDATE public.subscribers
SET 
  pref_north_america = CASE WHEN 'North America' = ANY(regions) THEN true ELSE false END,
  pref_europe = CASE WHEN 'Europe' = ANY(regions) THEN true ELSE false END,
  pref_asia = CASE WHEN 'Asia' = ANY(regions) THEN true ELSE false END,
  pref_global = CASE WHEN 'Global' = ANY(regions) OR regions IS NULL OR regions = '{}' OR array_length(regions, 1) IS NULL THEN true ELSE false END
WHERE regions IS NOT NULL;
