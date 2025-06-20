-- Supabase Database Schema for Hero365 App
-- This file documents the required database schema for the application
-- Run these commands in your Supabase SQL editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50) UNIQUE,
    full_name VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    supabase_id UUID UNIQUE, -- Reference to Supabase Auth user
    hashed_password VARCHAR(255), -- For local auth (optional)
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Items table
CREATE TABLE IF NOT EXISTS items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_deleted BOOLEAN DEFAULT false,
    deleted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_supabase_id ON users(supabase_id);
CREATE INDEX IF NOT EXISTS idx_users_active ON users(is_active);

CREATE INDEX IF NOT EXISTS idx_items_owner_id ON items(owner_id);
CREATE INDEX IF NOT EXISTS idx_items_deleted ON items(is_deleted);
CREATE INDEX IF NOT EXISTS idx_items_title ON items(title);
CREATE INDEX IF NOT EXISTS idx_items_created_at ON items(created_at);

-- Row Level Security (RLS) Policies
-- Enable RLS on all tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;

-- Users table policies
-- Users can read their own profile
CREATE POLICY "Users can view own profile" ON users
    FOR SELECT USING (auth.uid()::text = supabase_id::text);

-- Users can update their own profile
CREATE POLICY "Users can update own profile" ON users
    FOR UPDATE USING (auth.uid()::text = supabase_id::text);

-- Service role can manage all users
CREATE POLICY "Service role can manage users" ON users
    FOR ALL USING (auth.role() = 'service_role');

-- Items table policies
-- Users can read their own items
CREATE POLICY "Users can view own items" ON items
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = items.owner_id 
            AND users.supabase_id::text = auth.uid()::text
        )
    );

-- Users can create items (will be owned by them)
CREATE POLICY "Users can create items" ON items
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = items.owner_id 
            AND users.supabase_id::text = auth.uid()::text
        )
    );

-- Users can update their own items
CREATE POLICY "Users can update own items" ON items
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = items.owner_id 
            AND users.supabase_id::text = auth.uid()::text
        )
    );

-- Users can delete their own items
CREATE POLICY "Users can delete own items" ON items
    FOR DELETE USING (
        EXISTS (
            SELECT 1 FROM users 
            WHERE users.id = items.owner_id 
            AND users.supabase_id::text = auth.uid()::text
        )
    );

-- Service role can manage all items
CREATE POLICY "Service role can manage items" ON items
    FOR ALL USING (auth.role() = 'service_role');

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers to automatically update updated_at
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_items_updated_at
    BEFORE UPDATE ON items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Optional: Function to soft delete items
CREATE OR REPLACE FUNCTION soft_delete_item(item_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE items 
    SET is_deleted = true, deleted_at = NOW()
    WHERE id = item_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Optional: Function to restore soft deleted items
CREATE OR REPLACE FUNCTION restore_item(item_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE items 
    SET is_deleted = false, deleted_at = NULL
    WHERE id = item_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER; 