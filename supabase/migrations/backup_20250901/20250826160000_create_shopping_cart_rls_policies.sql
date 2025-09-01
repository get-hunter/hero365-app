-- Create RLS policies for shopping carts and cart items
-- Allow public access to shopping cart functionality

-- Shopping carts policies
CREATE POLICY "Allow public cart creation" ON shopping_carts
FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public cart access" ON shopping_carts
FOR ALL USING (true);

-- Cart items policies  
CREATE POLICY "Allow public cart item creation" ON cart_items
FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public cart item access" ON cart_items
FOR ALL USING (true);

-- Enable RLS if not already enabled
ALTER TABLE shopping_carts ENABLE ROW LEVEL SECURITY;
ALTER TABLE cart_items ENABLE ROW LEVEL SECURITY;
