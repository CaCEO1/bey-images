# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**ebay_test** - eBay product listing management system with GitHub-based image hosting. This repository manages product data, images, and automated workflows for creating eBay draft listings.

## Workflow Overview

**Complete Single-Product Processing Pipeline:**

For each product in a source directory (EBAY_DATA_1/PRODUCT_*, Package4/PRODUCT_*, Pack2/PRODUCT_*):

1. **Image Optimization** (if needed)
   - Use `image-downscaler` agent for images >1.5MB or HEIC format
   - Converts to .jpg, optimizes size to 100-300KB
   - Confirms before overwriting files in source directory

2. **SKU Assignment & GitHub Upload**
   - Use `batch-sku-image-processor` agent
   - Generates unique 8-character SKU (or retrieves existing from `generated_skus.csv`)
   - Adds brief product description to `generated_skus.csv`
   - Renames images to `{SKU}_1.jpg`, `{SKU}_2.jpg`, etc.
   - Runs `python3 batch_upload_product.py {SKU}` to upload to GitHub
   - Updates `product_image_urls.csv` with GitHub URLs

3. **Detailed Product Cataloging**
   - Use `ebay-product-cataloger` agent with batch_number (e.g., batch_number=0)
   - Creates `batch_{n}/{SKU}/` directory if it doesn't exist
   - **Processes images ONE AT A TIME**:
     - Reads single image
     - Extracts all visible details
     - Appends to `batch_{n}/{SKU}/{SKU}_image_data.txt`
     - Repeats for each image
   - Uses accumulated image data to:
     - Identify product accurately
     - Research pricing and category
     - Generate SEO title and HTML description
   - **Updates `generated_skus.csv`** with accurate product_title
   - Creates `batch_{n}/{SKU}/{SKU}_ebay_listing.csv`
   - Copies images to `image_db/{SKU}|{accurate_product_name}/`

4. **Agent Termination**
   - Agent exits after completing ONE product
   - Start new agent instance for next product

**Output Structure per Product:**
```
batch_0/{SKU}/{SKU}_image_data.txt          # Accumulated image analysis
batch_0/{SKU}/{SKU}_ebay_listing.csv        # eBay File Exchange format listing
image_db/{SKU}|{product_name}/              # Local image backup
images/{SKU}_*.jpg                          # GitHub-hosted images
generated_skus.csv                          # Updated with accurate product_title
product_image_urls.csv                      # GitHub URLs for product
```

## Development Commands

### Image Upload

**Batch Upload (Recommended):**
```bash
# Upload all images for a product SKU and track URLs
python3 batch_upload_product.py A7K9RN42

# This will:
# 1. Find all images for the SKU in Package4/
# 2. Upload them to GitHub in order
# 3. Append URLs to product_image_urls.csv
```

**Single Image Upload:**
```bash
# Upload a single image to GitHub (must configure GITHUB_USERNAME and REPO_NAME in script first)
python3 upload_image.py path/to/image.jpg

# Upload with custom name
python3 upload_image.py path/to/image.jpg custom-name
```

### Single-Product Processing (Current System)

**Two-Agent Workflow** (Single-Product Architecture):

The workflow uses two specialized agents that process ONE product at a time, then exit:

**Step 1: SKU Assignment & Image Upload**
Use the `batch-sku-image-processor` agent (Green) to process a SINGLE product directory:
- Generates unique 8-character SKU for ONE product
- Quick product identification (brief title for tracking)
- Checks for oversized images (>1.5MB) and invokes image-downscaler if needed
- Renames images to SKU format (`{SKU}_1.jpg`, `{SKU}_2.jpg`, etc.)
- Uploads images to GitHub CDN
- Updates `generated_skus.csv` and `product_image_urls.csv`
- Reports completion and EXITS

**Step 2: Detailed Cataloging**
Use the `ebay-product-cataloger` agent (Red) to create eBay listing for ONE product:
- **CRITICAL**: Process images ONE AT A TIME (never batch read)
- For EACH image in the product directory:
  1. Read the single image
  2. Extract all visible details (brand, model, part numbers, connectors, condition)
  3. Append findings to `batch_{n}/{SKU}/{SKU}_image_data.txt`
  4. Move to next image
- After ALL images processed, use accumulated `{SKU}_image_data.txt` to:
  - Perform deep product identification and research
  - Select eBay category and determine competitive pricing
  - Generate SEO-optimized title (80 chars max)
  - Create comprehensive HTML description (1,500-3,000 words)
  - Update `generated_skus.csv` with accurate product_title
- Creates individual CSV file: `batch_{n}/{SKU}/{SKU}_ebay_listing.csv`
- Copies images to `image_db/{SKU}|{accurate_product_name}/`
- Reports completion and EXITS

**Example Usage:**
```bash
# Full pipeline for one product (batch_0 processing session)
1. Use image-downscaler agent on EBAY_DATA_1/PRODUCT_7 (if images >1.5MB)
2. Use batch-sku-image-processor agent on EBAY_DATA_1/PRODUCT_7
3. Use ebay-product-cataloger agent on EBAY_DATA_1/PRODUCT_7 with batch_number=0

# Output structure:
# - batch_0/{SKU}/{SKU}_image_data.txt (accumulated image analysis)
# - batch_0/{SKU}/{SKU}_ebay_listing.csv (individual product listing)
# - image_db/{SKU}|{accurate_product_name}/ (local image backup)
```

**Key Points:**
- **Each agent processes EXACTLY ONE product directory**
- **Each product gets its own subdirectory** in `batch_{n}/{SKU}/`
- **Images processed ONE AT A TIME** by cataloger (no batch reading)
- **Agents EXIT after processing one product**
- **Clean error isolation** - errors affect only the current product
- **No batch operations** - run agents individually for each product

**Benefits:**
- Clear, predictable execution model
- No context bloat from batch processing
- Easy error recovery (re-run failed product only)
- Compartmentalized data: each SKU has its own directory with analysis + listing
- Can consolidate all `{SKU}_ebay_listing.csv` files into one master CSV later
- Reduced agent complexity

Both agents are designed to run independently on individual products for maximum flexibility and error isolation.

**Legacy Scripts (Deprecated):**
```bash
# These scripts update ebay_product_data.csv (no longer used)
python3 update_csv_urls.py          # Deprecated
python3 update_csv_all_images.py    # Deprecated
```

### Git Setup (First Time)
```bash
# Connect to GitHub repository (required before image uploads work)
git remote add origin https://github.com/YOUR-USERNAME/ebay-images.git
git branch -M main
git push -u origin main
```

## Architecture

### Directory Structure
```
ebay_test/
├── Package4/              # Product inventory - each PRODUCT_* folder contains images for one listing
│   ├── PRODUCT_1/        # Product images (SKU_1.jpg, SKU_2.jpg, etc.)
│   ├── PRODUCT_2/
│   ├── PRODUCT_3/
│   └── ...
├── Pack2/                # Additional product inventory
│   ├── PRODUCT_1/
│   ├── PRODUCT_2/
│   └── ...
├── EBAY_DATA_1/          # Additional product inventory
│   └── PRODUCT_*/
├── images/               # GitHub-hosted images (generated by upload scripts)
├── image_db/             # Local image backups (NOT uploaded to GitHub)
│   ├── {SKU}|{product_name}/  # One directory per product, searchable by SKU or name
│   │   ├── {SKU}_1.jpg
│   │   ├── {SKU}_2.jpg
│   │   └── ...
│   └── ...
├── batch_0/              # Batch processing directories (one per processing session)
│   ├── {SKU}/           # One subdirectory per product processed in this batch
│   │   ├── {SKU}_image_data.txt      # Accumulated image analysis (one image at a time)
│   │   └── {SKU}_ebay_listing.csv    # Individual product listing CSV
│   └── ...
├── batch_1/              # Subsequent batch directories
│   └── {SKU}/
├── upload_image.py       # Single image uploader with automatic URL generation
├── batch_upload_product.py  # Batch product image uploader by SKU
├── update_csv_urls.py    # Legacy - updates ebay_product_data.csv (deprecated)
├── update_csv_all_images.py  # Legacy - updates ebay_product_data.csv (deprecated)
├── generated_skus.csv    # SKU tracking: product_folder,sku,product_title
├── product_image_urls.csv   # Image URL tracking: product_sku,image_urls (JSON array)
└── ebay_product_data.csv # TEMPLATE ONLY - reference for format (DO NOT WRITE)
```

### Image Hosting System

The repository uses **GitHub as a free CDN** for product images:

1. **Local Storage**: Product images stored in `Package4/PRODUCT_*/` directories
2. **Upload Process**: `upload_image.py` copies images to `images/` folder, commits to git, and pushes to GitHub
3. **URL Generation**: Returns permanent public URLs in format:
   ```
   https://raw.githubusercontent.com/USERNAME/REPO/main/images/filename.jpg
   ```
4. **Integration**: URLs used directly in eBay listings via File Exchange CSV format

**Critical Configuration** (in upload_image.py:77-79):
```python
GITHUB_USERNAME = "your-username"  # Must update before first use
REPO_NAME = "ebay-images"          # Must match your GitHub repo name
```

### Product Image URL Tracking

**product_image_urls.csv** maintains a mapping of product SKUs to their GitHub-hosted image URLs.

**Format:**
```csv
product_sku,image_urls
A7K9RN42,"[""https://raw.githubusercontent.com/CaCEO1/bey-images/main/images/A7K9RN42_1.jpeg"",""https://raw.githubusercontent.com/CaCEO1/bey-images/main/images/A7K9RN42_2.jpeg""]"
```

**Key Features:**
- One row per product SKU
- `image_urls` column contains JSON array of all image URLs for that product
- URLs are in upload order (matching filename sequence: SKU_1, SKU_2, SKU_3, etc.)
- Generated automatically by `batch_upload_product.py`
- Used to update `ebay_product_data.csv` with proper image URLs

**Workflow:**
1. Rename images to SKU format: `{SKU}_{n}.{ext}`
2. Run batch upload: `python3 batch_upload_product.py A7K9RN42`
3. Script uploads all images and appends to `product_image_urls.csv`
4. Agent processes images ONE AT A TIME, accumulating data in `batch_{n}/{SKU}/{SKU}_image_data.txt`
5. Agent creates `batch_{n}/{SKU}/{SKU}_ebay_listing.csv` (individual product listing)
6. Agent updates `generated_skus.csv` with accurate product_title
7. Agent copies images to `image_db/{SKU}|{accurate_product_name}/` (local backup)

### Batch Processing System

**CRITICAL**: The system uses isolated batch directories for scalability. Each processing session gets its own numbered batch directory.

**Key Concepts:**
- **batch_{n}/** - Directory for each processing session (batch_0, batch_1, etc.)
  - Contains one subdirectory per SKU processed in that batch
  - Each SKU subdirectory contains:
    - `{SKU}_image_data.txt` - Accumulated image analysis (one image at a time)
    - `{SKU}_ebay_listing.csv` - Individual product listing in eBay File Exchange format
- **ebay_product_data.csv** - TEMPLATE ONLY (read for format reference, never write)
- **image_db/** - Local searchable image repository (NOT uploaded to GitHub)
  - Directory naming: `{SKU}|{accurate_product_name}/`

**Batch Structure:**
```
batch_0/
├── A7K9RN42/
│   ├── A7K9RN42_image_data.txt
│   └── A7K9RN42_ebay_listing.csv
├── B3C27CW8/
│   ├── B3C27CW8_image_data.txt
│   └── B3C27CW8_ebay_listing.csv
└── ...

batch_1/
├── C8MPGM14/
│   ├── C8MPGM14_image_data.txt
│   └── C8MPGM14_ebay_listing.csv
└── ...
```

**Benefits:**
- **Scalability**: Address issues in batch 5 without loading batches 0-4
- **Context Efficiency**: Reference specific batch/SKU directories in conversations
- **Compartmentalization**: Each product has its own isolated directory with all data
- **Easy Consolidation**: Scan all `{SKU}_ebay_listing.csv` files to create master CSV
- **PostgreSQL Ready**: Consistent format for future database import
- **Searchability**: Find images by SKU or product name in `image_db/`

### CSV Data Format

**ebay_product_data.csv** is a TEMPLATE ONLY - use for format reference, DO NOT WRITE to this file.

**Individual Product CSV Files** (`batch_{n}/{SKU}/{SKU}_ebay_listing.csv`):
Each product gets its own CSV file in eBay File Exchange format containing:
- Product metadata (SKU, Category ID, Title, UPC, Price, Quantity)
- Image URLs (pipe-separated GitHub URLs)
- Condition codes (3000 = Used, 1000 = New)
- Full HTML descriptions with specifications, compatibility lists, and marketing copy
- Format type (FixedPrice)

All individual CSVs follow eBay File Exchange template format v0.0.2 with required headers and info rows.

**Consolidation**: These individual CSV files can be consolidated into a master CSV by scanning all `batch_*/{SKU}/{SKU}_ebay_listing.csv` files and combining their data rows.

### Product Categories

The inventory includes diverse product types:
- **Server Components**: Dell PowerEdge power supplies (R610, R730, R630, R540)
- **Storage Hardware**: Dell Compellent/EqualLogic components (batteries, PSUs, enclosures)
- **Consumer Electronics**: Breville Nespresso Creatista Pro espresso machine

Each product has enterprise-grade HTML descriptions with detailed specifications, compatibility matrices, and condition disclosures.

## Important Conventions

### SKU Generation and Management

**CRITICAL**: Each product in Package4/ directories must be assigned a unique SKU before processing.

**SKU Requirements:**
- **Format**: 8-character alphanumeric string (A-Z, 0-9)
- **Uniqueness**: Must be unique across all products
- **Tracking**: All generated SKUs stored in `generated_skus.csv`
- **Validation**: Always check `generated_skus.csv` before generating new SKUs to prevent duplicates

**generated_skus.csv Format:**
```csv
product_folder,sku,product_title
PRODUCT_1,A7K9RN42,Dell PowerEdge R610 717W Power Supply
PRODUCT_2,B3C27CW8,Dell Compellent Battery Module 11.1V
```

**Important Notes:**
- The `product_title` field is initially set to a brief description during SKU generation
- **CRITICAL**: The `ebay-product-cataloger` agent MUST update this field with the accurate, detailed product name after image analysis
- This ensures `generated_skus.csv` serves as an accurate index for all products
- The accurate product_title is used for `image_db/{SKU}|{accurate_product_title}/` directory naming

**Current SKU Assignments:**
See `generated_skus.csv` for complete list. As of Batch 0 (proto import):
- Package4/PRODUCT_1: `A7K9RN42` (Dell PowerEdge R610 717W PSU)
- Package4/PRODUCT_2: `B3C27CW8` (Dell Compellent Battery)
- Package4/PRODUCT_3: `D5DD20N7` (Dell EqualLogic 700W PSU)
- Package4/PRODUCT_4: `C8MPGM14` (Dell PowerEdge 1100W PSU)
- Package4/PRODUCT_5: `E6NE800B` (Breville Nespresso Creatista Pro)
- Pack2/PRODUCT_1: `3YGFIYIF` (Samsung 16GB DDR4 RAM)
- Pack2/PRODUCT_2: `9UVLEVFW` (Sony PS5 DualSense Controller)

**Batch Documentation:**
- Batch 0: See `proto_import.md` for details on all 7 retroactively migrated products
- Batch 1+: See `batch_processing_{n}.md` for each new batch

### Image File Naming
- Product folders: `PRODUCT_1`, `PRODUCT_2`, etc.
- **Required format**: `{SKU}_{n}.{extension}` where:
  - `{SKU}` = 8-character product SKU from generated_skus.csv
  - `{n}` = sequential image number (1, 2, 3, ...)
  - `{extension}` = original file extension (jpg, jpeg, png)
- **Examples**:
  - `A7K9RN42_1.jpeg` (first image for PRODUCT_1)
  - `A7K9RN42_2.jpeg` (second image for PRODUCT_1)
  - `B3C27CW8_1.jpeg` (first image for PRODUCT_2)
- GitHub upload should preserve SKU-based filenames for consistency

### Local Image Database (image_db/)
- **Directory naming**: `{SKU}|{product_name}/` format for searchability
- **Example**: `image_db/A7K9RN42|Dell PowerEdge R610 717W Power Supply/`
- **Purpose**: Local backup, searchable by SKU or product name
- **Important**: This directory is in `.gitignore` and NOT uploaded to GitHub
- **Contents**: Copies of all product images with SKU-based filenames

### eBay Category IDs
Reference: https://pages.ebay.com/sellerinformation/news/categorychanges.html
- 175673: Server components (power supplies, hardware)
- 38072: Storage components (batteries, controllers)
- 20677: Small kitchen appliances (espresso machines)

### HTML Description Standards
Product descriptions in CSV use inline HTML with:
- Bold headers with `<b>` tags
- Unordered lists `<ul><li>` for specifications
- Part number variations listed prominently
- Compatibility matrices for enterprise hardware
- Condition disclosures with "Used - [detailed condition]"
- Feature benefits and use cases

### Git Workflow for Images
Each image upload creates an individual commit with message format:
```
Add image: filename.jpg
```

The script auto-commits and pushes - no manual git commands needed after initial setup.

## Critical Workflow Rules (Gemini Learnings)

These rules are based on lessons learned from the Gemini processing workflow:

### 1. Image Processing - ONE AT A TIME
- **NEVER batch read** multiple product images at once
- For each image in the product directory:
  1. Read the SINGLE image
  2. Extract ALL visible details meticulously
  3. Append findings to `batch_{n}/{SKU}/{SKU}_image_data.txt`
  4. Move to next image
- After ALL images processed, use accumulated txt file to build listing
- **Rationale**: Prevents assumptions and inaccuracies (e.g., HDMI male vs. female, Intel vs. Cisco branding)

### 2. SKU Status Verification
- **NEVER assume** SKU in CLAUDE.md means completion
- Always verify actual filesystem state:
  - Check `generated_skus.csv` for SKU entry
  - Check `images/` directory for uploaded images
  - Check `product_image_urls.csv` for URL entries
- If incomplete, run full `batch-sku-image-processor` workflow

### 3. Product Title Accuracy
- Initial `product_title` in `generated_skus.csv` is often generic ("Product to be cataloged")
- **CRITICAL**: `ebay-product-cataloger` MUST update this with accurate name after detailed analysis
- Accurate title used for `image_db/{SKU}|{accurate_title}/` directory naming

### 4. Image Extension Handling
- Downscaling .jpeg → .jpg requires explicit Git steps:
  1. Remove original .jpeg files from filesystem
  2. Remove .jpeg files from Git staging (`git rm`)
  3. Add new .jpg files (`git add`)
  4. Commit changes
  5. Push to GitHub
  6. Update `product_image_urls.csv` to reflect .jpg extensions

### 5. Agent Lifecycle
- Each agent processes EXACTLY ONE product
- Agent EXITS/terminates after product completion
- Start NEW agent instance for next product
- **Rationale**: Clean error isolation, no context bloat

### 6. Batch Directory Structure
- Each processing session creates `batch_{n}/` directory if it doesn't exist
- Each SKU gets subdirectory: `batch_{n}/{SKU}/`
- Each SKU subdirectory contains:
  - `{SKU}_image_data.txt` (accumulated analysis)
  - `{SKU}_ebay_listing.csv` (individual listing)
- Compartmentalized data enables easy consolidation later

## Setup Checklist

Before using this repository:
1. Create a **public** GitHub repository (private repos won't work for direct image URLs)
2. Configure git remote: `git remote add origin https://github.com/USERNAME/REPO.git`
3. Edit `upload_image.py` lines 78-79 with your GitHub username and repo name
4. Push initial commit to GitHub
5. Test image upload: `python upload_image.py Package4/PRODUCT_1/image1.jpg test-upload`
