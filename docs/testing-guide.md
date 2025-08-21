# Hero365 Website Builder - Testing Guide

## 🚀 **How to Test the SEO Website Builder**

This guide provides multiple ways to test the Hero365 Website Builder system, from quick demos to comprehensive testing.

---

## **🎯 Quick Start - Test in 3 Ways**

### **1. 🌐 Web Dashboard (Easiest)**
Access the visual testing interface:

```
http://localhost:8000/test-dashboard/
```

**Features:**
- ✅ Visual form interface
- ✅ Real-time deployment status  
- ✅ Instant preview links
- ✅ Recent tests history
- ✅ One-click testing for all trades

### **2. 📱 Simple Demo Page (Public)**
For quick demos without authentication:

```
http://localhost:8000/test-dashboard/simple
```

**Perfect for:**
- ✅ Client demonstrations
- ✅ Public testing
- ✅ Marketing purposes
- ✅ Quick proof-of-concept

### **3. 💻 Command Line (Advanced)**
For developers and detailed testing:

```bash
cd backend
python scripts/run_website_tests.py quick-demo
```

---

## **🧪 Testing Methods**

### **Method 1: Quick Single Website Test**

#### **Via Web Dashboard:**
1. Go to `http://localhost:8000/test-dashboard/`
2. Select trade type (e.g., "Plumbing")
3. Enter business name (e.g., "QuickFix Plumbing")
4. Enter location (e.g., "New York")
5. Click "Create & Deploy Website"
6. Wait 30-60 seconds
7. Click preview link to see your website!

#### **Via CLI:**
```bash
# Test specific trade
python scripts/run_website_tests.py quick-test --trade plumbing --name "QuickFix Plumbing"

# Test with custom location
python scripts/run_website_tests.py quick-test --trade hvac --name "ComfortZone HVAC" --location "Los Angeles"

# Deploy to custom subdomain
python scripts/run_website_tests.py deploy-subdomain --trade electrical --name "PowerPro Electric" --subdomain "my-test-site"
```

#### **Via API:**
```bash
curl -X POST "http://localhost:8000/api/testing/quick-test" \
  -H "Content-Type: application/json" \
  -d '{
    "trade_type": "plumbing",
    "trade_category": "residential", 
    "business_name": "QuickFix Plumbing",
    "location": "New York"
  }'
```

### **Method 2: Test All 20 Trades**

#### **Via Web Dashboard:**
1. Go to `http://localhost:8000/test-dashboard/`
2. Scroll to "Comprehensive Testing" section
3. Click "Test All 20 Trades"
4. Wait 5-10 minutes for completion
5. View success rates and performance metrics

#### **Via CLI:**
```bash
# Test all trades comprehensively
python scripts/run_website_tests.py test-all-trades

# Quick demo with 3 sample trades
python scripts/run_website_tests.py quick-demo
```

### **Method 3: Performance Testing**

#### **Test Website Performance:**
```bash
# Test performance of deployed subdomain
python scripts/run_website_tests.py performance-test --subdomain my-test-site
```

#### **Via API:**
```bash
curl -X POST "http://localhost:8000/api/testing/performance/my-test-site"
```

---

## **🌐 Subdomain Deployment**

### **Automatic Subdomain Creation**
Every test automatically creates a subdomain like:
- `https://plumbing-abc123.hero365.ai`
- `https://hvac-def456.hero365.ai`
- `https://electrical-ghi789.hero365.ai`

### **Custom Subdomains**
```bash
# Deploy with custom subdomain
python scripts/run_website_tests.py deploy-subdomain \
  --trade plumbing \
  --name "My Test Business" \
  --subdomain "my-custom-name"
```

### **Manage Subdomains**
```bash
# List all active subdomains
python scripts/run_website_tests.py list-deployments

# Clean up old deployments
python scripts/run_website_tests.py cleanup-tests
```

---

## **📊 What Gets Tested**

### **✅ Website Generation**
- ✅ **Template Selection** - Correct template for trade type
- ✅ **AI Content Generation** - Trade-specific content creation
- ✅ **SEO Optimization** - Meta tags, keywords, schema markup
- ✅ **Mobile Responsiveness** - Perfect display on all devices
- ✅ **Performance** - Fast loading times (target: <2s)

### **✅ Lead Capture System**
- ✅ **Contact Forms** - Working form submissions
- ✅ **Booking Widgets** - Direct appointment scheduling
- ✅ **Emergency Banners** - Priority lead routing
- ✅ **Call-to-Actions** - Strategic conversion points

### **✅ Technical Features**
- ✅ **SSL Certificates** - Secure HTTPS connections
- ✅ **CDN Delivery** - Global content distribution
- ✅ **SEO Structure** - Proper HTML structure and meta data
- ✅ **Schema Markup** - Rich snippets for search engines

### **✅ Performance Metrics**
- ✅ **Lighthouse Score** - Target: 90+ overall
- ✅ **Build Time** - Target: <60 seconds
- ✅ **Page Load Speed** - Target: <2 seconds
- ✅ **Mobile Score** - Target: 95+

---

## **🎯 Expected Results**

### **Successful Test Output:**
```
✅ SUCCESS!
   Preview URL: https://plumbing-abc123.hero365.ai
   Build Time: 45.2s
   Lighthouse Score: 92
   Pages Generated: 5
   Features: Hero, Services, Contact Form, Booking, Emergency Banner
```

### **Website Features You'll See:**
1. **🏠 Professional Homepage** - Hero section with business info
2. **📋 Services Page** - Trade-specific service listings
3. **📞 Contact Forms** - Lead capture with validation
4. **📅 Booking Widget** - Direct appointment scheduling
5. **🚨 Emergency Banner** - Priority contact for urgent needs
6. **📱 Mobile Optimization** - Perfect mobile experience
7. **🔍 SEO Ready** - Optimized for search engines

---

## **🔧 Troubleshooting**

### **Common Issues:**

#### **"Template not found" Error:**
```bash
# Validate all templates first
python scripts/run_website_tests.py validate-templates
```

#### **Slow Build Times:**
- Expected: 30-60 seconds for first build
- Subsequent builds: 15-30 seconds
- Check internet connection for AI content generation

#### **Subdomain Not Accessible:**
- DNS propagation can take 1-5 minutes
- Try accessing after a few minutes
- Check CloudFront cache invalidation

#### **API Authentication Errors:**
```bash
# For authenticated endpoints, ensure you're logged in
# Use the simple demo page for public testing
```

### **Debug Mode:**
```bash
# Run with verbose logging
PYTHONPATH=. python -m scripts.run_website_tests quick-test --trade plumbing
```

---

## **📈 Performance Benchmarks**

### **Target Metrics:**
- ✅ **Build Time:** <60 seconds
- ✅ **Lighthouse Score:** 90+
- ✅ **Page Load:** <2 seconds  
- ✅ **Mobile Score:** 95+
- ✅ **SEO Score:** 85+
- ✅ **Accessibility:** 90+

### **Trade-Specific Features:**

#### **Residential Trades:**
- ✅ Emergency service banners
- ✅ Direct booking widgets
- ✅ Homeowner-focused content
- ✅ Local SEO optimization

#### **Commercial Trades:**
- ✅ B2B focused messaging
- ✅ Quote request forms
- ✅ Commercial service areas
- ✅ Industry-specific keywords

---

## **🚀 Next Steps After Testing**

### **1. Review Generated Websites**
- Check content quality and accuracy
- Verify contact forms work
- Test mobile responsiveness
- Validate SEO elements

### **2. Customize Templates**
- Modify colors and branding
- Add business-specific content
- Adjust service offerings
- Update contact information

### **3. Deploy to Production**
- Register custom domain
- Configure business branding
- Set up lead routing
- Enable analytics tracking

### **4. Monitor Performance**
- Track conversion rates
- Monitor page speed
- Check search rankings
- Analyze user behavior

---

## **💡 Pro Tips**

### **For Best Results:**
1. **Use Real Business Names** - More realistic content generation
2. **Test Multiple Locations** - See local SEO variations
3. **Try Different Trades** - Compare template quality
4. **Check Mobile First** - Most traffic is mobile
5. **Test Forms** - Ensure lead capture works

### **For Demonstrations:**
1. **Use the Simple Demo Page** - No authentication needed
2. **Prepare Multiple Examples** - Show different trades
3. **Highlight Speed** - 30-60 second generation
4. **Show Mobile Version** - Responsive design
5. **Demonstrate Features** - Forms, booking, emergency

---

## **📞 Support**

### **Need Help?**
- 📧 **Email:** support@hero365.ai
- 💬 **Chat:** Available in dashboard
- 📚 **Docs:** Full documentation available
- 🐛 **Issues:** Report bugs via GitHub

### **Feature Requests:**
- New trade templates
- Additional customization options
- Integration requests
- Performance improvements

---

**🎉 Ready to test? Start with the web dashboard at `http://localhost:8000/test-dashboard/` for the easiest experience!**
