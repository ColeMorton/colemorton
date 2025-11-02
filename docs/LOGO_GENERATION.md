# Brand Logo Generation System

**Version**: 2.1 | **Last Updated**: 2024-09-24 | **Status**: Active
**Authority**: Design Team | **Audience**: Designers & Developers

This document outlines how to generate high-quality brand logo images identical to the h1 brand-text in the frontend header using the existing photo booth screenshot system.

## Overview

The logo generation system leverages the existing photo booth infrastructure to capture pixel-perfect logo images with multiple formats, resolutions, and theme variants. This ensures complete visual consistency with the current brand implementation.

## Current Brand Specification

**Text**: "Cole Morton"
**Font**: Paytone One (Google Font)
**CSS Classes**: `brand-text m-0 font-semibold`
**Special Styling**:
```css
.brand-text {
  font-family: var(--font-brand), sans-serif !important;
  display: flex;
  align-items: center;
  transform: translateY(-5px);
}
```

**Theme Colors**:
- Light mode: `#1A1A1A`
- Dark mode: `#F9FAFB`

## System Components

### 1. Logo Generation Dashboard
**File**: `frontend/src/content/dashboards/logo-generation.mdx`

Contains multiple logo variants optimized for different use cases:
- Large version (text-6xl to text-9xl) for high-resolution captures
- Medium version (text-4xl to text-6xl) for standard use
- Small version (text-2xl to text-4xl) for compact applications
- Horizontal layout with tagline space for future expansion

### 2. Logo Display Component
**File**: `frontend/src/layouts/components/LogoDisplay.tsx`

Reusable React component that renders the brand text with exact styling:
- Configurable sizes (small, medium, large, xl)
- Theme-aware colors
- Optional background for different contexts
- Consistent with header logo implementation

### 3. Photo Booth Configuration
**File**: `frontend/src/config/photo-booth.json`

Logo generation dashboard is registered as:
```json
{
  "id": "logo_generation",
  "name": "Logo Generation Dashboard",
  "file": "logo-generation.mdx",
  "description": "Brand logo generation with multiple sizes and formats",
  "layout": "logo_variants",
  "enabled": true
}
```

### 4. Logo Generation Helper Script
**File**: `scripts/generate_logos.py`

Automated script for generating complete logo sets with predefined configurations.

## Usage

### Method 1: Using the Helper Script (Recommended)

1. **Start the development server**:
   ```bash
   cd frontend && yarn dev
   ```

2. **Generate all logo variants**:
   ```bash
   python3 scripts/generate_logos.py
   ```

3. **Generate specific variants**:
   ```bash
   # PNG only at 300 DPI
   python3 scripts/generate_logos.py --formats png --sizes 300

   # Dark theme only
   python3 scripts/generate_logos.py --themes dark

   # High resolution only (600 DPI)
   python3 scripts/generate_logos.py --sizes 600
   ```

4. **Organize existing files**:
   ```bash
   python3 scripts/generate_logos.py --organize
   ```

### Method 2: Manual Photo Booth Generation

1. **Start the development server**:
   ```bash
   cd frontend && yarn dev
   ```

2. **Access photo booth interface**:
   - Visit `http://localhost:4321/photo-booth`
   - Select "Logo Generation Dashboard" from dropdown
   - Choose desired format, resolution, and theme
   - Click "Export Dashboard"

3. **Direct API call**:
   ```bash
   curl -X POST http://localhost:4321/api/export-dashboard \
     -H "Content-Type: application/json" \
     -d '{
       "dashboard_id": "logo_generation",
       "mode": "light",
       "aspect_ratio": "16:9",
       "format": "png",
       "dpi": 300,
       "scale_factor": 3
     }'
   ```

### Method 3: Direct Python Script

```bash
python3 scripts/photo_booth_generator.py \
  --dashboard logo_generation \
  --mode light \
  --aspect-ratio 16:9 \
  --format png \
  --dpi 300 \
  --scale-factor 3 \
  --base-url http://localhost:4321
```

## Output Formats

### Standard Configurations

The helper script generates these predefined logo variants:

| Use Case | Format | DPI | Scale | Aspect | Theme |
|----------|--------|-----|-------|--------|--------|
| Web Light | PNG | 150 | 2x | 16:9 | Light |
| Web Dark | PNG | 150 | 2x | 16:9 | Dark |
| Print Light | PNG | 300 | 3x | 16:9 | Light |
| Print Dark | PNG | 300 | 3x | 16:9 | Dark |
| Ultra Light | PNG | 600 | 4x | 16:9 | Light |
| Ultra Dark | PNG | 600 | 4x | 16:9 | Dark |
| Vector Light | SVG | 300 | 3x | 16:9 | Light |
| Vector Dark | SVG | 300 | 3x | 16:9 | Dark |
| Portrait Light | PNG | 300 | 3x | 3:4 | Light |
| Portrait Dark | PNG | 300 | 3x | 3:4 | Dark |

### Output Locations

- **Raw outputs**: `data/outputs/photo-booth/`
- **Organized outputs**: `data/outputs/logos/`

Organized files use the naming pattern: `cole_morton_logo_{theme}_{dpi}_{aspect}.{format}`

Example: `cole_morton_logo_light_300dpi_16x9.png`

## File Organization

After generation, logos are automatically organized into a clean structure:

```
data/outputs/logos/
├── cole_morton_logo_light_150dpi_16x9.png    # Web use
├── cole_morton_logo_dark_150dpi_16x9.png     # Web use (dark)
├── cole_morton_logo_light_300dpi_16x9.png    # Print quality
├── cole_morton_logo_dark_300dpi_16x9.png     # Print quality (dark)
├── cole_morton_logo_light_600dpi_16x9.png    # Ultra high-res
├── cole_morton_logo_dark_600dpi_16x9.png     # Ultra high-res (dark)
├── cole_morton_logo_light_300dpi_16x9.svg    # Vector (scalable)
├── cole_morton_logo_dark_300dpi_16x9.svg     # Vector (scalable, dark)
├── cole_morton_logo_light_300dpi_3x4.png     # Portrait/social
└── cole_morton_logo_dark_300dpi_3x4.png      # Portrait/social (dark)
```

## Integration with Existing Logo System

### Option 1: Replace Text Logo with Image
Update `frontend/src/layouts/components/Logo.astro` to use generated images:

```astro
{
  src || srcDarkmode || logo || logo_darkmode ? (
    // Existing image logo logic
  ) : logo_text ? (
    <img
      src="/images/logos/cole_morton_logo_light_150dpi_16x9.png"
      class="dark:hidden h-8 w-auto"
      alt={logo_text}
    />
    <img
      src="/images/logos/cole_morton_logo_dark_150dpi_16x9.png"
      class="hidden dark:inline-block h-8 w-auto"
      alt={logo_text}
    />
  ) : (
    // Fallback to text
  )
}
```

### Option 2: Hybrid Approach
Keep text logo for web, use image logos for external applications (presentations, social media, print materials).

## Quality Assurance

### Pixel-Perfect Accuracy
- Uses identical CSS styling from current implementation
- Same Paytone One font loading
- Exact color values from theme configuration
- Same `translateY(-5px)` transform applied

### Multi-Format Support
- **PNG**: Raster format with transparency, ideal for most uses
- **SVG**: Vector format, infinitely scalable, small file size
- **Multiple DPI**: 150 (web), 300 (print), 600 (ultra-high quality)

### Theme Consistency
- Light theme: `#1A1A1A` text color
- Dark theme: `#F9FAFB` text color
- Transparent backgrounds for flexible usage
- Theme switching maintains visual consistency

## Troubleshooting

### Server Connection Issues
```bash
# Check if development server is running
curl -I http://localhost:4321/

# If server is on different port
lsof -i :4321 -i :4322 -i :4323 | grep LISTEN

# Use correct port in generation commands
python3 scripts/generate_logos.py --base-url http://localhost:4322
```

### Font Loading Issues
- Ensure Paytone One font is loaded via Google Fonts
- Check `--font-brand` CSS variable is properly set
- Verify `.brand-text` CSS class is applied

### Generation Failures
```bash
# Run with verbose logging
python3 scripts/generate_logos.py --verbose

# Test individual component
python3 scripts/photo_booth_generator.py --help
```

### File Organization
```bash
# Manually organize existing files
python3 scripts/generate_logos.py --organize

# Check output locations
ls -la data/outputs/photo-booth/ | grep logo_generation
ls -la data/outputs/logos/
```

## Maintenance

### Updating Logo Design
If the brand text styling changes:

1. Update styles in CSS/components as normal
2. Regenerate logos: `python3 scripts/generate_logos.py`
3. Copy new logos to appropriate locations
4. Update any hardcoded logo references

### Adding New Formats
Edit `scripts/generate_logos.py` and add new configurations to the `self.configurations` list:

```python
{
  "mode": "light",
  "format": "webp",  # New format
  "dpi": 300,
  "scale": 3,
  "aspect": "16:9",
  "use_case": "webp_light"
}
```

### Batch Operations
```bash
# Generate only web formats
python3 scripts/generate_logos.py --formats png --sizes 150

# Generate only print formats
python3 scripts/generate_logos.py --sizes 300

# Generate only dark theme
python3 scripts/generate_logos.py --themes dark
```

## Best Practices

1. **Always test locally** before using in production
2. **Use organized outputs** from `data/outputs/logos/` rather than raw photo booth files
3. **Choose appropriate DPI** for use case (150 web, 300 print, 600 ultra)
4. **Use PNG with transparency** for most applications
5. **Use SVG** for scalable applications (web icons, vector graphics)
6. **Keep both themes** available for flexible usage
7. **Regenerate after styling changes** to maintain consistency

## Support

For issues or questions:
- Check the troubleshooting section above
- Review existing photo booth documentation
- Examine generated files in `data/outputs/` directories
- Test individual components before running full generation
