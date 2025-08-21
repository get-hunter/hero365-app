# Template Visual Parameters API - Mobile Integration Guide

## Overview

This document describes the enhanced template API endpoints that provide visual configuration parameters for mobile app template differentiation and thumbnail generation.

## Key Changes

### What's New
- **Enhanced Visual Configuration**: Templates now include detailed visual parameters
- **Mobile-Optimized Endpoint**: New `/templates/mobile/{template_type}` endpoint
- **Layout Style Detection**: Automatic detection of visual styles for existing templates
- **Backward Compatibility**: Existing endpoints continue to work unchanged

### Benefits for Mobile App
- **Distinct Thumbnails**: Each template has unique visual characteristics
- **Better UX**: Users can immediately differentiate between templates
- **Consistent Branding**: Templates maintain visual consistency across platforms

## New Mobile Endpoint

### GET `/templates/mobile/{template_type}`

Returns templates with enhanced visual parameters optimized for mobile app consumption.

**URL**: `/api/v1/templates/mobile/{template_type}`

**Method**: `GET`

**Parameters**:
- `template_type` (path): Template type (invoice, estimate, contract, etc.)
- `is_active` (query, optional): Filter by active status (default: true)
- `is_system` (query, optional): Show only system templates

**Headers**:
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Response Format**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Emergency Service Invoice",
    "template_type": "invoice",
    "category": "service_focused",
    "layout_style": "creative_split",
    "description": "Bold emergency service template with distinctive red theme",
    "is_active": true,
    "is_default": false,
    "is_system": true,
    "colors": {
      "primary": "#DC2626",
      "secondary": "#64748B",
      "accent": "#FEF3C7",
      "background": "#FFFFFF",
      "text_primary": "#000000",
      "text_secondary": "#6B7280",
      "border": "#E2E8F0",
      "header_background": "#DC2626",
      "header_text": "#FFFFFF",
      "table_header": "#FEF3C7"
    },
    "header_style": {
      "type": "split",
      "height": "medium",
      "show_logo": true,
      "logo_position": "left",
      "show_border": true,
      "border_style": "solid"
    },
    "layout_elements": {
      "side_panel": {
        "enabled": true,
        "position": "left",
        "width": "narrow"
      },
      "accent_bars": {
        "enabled": true,
        "position": "left",
        "thickness": "medium"
      },
      "spacing": {
        "sections": "normal",
        "elements": "normal"
      }
    },
    "visual_theme": {
      "border_radius": 4,
      "shadow_style": "subtle",
      "line_style": "solid",
      "table_style": "modern"
    },
    "typography": {
      "title": {
        "font": "System",
        "size": 28,
        "weight": "bold"
      },
      "header": {
        "font": "System",
        "size": 14,
        "weight": "semibold"
      },
      "body": {
        "font": "System",
        "size": 11,
        "weight": "regular"
      }
    },
    "created_at": "2025-01-27T10:00:00Z",
    "updated_at": "2025-01-27T10:00:00Z"
  }
]
```

## Layout Styles

### Available Layout Styles

| Layout Style | Description | Visual Characteristics |
|-------------|-------------|----------------------|
| `modern_minimal` | Clean, minimal design | Thin lines, subtle colors, minimal borders |
| `corporate_bold` | Strong corporate look | Bold headers, prominent branding, structured layout |
| `creative_split` | Unique side panel design | Side panel, rotated text, distinctive layout |
| `professional` | Traditional business style | Standard layout, professional colors, balanced design |
| `elegant_simple` | Refined, centered design | Centered elements, elegant typography, subtle styling |

### Layout Style Detection

For templates without explicit `layout_style`, the system automatically detects the style based on template name:

```javascript
// Detection logic (for reference)
const detectLayoutStyle = (templateName) => {
  const name = templateName.toLowerCase();
  
  if (name.includes('emergency') || name.includes('urgent') || name.includes('service')) {
    return 'creative_split';
  }
  if (name.includes('professional') || name.includes('corporate') || name.includes('business')) {
    return 'corporate_bold';
  }
  if (name.includes('classic') || name.includes('elegant') || name.includes('traditional')) {
    return 'elegant_simple';
  }
  if (name.includes('modern') || name.includes('minimal') || name.includes('clean')) {
    return 'modern_minimal';
  }
  return 'professional';
};
```

## Visual Configuration Structure

### Colors Configuration

```json
{
  "colors": {
    "primary": "#2563EB",           // Main brand color
    "secondary": "#64748B",         // Supporting text color  
    "accent": "#10B981",            // Highlight/accent color
    "background": "#FFFFFF",        // Document background
    "text_primary": "#000000",      // Primary text color
    "text_secondary": "#6B7280",    // Secondary text color
    "border": "#E2E8F0",            // Border colors
    "header_background": "#2563EB", // Header background color
    "header_text": "#FFFFFF",       // Header text color
    "table_header": "#F1F5F9"       // Table header background
  }
}
```

### Header Style Configuration

```json
{
  "header_style": {
    "type": "bold",              // "bold" | "minimal" | "split" | "traditional" | "centered"
    "height": "large",           // "small" | "medium" | "large"
    "show_logo": true,           // Boolean
    "logo_position": "left",     // "left" | "right" | "center"
    "show_border": true,         // Boolean
    "border_style": "solid"      // "solid" | "dashed" | "none"
  }
}
```

### Layout Elements Configuration

```json
{
  "layout_elements": {
    "side_panel": {
      "enabled": false,          // Boolean
      "position": "left",        // "left" | "right"
      "width": "narrow"          // "narrow" | "medium" | "wide"
    },
    "accent_bars": {
      "enabled": true,           // Boolean
      "position": "left",        // "left" | "right" | "top" | "bottom"
      "thickness": "medium"      // "thin" | "medium" | "thick"
    },
    "spacing": {
      "sections": "normal",      // "compact" | "normal" | "spacious"
      "elements": "normal"       // "tight" | "normal" | "loose"
    }
  }
}
```

### Visual Theme Configuration

```json
{
  "visual_theme": {
    "border_radius": 4,          // 0 | 2 | 4 | 8 (corner radius)
    "shadow_style": "subtle",    // "none" | "subtle" | "prominent"
    "line_style": "solid",       // "solid" | "dashed" | "dotted"
    "table_style": "bordered"    // "minimal" | "bordered" | "striped" | "modern"
  }
}
```

## Mobile Implementation Guide

### 1. Fetching Templates

```swift
// Swift example
func fetchTemplates(type: String) async throws -> [MobileTemplate] {
    let url = "\(baseURL)/templates/mobile/\(type)?is_active=true"
    let response = try await apiClient.get(url)
    return try JSONDecoder().decode([MobileTemplate].self, from: response)
}
```

### 2. Generating Thumbnails

Use the visual parameters to generate distinct thumbnails:

```swift
func generateThumbnail(for template: MobileTemplate) -> UIImage {
    let renderer = UIGraphicsImageRenderer(size: CGSize(width: 200, height: 150))
    
    return renderer.image { context in
        // Use template.colors.header_background for header
        UIColor(hex: template.colors.headerBackground).setFill()
        
        // Apply layout_style specific rendering
        switch template.layoutStyle {
        case "creative_split":
            renderCreativeSplitLayout(template, context)
        case "corporate_bold":
            renderCorporateBoldLayout(template, context)
        case "elegant_simple":
            renderElegantSimpleLayout(template, context)
        case "modern_minimal":
            renderModernMinimalLayout(template, context)
        default:
            renderProfessionalLayout(template, context)
        }
    }
}
```

### 3. Template Selection UI

```swift
struct TemplateSelectionView: View {
    @State private var templates: [MobileTemplate] = []
    
    var body: some View {
        LazyVGrid(columns: columns, spacing: 16) {
            ForEach(templates, id: \.id) { template in
                TemplateCard(template: template)
                    .onTapGesture {
                        selectTemplate(template)
                    }
            }
        }
        .onAppear {
            loadTemplates()
        }
    }
}

struct TemplateCard: View {
    let template: MobileTemplate
    
    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            // Thumbnail generated from visual parameters
            TemplateThumbnail(template: template)
                .frame(height: 120)
                .cornerRadius(8)
            
            Text(template.name)
                .font(.headline)
                .lineLimit(2)
            
            Text(template.layoutStyle.capitalized)
                .font(.caption)
                .foregroundColor(.secondary)
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .shadow(radius: 2)
    }
}
```

## Example Responses

### Professional Template
```json
{
  "id": "prof-001",
  "name": "Professional Business Invoice",
  "layout_style": "professional",
  "colors": {
    "primary": "#2563EB",
    "header_background": "#2563EB",
    "header_text": "#FFFFFF"
  },
  "header_style": {
    "type": "standard",
    "height": "medium"
  },
  "layout_elements": {
    "side_panel": {"enabled": false},
    "accent_bars": {"enabled": false}
  }
}
```

### Emergency Service Template
```json
{
  "id": "emerg-001", 
  "name": "Emergency Service Invoice",
  "layout_style": "creative_split",
  "colors": {
    "primary": "#DC2626",
    "header_background": "#DC2626",
    "accent": "#FEF3C7"
  },
  "header_style": {
    "type": "split",
    "height": "medium"
  },
  "layout_elements": {
    "side_panel": {"enabled": true, "position": "left"},
    "accent_bars": {"enabled": true, "thickness": "medium"}
  }
}
```

## Migration Notes

### Existing Templates
- Templates without `visual_config` will use automatic detection
- All existing endpoints continue to work unchanged
- Visual parameters are additive - no breaking changes

### Performance Considerations
- Mobile endpoint is optimized for thumbnail generation
- Response includes only essential visual data
- Consider caching templates locally for better performance

## Error Handling

### Common Error Responses

```json
{
  "detail": "Invalid template type: invalid_type",
  "status_code": 400
}
```

```json
{
  "detail": "Templates not found",
  "status_code": 404  
}
```

### Recommended Error Handling

```swift
do {
    let templates = try await fetchTemplates(type: "invoice")
    // Handle success
} catch APIError.invalidTemplateType {
    // Handle invalid type
} catch APIError.notFound {
    // Handle no templates found
} catch {
    // Handle other errors
}
```

## Testing

### Test Template Types
- `invoice` - Business invoices
- `estimate` - Project estimates  
- `contract` - Service contracts
- `proposal` - Business proposals

### Sample Test Cases

1. **Fetch Invoice Templates**
   ```
   GET /templates/mobile/invoice?is_active=true
   Expected: Array of invoice templates with visual parameters
   ```

2. **Verify Layout Styles**
   ```
   Verify each template has a valid layout_style
   Verify colors object contains required fields
   ```

3. **Test Thumbnail Generation**
   ```
   Use visual parameters to generate thumbnails
   Verify thumbnails are visually distinct
   ```

## Support

For questions about the template visual parameters API:

1. Check this documentation first
2. Review the OpenAPI specification at `/docs`
3. Contact the backend team for technical issues
4. Test with the provided sample templates

## Changelog

### Version 1.0.0 (2025-01-27)
- Initial release of enhanced template visual parameters
- Added mobile-optimized endpoint
- Implemented automatic layout style detection
- Added comprehensive visual configuration structure
