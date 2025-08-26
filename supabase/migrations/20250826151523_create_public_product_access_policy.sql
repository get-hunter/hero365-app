-- Create RLS policy for public access to products
-- Allow anonymous users to read products marked for website display

-- Create policy for public read access to products with show_on_website = true
CREATE POLICY "Allow public read access to website products" 
ON products 
FOR SELECT 
USING (show_on_website = true AND is_active = true);

-- Also allow public read access to product categories (needed for product catalog)
CREATE POLICY "Allow public read access to active product categories"
ON product_categories
FOR SELECT
USING (is_active = true);

-- Allow public read access to product installation options (for e-commerce)
CREATE POLICY "Allow public read access to active installation options"
ON product_installation_options  
FOR SELECT
USING (is_active = true);
