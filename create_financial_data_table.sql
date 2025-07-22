-- Create the financial_data table for SHAED Financial Model
-- Run this in your Supabase SQL Editor

CREATE TABLE financial_data (
    id BIGSERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Disable Row Level Security to avoid permission issues
ALTER TABLE financial_data DISABLE ROW LEVEL SECURITY;

-- Optional: Create an index on the updated_at column for better performance
CREATE INDEX idx_financial_data_updated_at ON financial_data (updated_at DESC);

-- Verify the table was created successfully
SELECT 
    table_name, 
    column_name, 
    data_type, 
    is_nullable, 
    column_default
FROM information_schema.columns 
WHERE table_name = 'financial_data' 
ORDER BY ordinal_position; 