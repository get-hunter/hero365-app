import React from 'react';
import { MapPin, Clock, CheckCircle } from 'lucide-react';

interface ServiceArea {
  name: string;
  distance?: string;
  responseTime?: string;
  popular?: boolean;
}

interface ServiceAreasProps {
  title?: string;
  subtitle?: string;
  areas?: ServiceArea[];
  primaryArea?: string;
  phone?: string;
}

export default function ServiceAreas({
  title = "Areas We Serve",
  subtitle = "Providing professional HVAC services throughout the Austin metro area",
  areas = [],
  primaryArea = "Austin, TX",
  phone = "(512) 555-HVAC"
}: ServiceAreasProps) {
  
  const defaultAreas: ServiceArea[] = [
    { name: 'Austin', distance: '0-15 miles', responseTime: '30 min', popular: true },
    { name: 'Round Rock', distance: '15-25 miles', responseTime: '45 min', popular: true },
    { name: 'Cedar Park', distance: '15-25 miles', responseTime: '45 min', popular: true },
    { name: 'Pflugerville', distance: '10-20 miles', responseTime: '40 min', popular: true },
    { name: 'Georgetown', distance: '20-30 miles', responseTime: '50 min' },
    { name: 'Leander', distance: '20-30 miles', responseTime: '50 min' },
    { name: 'Lakeway', distance: '15-25 miles', responseTime: '45 min' },
    { name: 'Bee Cave', distance: '20-30 miles', responseTime: '50 min' },
    { name: 'Dripping Springs', distance: '25-35 miles', responseTime: '60 min' },
    { name: 'Kyle', distance: '20-30 miles', responseTime: '50 min' },
    { name: 'Buda', distance: '25-35 miles', responseTime: '60 min' },
    { name: 'Hutto', distance: '20-30 miles', responseTime: '50 min' },
    { name: 'Manor', distance: '15-25 miles', responseTime: '45 min' },
    { name: 'Elgin', distance: '25-35 miles', responseTime: '60 min' },
    { name: 'Bastrop', distance: '30-40 miles', responseTime: '70 min' },
    { name: 'Wimberley', distance: '35-45 miles', responseTime: '80 min' }
  ];

  const displayAreas = areas.length > 0 ? areas : defaultAreas;
  const popularAreas = displayAreas.filter(area => area.popular);
  const otherAreas = displayAreas.filter(area => !area.popular);

  return (
    <section id="areas" className="py-16 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">{title}</h2>
          <p className="text-gray-600 max-w-2xl mx-auto">{subtitle}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Map Placeholder */}
          <div className="lg:col-span-2">
            <div className="bg-gray-100 rounded-xl p-8 h-96 flex items-center justify-center relative overflow-hidden">
              {/* Simple map representation */}
              <div className="absolute inset-0 bg-gradient-to-br from-blue-50 to-green-50"></div>
              <div className="relative z-10 text-center">
                <MapPin className="w-16 h-16 text-blue-600 mx-auto mb-4" />
                <h3 className="text-xl font-bold mb-2">Service Area Map</h3>
                <p className="text-gray-600 mb-4">
                  We serve a 50-mile radius around {primaryArea}
                </p>
                <div className="grid grid-cols-2 gap-4 max-w-md mx-auto">
                  {popularAreas.slice(0, 4).map((area, index) => (
                    <div key={area.name} className="bg-white rounded-lg p-3 shadow-md">
                      <div className="flex items-center gap-2">
                        <div className="w-3 h-3 bg-blue-600 rounded-full"></div>
                        <span className="font-medium">{area.name}</span>
                      </div>
                      <div className="text-sm text-gray-600 mt-1">
                        <Clock className="w-3 h-3 inline mr-1" />
                        {area.responseTime}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Service Areas List */}
          <div>
            <div className="bg-gray-50 rounded-xl p-6">
              <h3 className="text-xl font-bold mb-4">Primary Service Areas</h3>
              <div className="space-y-3 mb-6">
                {popularAreas.map((area) => (
                  <div key={area.name} className="flex items-center justify-between p-3 bg-white rounded-lg">
                    <div className="flex items-center gap-3">
                      <CheckCircle className="w-5 h-5 text-green-600" />
                      <div>
                        <p className="font-medium">{area.name}</p>
                        {area.distance && (
                          <p className="text-sm text-gray-600">{area.distance}</p>
                        )}
                      </div>
                    </div>
                    {area.responseTime && (
                      <div className="text-right">
                        <p className="text-sm font-medium text-blue-600">{area.responseTime}</p>
                        <p className="text-xs text-gray-500">avg response</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <h4 className="font-semibold mb-3">Additional Areas</h4>
              <div className="grid grid-cols-2 gap-2">
                {otherAreas.map((area) => (
                  <div key={area.name} className="flex items-center gap-2 p-2 text-sm">
                    <CheckCircle className="w-4 h-4 text-green-600 flex-shrink-0" />
                    <span>{area.name}</span>
                  </div>
                ))}
              </div>

              {/* Emergency Service Notice */}
              <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <h4 className="font-semibold text-red-800 mb-2">Emergency Service</h4>
                <p className="text-sm text-red-700 mb-3">
                  Available 24/7 in all service areas. Emergency fees may apply for after-hours service.
                </p>
                <a
                  href={`tel:${phone}`}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 transition-colors duration-200 inline-flex items-center gap-2"
                >
                  <Clock className="w-4 h-4" />
                  Call Emergency Line
                </a>
              </div>

              {/* Service Guarantee */}
              <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h4 className="font-semibold text-blue-800 mb-2">Service Guarantee</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Same-day service available</li>
                  <li>• No travel charges within 25 miles</li>
                  <li>• 100% satisfaction guarantee</li>
                  <li>• Licensed & insured technicians</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="text-center mt-12">
          <div className="bg-gradient-to-r from-blue-600 to-green-600 rounded-xl p-8 text-white">
            <h3 className="text-2xl font-bold mb-2">Don't See Your Area?</h3>
            <p className="mb-6">
              We're always expanding our service area. Call us to see if we can help!
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href={`tel:${phone}`}
                className="bg-white text-blue-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors duration-200 inline-flex items-center justify-center gap-2"
              >
                <MapPin className="w-5 h-5" />
                Call to Check Your Area
              </a>
              <a
                href="#contact"
                className="border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-blue-600 transition-colors duration-200"
              >
                Get Free Quote
              </a>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
