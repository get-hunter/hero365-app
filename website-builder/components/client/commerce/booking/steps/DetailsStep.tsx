/**
 * Details Step (Step 5)
 * 
 * Collects problem description and optional photo/video attachments
 */

'use client';

import React, { useState, useRef } from 'react';
import { FileText, Camera, Upload, X, AlertCircle, CheckCircle, Zap, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useBookingWizard, BookingDetails } from '../Hero365BookingContext';

interface DetailsStepProps {
  businessId: string;
  businessName?: string;
}

export default function DetailsStep({ 
  businessId, 
  businessName = 'our team' 
}: DetailsStepProps) {
  const { state, updateDetails, nextStep, prevStep, setError } = useBookingWizard();
  
  const [formData, setFormData] = useState<Partial<BookingDetails>>({
    notes: state.details?.notes || '',
    attachments: state.details?.attachments || [],
    urgencyLevel: state.details?.urgencyLevel || 'normal'
  });

  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadErrors, setUploadErrors] = useState<string[]>([]);

  const urgencyOptions = [
    {
      value: 'flexible' as const,
      label: 'Flexible',
      description: 'No rush, schedule when convenient',
      color: 'bg-green-50 border-green-200 text-green-900',
      icon: '📅'
    },
    {
      value: 'normal' as const,
      label: 'Normal',
      description: 'Standard service timing',
      color: 'bg-blue-50 border-blue-200 text-blue-900',
      icon: '🔧'
    },
    {
      value: 'urgent' as const,
      label: 'Urgent',
      description: 'Need service soon, willing to pay priority fee',
      color: 'bg-orange-50 border-orange-200 text-orange-900',
      icon: '⚡'
    },
    {
      value: 'emergency' as const,
      label: 'Emergency',
      description: 'Immediate attention required',
      color: 'bg-red-50 border-red-200 text-red-900',
      icon: '🚨'
    }
  ];

  const handleNotesChange = (value: string) => {
    setFormData(prev => ({ ...prev, notes: value }));
    setError();
  };

  const handleUrgencyChange = (urgency: BookingDetails['urgencyLevel']) => {
    setFormData(prev => ({ ...prev, urgencyLevel: urgency }));
  };

  const handleFileSelect = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;

    setIsUploading(true);
    setUploadErrors([]);

    const maxFileSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'video/mp4', 'video/quicktime'];
    const maxFiles = 5;

    const currentFiles = formData.attachments || [];
    const errors: string[] = [];

    // Validate files
    const validFiles: File[] = [];
    for (const file of files) {
      if (currentFiles.length + validFiles.length >= maxFiles) {
        errors.push(`Maximum ${maxFiles} files allowed`);
        break;
      }

      if (file.size > maxFileSize) {
        errors.push(`${file.name} is too large (max 10MB)`);
        continue;
      }

      if (!allowedTypes.includes(file.type)) {
        errors.push(`${file.name} is not a supported file type`);
        continue;
      }

      validFiles.push(file);
    }

    if (errors.length > 0) {
      setUploadErrors(errors);
    }

    if (validFiles.length > 0) {
      // In a real implementation, you would upload files to a server here
      // For now, we'll just store them in state
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate upload

      setFormData(prev => ({
        ...prev,
        attachments: [...(prev.attachments || []), ...validFiles]
      }));
    }

    setIsUploading(false);
    
    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const removeFile = (index: number) => {
    setFormData(prev => ({
      ...prev,
      attachments: prev.attachments?.filter((_, i) => i !== index) || []
    }));
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getFileIcon = (file: File) => {
    if (file.type.startsWith('image/')) return '🖼️';
    if (file.type.startsWith('video/')) return '🎥';
    return '📄';
  };

  const handleContinue = () => {
    const details: BookingDetails = {
      notes: formData.notes || '',
      attachments: formData.attachments || [],
      urgencyLevel: formData.urgencyLevel || 'normal'
    };

    updateDetails(details);
    nextStep();
  };

  const selectedUrgency = urgencyOptions.find(opt => opt.value === formData.urgencyLevel);

  return (
    <div className="max-w-2xl mx-auto p-6 space-y-6">
      {/* Back Button */}
      <div className="flex items-center justify-start mb-4">
        <Button
          variant="ghost"
          size="sm"
          onClick={prevStep}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-900"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back</span>
        </Button>
      </div>

      {/* Header */}
      <div className="text-center">
        <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <FileText className="w-8 h-8 text-blue-600" />
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          Tell us about the problem
        </h1>
        <p className="text-gray-600">
          Help our technician prepare by describing the issue and sharing photos if helpful
        </p>
      </div>

      {/* Problem Description */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <FileText className="w-5 h-5" />
            <span>Problem Description</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Describe the issue (Optional)
            </label>
            <Textarea
              value={formData.notes || ''}
              onChange={(e) => handleNotesChange(e.target.value)}
              placeholder="Tell us what's happening... For example: 'Air conditioner not cooling', 'Strange noise from water heater', 'Electrical outlet not working', etc."
              rows={4}
              className="w-full"
            />
            <p className="text-xs text-gray-500 mt-2">
              The more details you provide, the better we can prepare for your service call
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Urgency Level */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="w-5 h-5" />
            <span>How urgent is this?</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {urgencyOptions.map((option) => (
              <button
                key={option.value}
                onClick={() => handleUrgencyChange(option.value)}
                className={`
                  p-4 rounded-lg border-2 text-left transition-all duration-200
                  ${formData.urgencyLevel === option.value
                    ? option.color + ' border-current'
                    : 'bg-white border-gray-200 hover:border-gray-300'
                  }
                `}
              >
                <div className="flex items-start space-x-3">
                  <span className="text-2xl">{option.icon}</span>
                  <div>
                    <h3 className="font-semibold text-sm mb-1">
                      {option.label}
                    </h3>
                    <p className="text-xs text-gray-600">
                      {option.description}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>
          
          {formData.urgencyLevel === 'emergency' && (
            <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <div className="flex items-start space-x-2">
                <AlertCircle className="w-4 h-4 text-red-600 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-red-900">Emergency Service</p>
                  <p className="text-xs text-red-700 mt-1">
                    Emergency calls may include additional fees and will be prioritized for immediate response.
                  </p>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Photo/Video Upload */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Camera className="w-5 h-5" />
            <span>Photos & Videos (Optional)</span>
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <p className="text-sm text-gray-600 mb-4">
              Share photos or videos to help our technician understand the problem better
            </p>

            {/* Upload Button */}
            <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-gray-400 transition-colors">
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*,video/*"
                onChange={handleFileChange}
                className="hidden"
              />
              
              <Upload className="w-8 h-8 text-gray-400 mx-auto mb-3" />
              
              <Button
                onClick={handleFileSelect}
                disabled={isUploading}
                variant="outline"
                className="mb-2"
              >
                {isUploading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full animate-spin mr-2"></div>
                    Uploading...
                  </>
                ) : (
                  <>
                    <Camera className="w-4 h-4 mr-2" />
                    Choose Files
                  </>
                )}
              </Button>
              
              <p className="text-xs text-gray-500">
                Images and videos up to 10MB each • Max 5 files
              </p>
            </div>

            {/* Upload Errors */}
            {uploadErrors.length > 0 && (
              <div className="mt-3 space-y-1">
                {uploadErrors.map((error, index) => (
                  <div key={index} className="flex items-center space-x-2 text-sm text-red-600">
                    <AlertCircle className="w-4 h-4" />
                    <span>{error}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Uploaded Files */}
            {formData.attachments && formData.attachments.length > 0 && (
              <div className="mt-4 space-y-2">
                <p className="text-sm font-medium text-gray-700">
                  Uploaded Files ({formData.attachments.length}/5)
                </p>
                {formData.attachments.map((file, index) => (
                  <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
                    <div className="flex items-center space-x-3">
                      <span className="text-lg">{getFileIcon(file)}</span>
                      <div>
                        <p className="text-sm font-medium text-gray-900">{file.name}</p>
                        <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                      </div>
                    </div>
                    <Button
                      onClick={() => removeFile(index)}
                      variant="ghost"
                      size="sm"
                      className="text-gray-400 hover:text-red-600"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Service Summary */}
      {state.contact && state.slot && (
        <Card className="border-blue-200 bg-blue-50">
          <CardContent className="p-4">
            <div className="flex items-start space-x-3">
              <CheckCircle className="w-5 h-5 text-blue-600 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-blue-900 mb-2">
                  Ready to Review
                </p>
                <div className="text-xs text-blue-700 space-y-1">
                  <p>👤 {state.contact.firstName} {state.contact.lastName}</p>
                  <p>📞 {state.contact.phoneE164}</p>
                  <p>📧 {state.contact.email}</p>
                  {selectedUrgency && (
                    <div className="flex items-center space-x-1 mt-2">
                      <span>{selectedUrgency.icon}</span>
                      <Badge variant="outline" className="text-xs">
                        {selectedUrgency.label} Priority
                      </Badge>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Continue Button */}
      <div className="flex justify-center pt-4">
        <Button
          onClick={handleContinue}
          size="lg"
          className="px-8"
        >
          Review Booking
        </Button>
      </div>

      {/* Help Text */}
      <div className="text-center">
        <p className="text-sm text-gray-500">
          Photos and descriptions help our technicians come prepared with the right tools and parts
        </p>
      </div>
    </div>
  );
}
