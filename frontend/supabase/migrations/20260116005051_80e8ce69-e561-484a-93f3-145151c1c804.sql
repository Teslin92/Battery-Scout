-- Create subscribers table for newsletter signups
CREATE TABLE public.subscribers (
    id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    frequency TEXT NOT NULL DEFAULT 'daily' CHECK (frequency IN ('daily', 'weekly')),
    categories TEXT[] NOT NULL DEFAULT '{}',
    subscribed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    is_active BOOLEAN NOT NULL DEFAULT true
);

-- Create articles table for sample previews
CREATE TABLE public.articles (
    id UUID NOT NULL DEFAULT gen_random_uuid() PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT,
    summary TEXT NOT NULL,
    category TEXT NOT NULL,
    source_country TEXT NOT NULL,
    source_name TEXT NOT NULL,
    publish_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);

-- Enable RLS on both tables
ALTER TABLE public.subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.articles ENABLE ROW LEVEL SECURITY;

-- Articles are publicly readable (for the preview section)
CREATE POLICY "Anyone can view articles"
ON public.articles
FOR SELECT
USING (true);

-- Allow anonymous inserts to subscribers (for signups)
CREATE POLICY "Anyone can subscribe"
ON public.subscribers
FOR INSERT
WITH CHECK (true);

-- Insert sample articles for the preview
INSERT INTO public.articles (title, url, summary, category, source_country, source_name, publish_date)
VALUES 
    ('CATL Unveils Next-Generation Sodium-Ion Battery for Grid Storage', 'https://example.com/catl', 'Chinese battery giant CATL has announced a breakthrough sodium-ion battery designed for large-scale energy storage. The new cell offers 160 Wh/kg density and addresses lithium supply chain concerns for stationary applications.', 'Technology & Innovation', '🇨🇳', 'Reuters', now() - interval '2 days'),
    ('Tesla Secures Major Lithium Supply Deal with Chilean Miner', 'https://example.com/tesla', 'Tesla has signed a multi-year agreement with SQM to secure lithium supply for its US battery manufacturing operations. The deal is valued at approximately $1.5 billion and includes sustainability requirements.', 'Supply Chain & Materials', '🇺🇸', 'Bloomberg', now() - interval '1 day'),
    ('EU Proposes Stricter Battery Recycling Targets for 2030', 'https://example.com/eu', 'The European Commission has proposed new regulations requiring 70% recycling efficiency for lithium-ion batteries by 2030. Manufacturers will be required to use minimum recycled content in new batteries.', 'Policy & Regulations', '🇪🇺', 'Financial Times', now() - interval '3 days'),
    ('Northvolt Opens Europe''s Largest Battery Recycling Facility', 'https://example.com/northvolt', 'Swedish battery maker Northvolt has opened a new recycling plant in Germany capable of processing 25,000 tonnes of battery material annually. The facility aims to recover 95% of critical metals.', 'Battery Recycling', '🇩🇪', 'Handelsblatt', now() - interval '4 days'),
    ('Toyota and Panasonic JV Announces Solid-State Battery Production Timeline', 'https://example.com/toyota', 'Prime Planet Energy & Solutions has confirmed plans to begin mass production of solid-state batteries by 2027. The technology promises doubled energy density and faster charging compared to current lithium-ion cells.', 'Industry News', '🇯🇵', 'Nikkei Asia', now()),
    ('Samsung SDI Partners with Stellantis for EV Battery Plant in Indiana', 'https://example.com/samsung', 'Samsung SDI and Stellantis have announced a $3.2 billion joint venture to build an EV battery manufacturing facility in Indiana. Production is expected to begin in 2027 with annual capacity of 33 GWh.', 'Manufacturing & Production', '🇰🇷', 'Korea Herald', now() - interval '5 days');