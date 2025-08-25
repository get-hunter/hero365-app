/**
 * Widget Demo Page
 * 
 * Demonstrates different ways to embed the Hero365 booking widget
 */

'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Input } from '../../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../components/ui/select';
import { Textarea } from '../../components/ui/textarea';
import { Badge } from '../../components/ui/badge';
import { Copy, ExternalLink, Code, Smartphone, Monitor, Sidebar } from 'lucide-react';
import { generateEmbedCode } from '../../components/booking/EmbeddableBookingWidget';

export default function WidgetDemoPage() {
  const [config, setConfig] = useState({
    businessId: '123e4567-e89b-12d3-a456-426614174000',
    mode: 'inline' as 'popup' | 'inline' | 'sidebar',
    theme: 'light' as 'light' | 'dark' | 'auto',
    primaryColor: '#3b82f6',
    companyName: 'Professional Services',
    width: '100%',
    height: '600px'
  });

  const [copiedCode, setCopiedCode] = useState<string | null>(null);

  const embedCodes = generateEmbedCode(config);

  const copyToClipboard = (text: string, type: string) => {
    navigator.clipboard.writeText(text).then(() => {
      setCopiedCode(type);
      setTimeout(() => setCopiedCode(null), 2000);
    });
  };

  const previewUrl = `/widget?${new URLSearchParams({
    businessId: config.businessId,
    mode: config.mode,
    theme: config.theme,
    primaryColor: config.primaryColor,
    companyName: config.companyName
  }).toString()}`;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Hero365 Booking Widget Demo
            </h1>
            <p className="text-lg text-gray-600">
              Embed our booking system into any website with just a few lines of code
            </p>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Configuration Panel */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code className="w-5 h-5" />
                  Widget Configuration
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Business ID */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Business ID
                  </label>
                  <Input
                    value={config.businessId}
                    onChange={(e) => setConfig(prev => ({ ...prev, businessId: e.target.value }))}
                    placeholder="Enter your business ID"
                  />
                </div>

                {/* Display Mode */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Display Mode
                  </label>
                  <Select
                    value={config.mode}
                    onValueChange={(value: any) => setConfig(prev => ({ ...prev, mode: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="inline">
                        <div className="flex items-center gap-2">
                          <Monitor className="w-4 h-4" />
                          Inline - Embedded in page content
                        </div>
                      </SelectItem>
                      <SelectItem value="popup">
                        <div className="flex items-center gap-2">
                          <Smartphone className="w-4 h-4" />
                          Popup - Overlay modal
                        </div>
                      </SelectItem>
                      <SelectItem value="sidebar">
                        <div className="flex items-center gap-2">
                          <Sidebar className="w-4 h-4" />
                          Sidebar - Fixed side panel
                        </div>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Theme */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Theme
                  </label>
                  <Select
                    value={config.theme}
                    onValueChange={(value: any) => setConfig(prev => ({ ...prev, theme: value }))}
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="light">Light</SelectItem>
                      <SelectItem value="dark">Dark</SelectItem>
                      <SelectItem value="auto">Auto (System)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Primary Color */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Primary Color
                  </label>
                  <div className="flex gap-2">
                    <Input
                      type="color"
                      value={config.primaryColor}
                      onChange={(e) => setConfig(prev => ({ ...prev, primaryColor: e.target.value }))}
                      className="w-16 h-10 p-1 border rounded"
                    />
                    <Input
                      value={config.primaryColor}
                      onChange={(e) => setConfig(prev => ({ ...prev, primaryColor: e.target.value }))}
                      placeholder="#3b82f6"
                      className="flex-1"
                    />
                  </div>
                </div>

                {/* Company Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Company Name
                  </label>
                  <Input
                    value={config.companyName}
                    onChange={(e) => setConfig(prev => ({ ...prev, companyName: e.target.value }))}
                    placeholder="Your Company Name"
                  />
                </div>

                {/* Dimensions (for iframe) */}
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Width
                    </label>
                    <Input
                      value={config.width}
                      onChange={(e) => setConfig(prev => ({ ...prev, width: e.target.value }))}
                      placeholder="100%"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Height
                    </label>
                    <Input
                      value={config.height}
                      onChange={(e) => setConfig(prev => ({ ...prev, height: e.target.value }))}
                      placeholder="600px"
                    />
                  </div>
                </div>

                {/* Preview Button */}
                <Button
                  onClick={() => window.open(previewUrl, '_blank')}
                  className="w-full flex items-center gap-2"
                >
                  <ExternalLink className="w-4 h-4" />
                  Preview Widget
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Embed Codes */}
          <div className="space-y-6">
            {/* iframe Embed */}
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="flex items-center gap-2">
                    <Monitor className="w-5 h-5" />
                    iframe Embed
                  </CardTitle>
                  <Badge variant="secondary">Recommended</Badge>
                </div>
                <p className="text-sm text-gray-600">
                  Simple iframe embedding - works on any website
                </p>
              </CardHeader>
              <CardContent>
                <div className="relative">
                  <Textarea
                    value={embedCodes.iframe}
                    readOnly
                    rows={6}
                    className="font-mono text-sm"
                  />
                  <Button
                    size="sm"
                    variant="outline"
                    className="absolute top-2 right-2"
                    onClick={() => copyToClipboard(embedCodes.iframe, 'iframe')}
                  >
                    {copiedCode === 'iframe' ? (
                      'Copied!'
                    ) : (
                      <>
                        <Copy className="w-4 h-4 mr-1" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* JavaScript Embed */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Code className="w-5 h-5" />
                  JavaScript Embed
                </CardTitle>
                <p className="text-sm text-gray-600">
                  Dynamic loading with more customization options
                </p>
              </CardHeader>
              <CardContent>
                <div className="relative">
                  <Textarea
                    value={embedCodes.script}
                    readOnly
                    rows={8}
                    className="font-mono text-sm"
                  />
                  <Button
                    size="sm"
                    variant="outline"
                    className="absolute top-2 right-2"
                    onClick={() => copyToClipboard(embedCodes.script, 'script')}
                  >
                    {copiedCode === 'script' ? (
                      'Copied!'
                    ) : (
                      <>
                        <Copy className="w-4 h-4 mr-1" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Direct Link */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <ExternalLink className="w-5 h-5" />
                  Direct Link
                </CardTitle>
                <p className="text-sm text-gray-600">
                  Direct URL for testing or linking
                </p>
              </CardHeader>
              <CardContent>
                <div className="relative">
                  <Input
                    value={embedCodes.directUrl}
                    readOnly
                    className="font-mono text-sm pr-20"
                  />
                  <Button
                    size="sm"
                    variant="outline"
                    className="absolute top-1 right-1"
                    onClick={() => copyToClipboard(embedCodes.directUrl, 'url')}
                  >
                    {copiedCode === 'url' ? (
                      'Copied!'
                    ) : (
                      <>
                        <Copy className="w-4 h-4 mr-1" />
                        Copy
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Integration Examples */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Integration Examples</h2>
          
          <div className="grid md:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">WordPress</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  Add the iframe code to any WordPress page or post using the HTML block.
                </p>
                <div className="bg-gray-100 p-3 rounded text-xs font-mono">
                  1. Edit page/post<br/>
                  2. Add HTML block<br/>
                  3. Paste iframe code<br/>
                  4. Publish
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Shopify</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  Embed in product pages or create a dedicated booking page.
                </p>
                <div className="bg-gray-100 p-3 rounded text-xs font-mono">
                  1. Edit theme<br/>
                  2. Add custom HTML section<br/>
                  3. Insert iframe code<br/>
                  4. Save theme
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Custom Website</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  Use JavaScript embed for dynamic loading and better performance.
                </p>
                <div className="bg-gray-100 p-3 rounded text-xs font-mono">
                  1. Add script to &lt;head&gt;<br/>
                  2. Configure options<br/>
                  3. Widget loads automatically<br/>
                  4. Customize styling
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Features */}
        <div className="mt-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Widget Features</h2>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-white rounded-lg shadow-sm">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Monitor className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="font-semibold mb-2">Responsive Design</h3>
              <p className="text-sm text-gray-600">Works perfectly on desktop, tablet, and mobile devices</p>
            </div>

            <div className="text-center p-4 bg-white rounded-lg shadow-sm">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Code className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="font-semibold mb-2">Easy Integration</h3>
              <p className="text-sm text-gray-600">Simple copy-paste integration with any website platform</p>
            </div>

            <div className="text-center p-4 bg-white rounded-lg shadow-sm">
              <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <Smartphone className="w-6 h-6 text-purple-600" />
              </div>
              <h3 className="font-semibold mb-2">Multiple Modes</h3>
              <p className="text-sm text-gray-600">Inline, popup, or sidebar display options</p>
            </div>

            <div className="text-center p-4 bg-white rounded-lg shadow-sm">
              <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <ExternalLink className="w-6 h-6 text-orange-600" />
              </div>
              <h3 className="font-semibold mb-2">Customizable</h3>
              <p className="text-sm text-gray-600">Match your brand colors and styling preferences</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
