import React from 'react';
import { Shield, Award, Users, Clock, CheckCircle, Star } from 'lucide-react';

interface AboutUsProps {
  business: {
    name: string;
    description?: string;
    founded?: string;
    employees?: number;
  };
  stats?: {
    yearsInBusiness?: number;
    customersServed?: number;
    projectsCompleted?: number;
    satisfactionRate?: number;
  };
}

export default function AboutUs({ 
  business, 
  stats = {
    yearsInBusiness: 25,
    customersServed: 5000,
    projectsCompleted: 8500,
    satisfactionRate: 98
  }
}: AboutUsProps) {
  
  const certifications = [
    { name: 'NATE Certified', description: 'North American Technician Excellence' },
    { name: 'EPA Certified', description: 'Environmental Protection Agency' },
    { name: 'BBB A+ Rating', description: 'Better Business Bureau' },
    { name: 'Licensed & Insured', description: 'State of Texas License #TACLA123456' }
  ];

  const values = [
    {
      icon: <Shield className="w-8 h-8" />,
      title: 'Integrity First',
      description: 'We believe in honest, transparent service with no hidden fees or unnecessary upsells.'
    },
    {
      icon: <Award className="w-8 h-8" />,
      title: 'Quality Workmanship',
      description: 'Every job is completed to the highest standards with attention to detail and craftsmanship.'
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: 'Customer Focus',
      description: 'Your comfort and satisfaction are our top priorities. We listen and deliver solutions.'
    },
    {
      icon: <Clock className="w-8 h-8" />,
      title: 'Reliable Service',
      description: 'On-time service, quick response, and dependable solutions you can count on.'
    }
  ];

  const teamMembers = [
    {
      name: 'Mike Johnson',
      title: 'Owner & Master Technician',
      experience: '25+ years',
      certifications: ['NATE Certified', 'EPA Universal'],
      image: '/api/placeholder/150/150'
    },
    {
      name: 'Sarah Martinez',
      title: 'Lead Service Technician',
      experience: '15+ years',
      certifications: ['NATE Certified', 'HVAC Excellence'],
      image: '/api/placeholder/150/150'
    },
    {
      name: 'David Chen',
      title: 'Installation Specialist',
      experience: '12+ years',
      certifications: ['EPA Certified', 'Manufacturer Trained'],
      image: '/api/placeholder/150/150'
    }
  ];

  return (
    <section id="about" className="py-16 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold mb-4">About {business.name}</h2>
          <p className="text-gray-600 max-w-3xl mx-auto text-lg">
            {business.description || `For over ${stats.yearsInBusiness} years, we've been Austin's trusted HVAC experts, providing reliable heating and cooling solutions for homes and businesses throughout the area.`}
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          <div className="text-center">
            <div className="bg-blue-600 text-white rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold">{stats.yearsInBusiness}+</span>
            </div>
            <h3 className="font-semibold text-gray-900">Years in Business</h3>
            <p className="text-gray-600">Serving Austin since 1999</p>
          </div>
          <div className="text-center">
            <div className="bg-green-600 text-white rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold">{(stats.customersServed / 1000).toFixed(0)}K+</span>
            </div>
            <h3 className="font-semibold text-gray-900">Happy Customers</h3>
            <p className="text-gray-600">Satisfied homeowners</p>
          </div>
          <div className="text-center">
            <div className="bg-orange-600 text-white rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold">{(stats.projectsCompleted / 1000).toFixed(1)}K+</span>
            </div>
            <h3 className="font-semibold text-gray-900">Projects Completed</h3>
            <p className="text-gray-600">Successful installations</p>
          </div>
          <div className="text-center">
            <div className="bg-purple-600 text-white rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
              <span className="text-2xl font-bold">{stats.satisfactionRate}%</span>
            </div>
            <h3 className="font-semibold text-gray-900">Satisfaction Rate</h3>
            <p className="text-gray-600">Customer satisfaction</p>
          </div>
        </div>

        {/* Our Story */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          <div>
            <h3 className="text-2xl font-bold mb-6">Our Story</h3>
            <div className="space-y-4 text-gray-700">
              <p>
                Founded in 1999, {business.name} began as a small family business with a simple mission: 
                provide honest, reliable HVAC services to the Austin community. What started with just 
                one truck and a commitment to quality has grown into one of the area's most trusted 
                HVAC companies.
              </p>
              <p>
                Over the years, we've built our reputation on three core principles: exceptional 
                workmanship, transparent pricing, and unmatched customer service. We believe that 
                your home's comfort shouldn't be compromised, which is why we're available 24/7 
                for emergency services.
              </p>
              <p>
                Today, our team of certified technicians continues to serve the Austin metro area 
                with the same dedication to excellence that has made us a household name. We're 
                not just your HVAC contractor – we're your neighbors, committed to keeping our 
                community comfortable year-round.
              </p>
            </div>
          </div>
          
          <div className="space-y-6">
            <h3 className="text-2xl font-bold mb-6">Why Choose Us?</h3>
            <div className="space-y-4">
              {[
                'Licensed, bonded, and insured for your protection',
                'NATE-certified technicians with ongoing training',
                'Upfront pricing with no hidden fees or surprises',
                '24/7 emergency service availability',
                '100% satisfaction guarantee on all work',
                'Financing options available for major repairs',
                'Same-day service for most repair requests',
                'Comprehensive maintenance plans available'
              ].map((item, index) => (
                <div key={index} className="flex items-start gap-3">
                  <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
                  <span className="text-gray-700">{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Our Values */}
        <div className="mb-16">
          <h3 className="text-2xl font-bold text-center mb-8">Our Values</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {values.map((value, index) => (
              <div key={index} className="bg-white rounded-xl p-6 text-center shadow-lg hover:shadow-xl transition-shadow duration-300">
                <div className="text-blue-600 mb-4 flex justify-center">
                  {value.icon}
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">{value.title}</h4>
                <p className="text-gray-600 text-sm">{value.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Certifications */}
        <div className="mb-16">
          <h3 className="text-2xl font-bold text-center mb-8">Certifications & Credentials</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {certifications.map((cert, index) => (
              <div key={index} className="bg-white rounded-lg p-6 text-center border-2 border-gray-200 hover:border-blue-300 transition-colors duration-200">
                <Award className="w-12 h-12 text-blue-600 mx-auto mb-3" />
                <h4 className="font-semibold text-gray-900 mb-1">{cert.name}</h4>
                <p className="text-sm text-gray-600">{cert.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Team */}
        <div>
          <h3 className="text-2xl font-bold text-center mb-8">Meet Our Team</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {teamMembers.map((member, index) => (
              <div key={index} className="bg-white rounded-xl p-6 text-center shadow-lg">
                <div className="w-32 h-32 bg-gray-200 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <Users className="w-16 h-16 text-gray-400" />
                </div>
                <h4 className="text-xl font-semibold text-gray-900 mb-1">{member.name}</h4>
                <p className="text-blue-600 font-medium mb-2">{member.title}</p>
                <p className="text-gray-600 mb-3">{member.experience} experience</p>
                <div className="space-y-1">
                  {member.certifications.map((cert, certIndex) => (
                    <span key={certIndex} className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full mr-1">
                      {cert}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
