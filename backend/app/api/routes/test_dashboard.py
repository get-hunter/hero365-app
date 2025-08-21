"""
Website Builder Test Dashboard

Simple web interface for testing the website builder system.
Provides a user-friendly way to create and test websites.
"""

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import uuid

from ..deps import get_current_user
from ...domain.entities.business import TradeCategory

router = APIRouter(prefix="/test-dashboard", tags=["test-dashboard"])

# Initialize templates (you'd need to create the templates directory)
# templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def test_dashboard(request: Request):
    """Main test dashboard page."""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hero365 Website Builder - Test Dashboard</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
    </head>
    <body class="bg-gray-100 min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <!-- Header -->
            <div class="bg-white rounded-lg shadow-md p-6 mb-8">
                <h1 class="text-3xl font-bold text-gray-900 mb-2">Hero365 Website Builder</h1>
                <p class="text-gray-600">Test Dashboard - Create and deploy websites instantly</p>
            </div>

            <!-- Quick Test Form -->
            <div class="bg-white rounded-lg shadow-md p-6 mb-8" x-data="testForm()">
                <h2 class="text-2xl font-semibold text-gray-900 mb-4">🚀 Quick Website Test</h2>
                
                <form @submit.prevent="submitTest()" class="space-y-4">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Trade Type</label>
                            <select x-model="formData.trade_type" class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                                <option value="">Select Trade</option>
                                <optgroup label="Residential">
                                    <option value="hvac">HVAC</option>
                                    <option value="plumbing">Plumbing</option>
                                    <option value="electrical">Electrical</option>
                                    <option value="chimney">Chimney</option>
                                    <option value="roofing">Roofing</option>
                                    <option value="garage_door">Garage Door</option>
                                    <option value="septic">Septic</option>
                                    <option value="pest_control">Pest Control</option>
                                    <option value="irrigation">Irrigation</option>
                                    <option value="painting">Painting</option>
                                </optgroup>
                                <optgroup label="Commercial">
                                    <option value="mechanical">Mechanical</option>
                                    <option value="refrigeration">Refrigeration</option>
                                    <option value="security_systems">Security Systems</option>
                                    <option value="landscaping">Landscaping</option>
                                    <option value="kitchen_equipment">Kitchen Equipment</option>
                                    <option value="water_treatment">Water Treatment</option>
                                    <option value="pool_spa">Pool & Spa</option>
                                </optgroup>
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Business Name</label>
                            <input type="text" x-model="formData.business_name" placeholder="e.g., QuickFix Plumbing" 
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                    </div>
                    
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Location</label>
                            <input type="text" x-model="formData.location" placeholder="e.g., New York" 
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Custom Subdomain (Optional)</label>
                            <input type="text" x-model="formData.subdomain" placeholder="e.g., my-test-site" 
                                   class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
                        </div>
                    </div>
                    
                    <button type="submit" :disabled="loading" 
                            class="bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-200">
                        <span x-show="!loading">🚀 Create & Deploy Website</span>
                        <span x-show="loading" class="flex items-center">
                            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Building Website...
                        </span>
                    </button>
                </form>
                
                <!-- Results -->
                <div x-show="result" class="mt-6 p-4 rounded-lg" :class="result?.success ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'">
                    <div x-show="result?.success">
                        <h3 class="text-lg font-semibold text-green-800 mb-2">✅ Website Created Successfully!</h3>
                        <div class="space-y-2 text-green-700">
                            <p><strong>Preview URL:</strong> <a :href="result.preview_url" target="_blank" class="text-blue-600 hover:underline" x-text="result.preview_url"></a></p>
                            <p><strong>Build Time:</strong> <span x-text="result.build_time_seconds"></span>s</p>
                            <p><strong>Lighthouse Score:</strong> <span x-text="result.lighthouse_score"></span>/100</p>
                        </div>
                        <button @click="openPreview()" class="mt-3 bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
                            🌐 Open Preview
                        </button>
                    </div>
                    
                    <div x-show="result && !result.success">
                        <h3 class="text-lg font-semibold text-red-800 mb-2">❌ Website Creation Failed</h3>
                        <p class="text-red-700" x-text="result?.error"></p>
                    </div>
                </div>
            </div>

            <!-- Recent Tests -->
            <div class="bg-white rounded-lg shadow-md p-6 mb-8" x-data="recentTests()">
                <h2 class="text-2xl font-semibold text-gray-900 mb-4">📋 Recent Test Deployments</h2>
                
                <div x-show="tests.length === 0" class="text-gray-500 text-center py-8">
                    No test deployments yet. Create your first website above!
                </div>
                
                <div x-show="tests.length > 0" class="space-y-4">
                    <template x-for="test in tests" :key="test.id">
                        <div class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                            <div class="flex justify-between items-start">
                                <div>
                                    <h3 class="font-semibold text-gray-900" x-text="test.business_name"></h3>
                                    <p class="text-sm text-gray-600" x-text="test.trade_type + ' • ' + test.location"></p>
                                    <p class="text-xs text-gray-500" x-text="'Created: ' + new Date(test.created_at).toLocaleString()"></p>
                                </div>
                                <div class="flex space-x-2">
                                    <a :href="test.preview_url" target="_blank" 
                                       class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm">
                                        View
                                    </a>
                                    <button @click="deleteTest(test.id)" 
                                            class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-sm">
                                        Delete
                                    </button>
                                </div>
                            </div>
                        </div>
                    </template>
                </div>
            </div>

            <!-- Test All Trades -->
            <div class="bg-white rounded-lg shadow-md p-6" x-data="allTradesTest()">
                <h2 class="text-2xl font-semibold text-gray-900 mb-4">🧪 Comprehensive Testing</h2>
                
                <div class="space-y-4">
                    <button @click="testAllTrades()" :disabled="testing" 
                            class="bg-purple-600 hover:bg-purple-700 disabled:bg-purple-400 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-200">
                        <span x-show="!testing">🧪 Test All 20 Trades</span>
                        <span x-show="testing">Testing in progress...</span>
                    </button>
                    
                    <div x-show="testResults" class="mt-4 p-4 bg-gray-50 rounded-lg">
                        <h3 class="font-semibold mb-2">Test Results:</h3>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                            <div>
                                <span class="font-medium">Success Rate:</span>
                                <span x-text="testResults?.success_rate + '%'"></span>
                            </div>
                            <div>
                                <span class="font-medium">Avg Build Time:</span>
                                <span x-text="testResults?.avg_build_time + 's'"></span>
                            </div>
                            <div>
                                <span class="font-medium">Avg Lighthouse:</span>
                                <span x-text="testResults?.avg_lighthouse_score"></span>
                            </div>
                            <div>
                                <span class="font-medium">Total Tests:</span>
                                <span x-text="testResults?.total_trades"></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function testForm() {
                return {
                    loading: false,
                    result: null,
                    formData: {
                        trade_type: 'plumbing',
                        business_name: 'QuickFix Plumbing',
                        location: 'New York',
                        subdomain: ''
                    },
                    
                    async submitTest() {
                        this.loading = true;
                        this.result = null;
                        
                        try {
                            // Determine trade category
                            const commercialTrades = ['mechanical', 'refrigeration', 'security_systems', 'landscaping', 'kitchen_equipment', 'water_treatment', 'pool_spa'];
                            const trade_category = commercialTrades.includes(this.formData.trade_type) ? 'commercial' : 'residential';
                            
                            const response = await fetch('/api/testing/quick-test', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    ...this.formData,
                                    trade_category
                                })
                            });
                            
                            this.result = await response.json();
                            
                            // Save to recent tests
                            if (this.result.success) {
                                this.saveToRecentTests();
                            }
                        } catch (error) {
                            this.result = {
                                success: false,
                                error: 'Network error: ' + error.message
                            };
                        } finally {
                            this.loading = false;
                        }
                    },
                    
                    openPreview() {
                        if (this.result?.preview_url) {
                            window.open(this.result.preview_url, '_blank');
                        }
                    },
                    
                    saveToRecentTests() {
                        const tests = JSON.parse(localStorage.getItem('hero365_tests') || '[]');
                        tests.unshift({
                            id: this.result.test_id,
                            ...this.formData,
                            preview_url: this.result.preview_url,
                            created_at: new Date().toISOString()
                        });
                        
                        // Keep only last 10 tests
                        tests.splice(10);
                        localStorage.setItem('hero365_tests', JSON.stringify(tests));
                        
                        // Trigger update in recent tests component
                        window.dispatchEvent(new CustomEvent('testsUpdated'));
                    }
                }
            }
            
            function recentTests() {
                return {
                    tests: [],
                    
                    init() {
                        this.loadTests();
                        window.addEventListener('testsUpdated', () => this.loadTests());
                    },
                    
                    loadTests() {
                        this.tests = JSON.parse(localStorage.getItem('hero365_tests') || '[]');
                    },
                    
                    deleteTest(testId) {
                        this.tests = this.tests.filter(test => test.id !== testId);
                        localStorage.setItem('hero365_tests', JSON.stringify(this.tests));
                    }
                }
            }
            
            function allTradesTest() {
                return {
                    testing: false,
                    testResults: null,
                    
                    async testAllTrades() {
                        this.testing = true;
                        this.testResults = null;
                        
                        try {
                            const response = await fetch('/api/testing/test-all-trades', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json',
                                }
                            });
                            
                            const result = await response.json();
                            
                            if (result.success) {
                                // Poll for results
                                await this.pollTestResults(result.test_batch_id);
                            }
                        } catch (error) {
                            alert('Error starting comprehensive test: ' + error.message);
                        } finally {
                            this.testing = false;
                        }
                    },
                    
                    async pollTestResults(batchId) {
                        // Poll every 30 seconds for results
                        const pollInterval = setInterval(async () => {
                            try {
                                const response = await fetch(`/api/testing/batch/${batchId}`);
                                const result = await response.json();
                                
                                if (result.status === 'completed') {
                                    this.testResults = result.results;
                                    clearInterval(pollInterval);
                                    this.testing = false;
                                }
                            } catch (error) {
                                console.error('Polling error:', error);
                            }
                        }, 30000);
                        
                        // Stop polling after 10 minutes
                        setTimeout(() => {
                            clearInterval(pollInterval);
                            this.testing = false;
                        }, 600000);
                    }
                }
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/simple", response_class=HTMLResponse)
async def simple_test_page():
    """Simple test page without authentication."""
    
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Hero365 - Simple Website Test</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <div class="max-w-2xl mx-auto">
                <!-- Header -->
                <div class="text-center mb-8">
                    <h1 class="text-4xl font-bold text-gray-900 mb-2">Hero365 Website Builder</h1>
                    <p class="text-xl text-gray-600">Create professional websites in seconds</p>
                </div>

                <!-- Demo Form -->
                <div class="bg-white rounded-xl shadow-lg p-8">
                    <h2 class="text-2xl font-semibold text-gray-900 mb-6">🚀 Try It Now - Free Demo</h2>
                    
                    <form id="demoForm" class="space-y-6">
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">What's your trade?</label>
                            <select id="tradeType" class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                                <option value="plumbing">🔧 Plumbing</option>
                                <option value="hvac">❄️ HVAC</option>
                                <option value="electrical">⚡ Electrical</option>
                                <option value="roofing">🏠 Roofing</option>
                                <option value="landscaping">🌿 Landscaping</option>
                                <option value="pest_control">🐛 Pest Control</option>
                                <option value="painting">🎨 Painting</option>
                                <option value="garage_door">🚪 Garage Door</option>
                            </select>
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Business Name</label>
                            <input type="text" id="businessName" placeholder="e.g., QuickFix Plumbing" 
                                   class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                        </div>
                        
                        <div>
                            <label class="block text-sm font-medium text-gray-700 mb-2">Your City</label>
                            <input type="text" id="location" placeholder="e.g., New York" 
                                   class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                        </div>
                        
                        <button type="submit" id="createBtn" 
                                class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-bold py-4 px-6 rounded-lg text-lg transition-all duration-200 transform hover:scale-105">
                            ✨ Create My Website Now
                        </button>
                    </form>
                    
                    <!-- Loading State -->
                    <div id="loadingState" class="hidden text-center py-8">
                        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                        <p class="mt-4 text-gray-600">Building your professional website...</p>
                        <p class="text-sm text-gray-500">This usually takes 30-60 seconds</p>
                    </div>
                    
                    <!-- Success State -->
                    <div id="successState" class="hidden">
                        <div class="text-center py-8">
                            <div class="text-6xl mb-4">🎉</div>
                            <h3 class="text-2xl font-bold text-green-600 mb-4">Your Website is Ready!</h3>
                            <p class="text-gray-600 mb-6">We've created a professional website for your business with:</p>
                            
                            <div class="grid grid-cols-2 gap-4 mb-6 text-sm">
                                <div class="bg-green-50 p-3 rounded-lg">
                                    <div class="font-semibold text-green-800">✅ Mobile Optimized</div>
                                </div>
                                <div class="bg-green-50 p-3 rounded-lg">
                                    <div class="font-semibold text-green-800">✅ SEO Ready</div>
                                </div>
                                <div class="bg-green-50 p-3 rounded-lg">
                                    <div class="font-semibold text-green-800">✅ Contact Forms</div>
                                </div>
                                <div class="bg-green-50 p-3 rounded-lg">
                                    <div class="font-semibold text-green-800">✅ Fast Loading</div>
                                </div>
                            </div>
                            
                            <a id="previewLink" href="#" target="_blank" 
                               class="inline-block bg-green-600 hover:bg-green-700 text-white font-bold py-3 px-8 rounded-lg text-lg transition-colors duration-200">
                                🌐 View Your Website
                            </a>
                            
                            <div class="mt-6 p-4 bg-blue-50 rounded-lg">
                                <p class="text-sm text-blue-800">
                                    <strong>Want to customize further?</strong> 
                                    <a href="#" class="underline">Contact us</a> to learn about Hero365's full website builder platform.
                                </p>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Error State -->
                    <div id="errorState" class="hidden text-center py-8">
                        <div class="text-6xl mb-4">😞</div>
                        <h3 class="text-2xl font-bold text-red-600 mb-4">Oops! Something went wrong</h3>
                        <p class="text-gray-600 mb-6">We couldn't create your website right now. Please try again.</p>
                        <button onclick="resetForm()" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-6 rounded-lg">
                            Try Again
                        </button>
                    </div>
                </div>
                
                <!-- Features -->
                <div class="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div class="text-center">
                        <div class="text-4xl mb-2">⚡</div>
                        <h3 class="font-semibold text-gray-900">Lightning Fast</h3>
                        <p class="text-sm text-gray-600">Websites load in under 2 seconds</p>
                    </div>
                    <div class="text-center">
                        <div class="text-4xl mb-2">📱</div>
                        <h3 class="font-semibold text-gray-900">Mobile Ready</h3>
                        <p class="text-sm text-gray-600">Perfect on all devices</p>
                    </div>
                    <div class="text-center">
                        <div class="text-4xl mb-2">🔍</div>
                        <h3 class="font-semibold text-gray-900">SEO Optimized</h3>
                        <p class="text-sm text-gray-600">Built to rank on Google</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            document.getElementById('demoForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = {
                    trade_type: document.getElementById('tradeType').value,
                    business_name: document.getElementById('businessName').value || 'Demo Business',
                    location: document.getElementById('location').value || 'New York',
                    trade_category: 'residential' // Default for demo
                };
                
                // Show loading state
                document.getElementById('demoForm').style.display = 'none';
                document.getElementById('loadingState').classList.remove('hidden');
                
                try {
                    // Simulate API call (replace with actual endpoint)
                    await new Promise(resolve => setTimeout(resolve, 3000)); // 3 second delay for demo
                    
                    // Show success state
                    document.getElementById('loadingState').classList.add('hidden');
                    document.getElementById('successState').classList.remove('hidden');
                    
                    // Set preview link
                    const previewUrl = `https://demo-${formData.trade_type}-${Date.now()}.hero365.ai`;
                    document.getElementById('previewLink').href = previewUrl;
                    
                } catch (error) {
                    // Show error state
                    document.getElementById('loadingState').classList.add('hidden');
                    document.getElementById('errorState').classList.remove('hidden');
                }
            });
            
            function resetForm() {
                document.getElementById('errorState').classList.add('hidden');
                document.getElementById('successState').classList.add('hidden');
                document.getElementById('demoForm').style.display = 'block';
            }
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)
