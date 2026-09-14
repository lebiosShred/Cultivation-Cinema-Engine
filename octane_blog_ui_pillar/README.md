# Octane Blog 3-Column Pillar UI Architecture

This directory preserves the exact source code, layout configuration, and CSS stylesheet for the Octane blog UI.

## Layout Overview
- Left Column: Sticky Blog Reading Tracker showing which article the user is currently reading.
- Center Column: Main Article Body with Roboto typography, clear paragraph spacing, and centered content.
- Right Column: Secondary sidebar elements and navigation.

## HubSpot Template Details
- Blog Post Layout ID: 65127478077 (Octane Blog Post 2022)
- Blog Listing Layout ID: 65124426908 (Octane Blog Listing 2022)
- Blog Module Name: module_151388194052436
- Injected Stylesheet: template_Octane_2022_Stylesheet.min.css
- Google Font: Roboto (weights 300, 400, 500, 700, 900)

## Included Files
1. widget_blog_post_source.html: The complete HubL and HTML template containing the 3-column layout structure and the reading tracker.
2. widget_blog_listing_source.html: The original HubL listing template.
3. layout_65124426908_blog_listing_source.html: The live HubL listing template in layout 65124426908 with SEO crawlable pagination (pages 1 to 9).
4. template_Octane_2022_Stylesheet.min.css: The exact 49.4 KB minified CSS stylesheet loaded by the blog.
5. layout_65127478077_tree.json: The complete JSON tree exported directly from the HubSpot Layouts API.
6. restore_blog_ui_to_hubspot.py: Standalone Python script to re-apply this exact UI layout to HubSpot anytime.
