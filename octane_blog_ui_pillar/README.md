# Octane Blog 3-Column Pillar UI Architecture

This directory preserves the exact source code, layout configuration, and CSS stylesheet for the Octane blog UI.

## Layout Overview
- Left Column: Sticky Blog Reading Tracker showing which article the user is currently reading.
- Center Column: Main Article Body with Roboto typography, clear paragraph spacing, and centered content.
- Right Column: Secondary sidebar elements and navigation.

## HubSpot Template Details
- Template / Layout ID: 65127478077
- Blog Post Module Name: module_151388194052436
- Injected Stylesheet: template_Octane_2022_Stylesheet.min.css
- Google Font: Roboto (weights 300, 400, 500, 700, 900)

## Included Files
1. widget_blog_post_source.html: The complete HubL and HTML template containing the 3-column layout structure and the reading tracker.
2. widget_blog_listing_source.html: The HubL listing template.
3. template_Octane_2022_Stylesheet.min.css: The exact 49.4 KB minified CSS stylesheet loaded by the blog.
4. layout_65127478077_tree.json: The complete JSON tree exported directly from the HubSpot Layouts API.
5. restore_blog_ui_to_hubspot.py: Standalone Python script to re-apply this exact UI layout to HubSpot anytime.
