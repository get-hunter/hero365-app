
import { NextApiRequest, NextApiResponse } from 'next';

export default async function handler(
  req: NextApiRequest,
  res: NextApiResponse
) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Extract form data
    const formData = req.body;
    
    // Submit to Hero365 backend
    const response = await fetch('http://localhost:8000/api/websites/forms/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        website_id: '3ed09ec0-c570-445f-8e40-11ddba83e624',
        business_id: '23250f53-29f3-4eb7-a6d3-3bce994228ee',
        form_data: formData,
        visitor_info: {
          ip: req.headers['x-forwarded-for'] || req.connection.remoteAddress,
          user_agent: req.headers['user-agent'],
          referrer: req.headers.referer
        }
      })
    });
    
    if (response.ok) {
      const result = await response.json();
      res.status(200).json({ success: true, message: 'Form submitted successfully' });
    } else {
      res.status(500).json({ error: 'Failed to submit form' });
    }
  } catch (error) {
    console.error('Form submission error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
}