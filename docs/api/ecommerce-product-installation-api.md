# 🛒 **E-Commerce Product + Installation API Documentation**

## **Overview**
The Hero365 e-commerce system enables customers to browse products (HVAC units, water heaters, electrical equipment) with professional installation services, view pricing with membership discounts, and add items to shopping carts.

---

## 🎯 **Key Features**

### **1. Product Catalog System**
- **Products** with detailed specifications, images, and descriptions
- **Installation Options** with different complexity levels and pricing
- **Membership Pricing** with automatic discounts for different tiers
- **Categories** for organizing products (HVAC, Electrical, Plumbing)
- **Search & Filtering** by category, featured status, and keywords

### **2. Advanced Pricing Engine**
- **Combined Pricing**: Product price + Installation price
- **Membership Discounts**: Residential (10-15%), Commercial (15-20%), Premium (20-25%)
- **Bundle Savings**: Additional discounts for product + installation packages
- **Complex Calculations**: Volume discounts, complexity multipliers, tax calculations
- **Display Logic**: "from $X", "Quote Required", exact pricing based on complexity

### **3. Database Schema**
```sql
-- Core tables created:
- products (extended with e-commerce fields)
- product_categories (hierarchical organization)  
- product_installation_options (links products to installation services)
- shopping_carts (session-based cart management)
- cart_items (detailed cart entries with pricing snapshots)
- product_variants (for products with size/color options)
```

---

## 📋 **API Endpoints**

### **Product Catalog Endpoints**

#### **GET** `/api/v1/public/professional/product-catalog/{business_id}`
**Get product catalog with installation options**

**Query Parameters:**
- `category` (optional): Filter by category name
- `search` (optional): Search products by name/description  
- `featured_only` (optional): Show only featured products
- `limit` (default: 50): Maximum products to return
- `offset` (default: 0): Pagination offset

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "Carrier 3-Ton 16 SEER Heat Pump System",
    "sku": "HP-3TON-SEER16", 
    "description": "Energy-efficient heat pump system...",
    "unit_price": 4500.00,
    "category_name": "HVAC Equipment",
    "requires_professional_install": true,
    "install_complexity": "complex",
    "warranty_years": 10,
    "energy_efficiency_rating": "16 SEER",
    "featured_image_url": "https://...",
    "gallery_images": ["https://..."],
    "product_highlights": ["16 SEER Rating", "10-Year Warranty"],
    "technical_specs": {
      "cooling_capacity": "36000 BTU",
      "electrical": "240V"
    },
    "installation_options": [
      {
        "id": "uuid",
        "option_name": "Standard Heat Pump Installation",
        "description": "Complete installation including...",
        "base_install_price": 1200.00,
        "residential_install_price": 1020.00,
        "commercial_install_price": 960.00,
        "premium_install_price": 900.00,
        "estimated_duration_hours": 6.0,
        "is_default": true,
        "requirements": {
          "electrical_service": "240V/60A circuit",
          "permits": "mechanical permit required"
        },
        "included_in_install": [
          "Electrical connections",
          "Refrigerant lines",
          "System startup"
        ]
      }
    ]
  }
]
```

#### **GET** `/api/v1/public/professional/product-categories/{business_id}`
**Get product categories with counts**

**Response:**
```json
[
  {
    "id": "uuid",
    "name": "HVAC Equipment",
    "description": "Heating, ventilation, and air conditioning equipment",
    "product_count": 15,
    "sort_order": 1
  }
]
```

#### **GET** `/api/v1/public/professional/product/{business_id}/{product_id}`
**Get detailed product information**

**Response:** Same as catalog item but with full details.

---

### **Pricing Calculation Endpoint**

#### **POST** `/api/v1/public/professional/product-pricing/{business_id}/{product_id}`
**Calculate detailed pricing for product + installation**

**Query Parameters:**
- `installation_option_id` (optional): Specific installation option
- `quantity` (default: 1): Number of units
- `membership_type` (optional): "residential", "commercial", or "premium"

**Response:**
```json
{
  "product_unit_price": 4500.00,
  "installation_base_price": 1200.00,
  "quantity": 1,
  "product_subtotal": 4500.00,
  "installation_subtotal": 1200.00,
  "subtotal_before_discounts": 5700.00,
  "membership_type": "residential",
  "product_discount_amount": 450.00,
  "installation_discount_amount": 180.00,
  "total_discount_amount": 630.00,
  "bundle_savings": 285.00,
  "subtotal_after_discounts": 4785.00,
  "tax_rate": 0.0825,
  "tax_amount": 394.76,
  "total_amount": 5179.76,
  "total_savings": 915.00,
  "savings_percentage": 16.1,
  "formatted_display_price": "$5,180",
  "price_display_type": "fixed"
}
```

---

## 🎨 **Frontend Integration**

### **Sample Implementation**

```typescript
// Product listing with installation pricing
import { ProductCatalogItem, PricingBreakdown } from './api/types';

function ProductCard({ product }: { product: ProductCatalogItem }) {
  const [pricing, setPricing] = useState<PricingBreakdown | null>(null);
  const [membershipType, setMembershipType] = useState('residential');

  useEffect(() => {
    // Calculate pricing with membership
    fetchProductPricing(product.id, membershipType).then(setPricing);
  }, [product.id, membershipType]);

  return (
    <div className="product-card">
      <img src={product.featured_image_url} alt={product.name} />
      <h3>{product.name}</h3>
      <div className="pricing">
        {pricing && (
          <>
            <div className="price-display">
              <span className="current-price">{pricing.formatted_display_price}</span>
              {pricing.total_savings > 0 && (
                <span className="original-price">${pricing.subtotal_before_discounts}</span>
              )}
            </div>
            <div className="savings">
              Save ${pricing.total_savings} ({pricing.savings_percentage}%)
            </div>
            <div className="breakdown">
              <div>Product: ${pricing.product_subtotal - pricing.product_discount_amount}</div>
              <div>Installation: ${pricing.installation_subtotal - pricing.installation_discount_amount}</div>
              {pricing.bundle_savings > 0 && (
                <div>Bundle Discount: -${pricing.bundle_savings}</div>
              )}
            </div>
          </>
        )}
      </div>
      
      <div className="installation-options">
        {product.installation_options.map(option => (
          <div key={option.id} className="install-option">
            <h4>{option.option_name}</h4>
            <p>{option.description}</p>
            <div className="duration">Est. {option.estimated_duration_hours} hours</div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## 🔧 **Development Status**

### **✅ Completed**
- [x] Database schema for products + installation system
- [x] Advanced pricing engine with membership discounts
- [x] Product catalog API endpoints
- [x] Installation options with complexity pricing
- [x] Shopping cart schema (ready for implementation)
- [x] Sample data seeding (6 products with installation options)

### **🚧 In Progress**
- [ ] Shopping cart CRUD APIs
- [ ] Checkout flow integration with estimates
- [ ] Frontend product catalog pages
- [ ] Cart and checkout UI components

### **📦 Sample Products Available**
1. **Carrier 3-Ton Heat Pump** - $4,500 + installation from $900-$1,200
2. **Trane Gas Furnace** - $2,800 + installation
3. **AO Smith Water Heaters** (40 & 50 gal) - $850-$950 + installation
4. **Square D Electrical Panel** - $320 + installation from $600-$800
5. **Tesla EV Charger** - $475 + installation from $263-$550

---

## 🎯 **Next Implementation Steps**

### **Phase 1: Shopping Cart APIs** (2-3 days)
```typescript
POST /api/v1/public/cart                    // Create cart
POST /api/v1/public/cart/{id}/items         // Add items
PUT  /api/v1/public/cart/{id}/items/{id}    // Update quantities
GET  /api/v1/public/cart/{id}               // Get cart with totals
```

### **Phase 2: Frontend Product Pages** (3-4 days)
- Product listing page with category filters
- Product detail page with installation options
- Live pricing calculator with membership toggles
- Add to cart functionality

### **Phase 3: Cart & Checkout** (3-4 days)
- Shopping cart UI with pricing breakdown
- Checkout flow with installation scheduling
- Integration with existing estimate/invoice system

---

## 🔍 **Testing the Implementation**

### **API Testing Commands**
```bash
# Test product catalog
curl "http://127.0.0.1:8000/api/v1/public/professional/product-catalog/a1b2c3d4-e5f6-7890-1234-567890abcdef"

# Test pricing calculation
curl "http://127.0.0.1:8000/api/v1/public/professional/product-pricing/a1b2c3d4-e5f6-7890-1234-567890abcdef/[product-id]?membership_type=residential&quantity=1"

# Test categories
curl "http://127.0.0.1:8000/api/v1/public/professional/product-categories/a1b2c3d4-e5f6-7890-1234-567890abcdef"
```

---

## 💡 **Advanced Features Ready for Implementation**

### **Dynamic Pricing Rules**
- Volume discounts for bulk purchases
- Seasonal pricing adjustments
- Location-based pricing variations
- Time-sensitive promotional pricing

### **Product Variations**
- Size/capacity options (different BTU ratings, gallon sizes)
- Color/finish selections
- Model upgrades with price adjustments
- Accessory bundles

### **Smart Recommendations**
- "Customers who bought this also bought..."
- Size/capacity recommendations based on property details
- Energy efficiency upgrade suggestions
- Maintenance plan upsells

---

This e-commerce system provides a solid foundation for selling products with professional installation services, offering transparent pricing, membership benefits, and seamless integration with the existing Hero365 platform.
