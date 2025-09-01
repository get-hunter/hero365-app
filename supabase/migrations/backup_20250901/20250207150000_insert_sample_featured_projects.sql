-- Insert sample featured projects for Austin Elite Home Services
-- This migration adds demo projects to showcase the featured projects functionality

-- Insert sample projects only if none exist
DO $$
DECLARE
    business_uuid UUID;
    project_count INTEGER;
BEGIN
    -- Get the business ID
    SELECT id INTO business_uuid FROM businesses WHERE is_active = true LIMIT 1;
    
    IF business_uuid IS NOT NULL THEN
        -- Check if projects already exist for this business
        SELECT COUNT(*) INTO project_count FROM featured_projects WHERE business_id = business_uuid;
        
        -- Only insert if no projects exist
        IF project_count = 0 THEN
            -- Insert first project
            INSERT INTO featured_projects (
                business_id, title, description, trade, service_category, location,
                completion_date, project_duration, project_value, customer_name,
                customer_testimonial, before_images, after_images, gallery_images,
                challenges_faced, solutions_provided, equipment_installed,
                warranty_info, is_featured, seo_slug, tags, display_order
            ) VALUES (
                business_uuid,
                'Complete HVAC System Replacement',
                'Full HVAC system replacement for a 3,500 sq ft home including new ductwork, smart thermostat, and energy-efficient units.',
                'HVAC',
                'HVAC Installation',
                'Austin, TX',
                DATE '2024-01-15',
                '3 days',
                15500.00,
                'Sarah Johnson',
                'Outstanding service from start to finish. The team was professional, clean, and completed the job ahead of schedule. Our energy bills have dropped significantly!',
                ARRAY['https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800', 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800'],
                ARRAY['https://images.unsplash.com/photo-1631889993959-41b4e9c6e3c5?w=800', 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800'],
                ARRAY['https://images.unsplash.com/photo-1631889993959-41b4e9c6e3c5?w=800', 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800', 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800'],
                ARRAY['Old system was 20+ years old and inefficient', 'Ductwork needed complete replacement', 'Tight timeline before summer heat'],
                ARRAY['Installed high-efficiency variable speed system', 'Replaced all ductwork with proper insulation', 'Added smart zoning controls'],
                ARRAY['Carrier Infinity 19VS Heat Pump', 'Carrier Infinity Air Handler', 'Ecobee Smart Thermostat Pro', 'New insulated ductwork'],
                '10-year manufacturer warranty on equipment, 5-year warranty on installation',
                true,
                'complete-hvac-system-replacement-austin',
                ARRAY['Residential', 'Energy Efficient', 'Smart Home', 'Upgrade'],
                1
            );

            -- Insert second project
            INSERT INTO featured_projects (
                business_id, title, description, trade, service_category, location,
                completion_date, project_duration, project_value, customer_name,
                customer_testimonial, before_images, after_images, gallery_images,
                challenges_faced, solutions_provided, equipment_installed,
                warranty_info, is_featured, seo_slug, tags, display_order
            ) VALUES (
                business_uuid,
                'Emergency Plumbing Repair - Burst Pipe',
                'Emergency response to a burst pipe in the main water line. Completed full repair and restoration within 4 hours.',
                'Plumbing',
                'Plumbing Repair',
                'Round Rock, TX',
                DATE '2024-01-20',
                '4 hours',
                850.00,
                'Mike Chen',
                'Called at 2 AM with a burst pipe flooding my basement. They arrived within 30 minutes and had everything fixed by 6 AM. Incredible service!',
                ARRAY['https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800'],
                ARRAY['https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800'],
                ARRAY['https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800', 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800'],
                ARRAY['Water damage spreading rapidly', 'Limited access to main line', 'Emergency response needed'],
                ARRAY['Immediate water shutoff and containment', 'Replaced damaged section with PEX piping', 'Pressure tested entire system'],
                ARRAY['PEX piping and fittings', 'New shutoff valve', 'Pipe insulation'],
                '2-year warranty on all parts and labor',
                true,
                'emergency-plumbing-repair-burst-pipe',
                ARRAY['Emergency', 'Residential', 'Warranty Work'],
                2
            );

            -- Insert third project
            INSERT INTO featured_projects (
                business_id, title, description, trade, service_category, location,
                completion_date, project_duration, project_value, customer_name,
                customer_testimonial, before_images, after_images, gallery_images,
                challenges_faced, solutions_provided, equipment_installed,
                warranty_info, is_featured, seo_slug, tags, display_order
            ) VALUES (
                business_uuid,
                'Smart Home Security System Installation',
                'Complete smart security system installation with cameras, sensors, and mobile app integration for a modern home.',
                'Security Systems',
                'Security Installation',
                'Pflugerville, TX',
                DATE '2024-02-10',
                '1 day',
                4800.00,
                'Robert Kim',
                'Excellent installation and setup. The mobile app works perfectly and we feel much more secure. Highly recommend!',
                ARRAY['https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800'],
                ARRAY['https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800'],
                ARRAY['https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800', 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800'],
                ARRAY['Existing system was outdated', 'Wanted mobile integration', 'Multiple entry points to secure'],
                ARRAY['Installed wireless security system', 'Set up mobile app and notifications', 'Added smart door locks and cameras'],
                ARRAY['Ring Alarm Pro System', '8 Door/Window Sensors', '4 Motion Detectors', '6 Security Cameras', 'Smart Door Locks'],
                '3-year manufacturer warranty, 1-year installation warranty',
                true,
                'smart-home-security-system-installation',
                ARRAY['Residential', 'Smart Home', 'Security'],
                3
            );

            -- Insert fourth project
            INSERT INTO featured_projects (
                business_id, title, description, trade, service_category, location,
                completion_date, project_duration, project_value, customer_name,
                customer_testimonial, before_images, after_images, gallery_images,
                challenges_faced, solutions_provided, equipment_installed,
                warranty_info, is_featured, seo_slug, tags, display_order
            ) VALUES (
                business_uuid,
                'Commercial Electrical Panel Upgrade',
                'Upgraded electrical panel for a 10,000 sq ft office building to support increased power demands and improve safety.',
                'Electrical',
                'Electrical Installation',
                'Cedar Park, TX',
                DATE '2024-01-25',
                '2 days',
                8500.00,
                'David Rodriguez',
                'Professional installation with minimal disruption to our business operations. The team worked around our schedule perfectly.',
                ARRAY['https://images.unsplash.com/photo-1504307651254-35680f356dfd?w=800'],
                ARRAY['https://images.unsplash.com/photo-1631889993959-41b4e9c6e3c5?w=800'],
                ARRAY['https://images.unsplash.com/photo-1631889993959-41b4e9c6e3c5?w=800', 'https://images.unsplash.com/photo-1558618047-3c8c76ca7d13?w=800'],
                ARRAY['Old panel at capacity', 'Code compliance requirements', 'Minimize business downtime'],
                ARRAY['Installed 400A main panel', 'Added surge protection', 'Updated all circuits to code'],
                ARRAY['400A electrical panel', 'Surge protection system', 'New circuit breakers', 'Updated wiring'],
                '5-year warranty on panel and installation',
                false,
                'commercial-electrical-panel-upgrade',
                ARRAY['Commercial', 'Upgrade', 'New Construction'],
                4
            );

            -- Insert fifth project
            INSERT INTO featured_projects (
                business_id, title, description, trade, service_category, location,
                completion_date, project_duration, project_value, customer_name,
                customer_testimonial, before_images, after_images, gallery_images,
                challenges_faced, solutions_provided, equipment_installed,
                warranty_info, is_featured, seo_slug, tags, display_order
            ) VALUES (
                business_uuid,
                'Residential Pool Heater Installation',
                'Installation of energy-efficient pool heater system with smart controls for year-round swimming comfort.',
                'Pool & Spa',
                'Pool Equipment Installation',
                'Lakeway, TX',
                DATE '2024-02-01',
                '1 day',
                3200.00,
                'Jennifer Martinez',
                'Great job on the pool heater installation. Now we can enjoy our pool even in the cooler months. Very professional team!',
                ARRAY['https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800'],
                ARRAY['https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=800'],
                ARRAY['https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=800', 'https://images.unsplash.com/photo-1544551763-46a013bb70d5?w=800'],
                ARRAY['Existing heater was inefficient', 'Pool area had limited space', 'Customer wanted smart controls'],
                ARRAY['Installed compact high-efficiency heater', 'Added smart pool control system', 'Optimized plumbing layout'],
                ARRAY['Pentair MasterTemp 400K BTU Heater', 'IntelliCenter Pool Control System', 'New gas line and connections'],
                '3-year manufacturer warranty, 2-year installation warranty',
                true,
                'residential-pool-heater-installation',
                ARRAY['Residential', 'Smart Home', 'Energy Efficient'],
                5
            );

            -- Insert sixth project
            INSERT INTO featured_projects (
                business_id, title, description, trade, service_category, location,
                completion_date, project_duration, project_value, customer_name,
                customer_testimonial, before_images, after_images, gallery_images,
                challenges_faced, solutions_provided, equipment_installed,
                warranty_info, is_featured, seo_slug, tags, display_order
            ) VALUES (
                business_uuid,
                'Kitchen Equipment Maintenance Contract',
                'Comprehensive maintenance service for restaurant kitchen equipment including ovens, fryers, and refrigeration units.',
                'Kitchen Equipment',
                'Maintenance',
                'Downtown Austin, TX',
                DATE '2024-02-05',
                'Ongoing',
                2400.00,
                'Restaurant Manager - Tony''s Bistro',
                'Having a reliable maintenance contract has saved us thousands in emergency repairs. The team is always responsive and professional.',
                ARRAY['https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800'],
                ARRAY['https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800'],
                ARRAY['https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=800'],
                ARRAY['Equipment was breaking down frequently', 'High emergency repair costs', 'Need for preventive maintenance'],
                ARRAY['Implemented quarterly maintenance schedule', 'Replaced worn components proactively', 'Provided staff training on proper usage'],
                ARRAY['Replacement filters and gaskets', 'Calibration tools', 'Cleaning supplies and chemicals'],
                '1-year service contract with parts warranty',
                false,
                'kitchen-equipment-maintenance-contract',
                ARRAY['Commercial', 'Maintenance'],
                6
            );

            RAISE NOTICE 'Successfully inserted % sample featured projects for business %', 6, business_uuid;
        ELSE
            RAISE NOTICE 'Featured projects already exist for business %, skipping insert', business_uuid;
        END IF;
    ELSE
        RAISE NOTICE 'No active business found, skipping featured projects insert';
    END IF;
END $$;


