import os
import sys
import csv
import json
from pathlib import Path
from tools.upload_image import GitHubImageUploader

# Configuration
GITHUB_USERNAME = "CaCEO1"  # Set your GitHub username
REPO_NAME = "bey-images"  # Set your GitHub repository name

def find_product_folder(sku, generated_skus_csv="PROJECT_DATA/generated_skus.csv"):
    """Find the product folder for a given SKU."""
    if not Path(generated_skus_csv).exists():
        raise FileNotFoundError(f"SKU tracking file not found: {generated_skus_csv}")

    with open(generated_skus_csv, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['sku'] == sku:
                return row['product_folder']

    raise ValueError(f"SKU '{sku}' not found in {generated_skus_csv}")

def get_product_images(product_folder, base_path="Package4"):
    """Get all image files for a product, sorted by filename."""
    # Handle full paths (e.g., EBAY_DATA_1/PRODUCT_2)
    if '/' in product_folder:
        product_path = Path(product_folder)
    else:
        product_path = Path(base_path) / product_folder

    if not product_path.exists():
        raise FileNotFoundError(f"Product folder not found: {product_path}")

    # Find all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif']
    images = []

    for ext in image_extensions:
        images.extend(product_path.glob(f"*{ext}"))
        images.extend(product_path.glob(f"*{ext.upper()}"))

    # Sort by filename to ensure consistent ordering
    return sorted(images, key=lambda x: x.name)

def upload_product_images(sku, product_folder_override=None):
    """Upload all images for a product SKU and return URLs."""
    # Configuration
    # These are already defined globally or inferred from the uploader class.
    # GITHUB_USERNAME = "CaCEO1"
    # REPO_NAME = "bey-images"

    # Find product folder
    if product_folder_override:
        product_folder = product_folder_override
    else:
        product_folder = find_product_folder(sku)
    print(f"📦 Processing {product_folder} (SKU: {sku})")

    # Get all images
    images = get_product_images(product_folder)

    if not images:
        print(f"⚠️  No images found for {product_folder}")
        return []

    print(f"Found {len(images)} image(s)")

    # Initialize uploader
    uploader = GitHubImageUploader(REPO_NAME, GITHUB_USERNAME)

    # Upload each image
    urls = []
    for i, image_path in enumerate(images, 1):
        print(f"\n[{i}/{len(images)}] Uploading {image_path.name}...")

        # Upload with original filename (should already be in SKU_n format)
        url = uploader.upload_image(str(image_path), image_path.stem)

        if url:
            urls.append(url)
            print(f"✓ Uploaded: {url}")
        else:
            print(f"✗ Failed to upload {image_path.name}")

    return urls

def save_urls_to_csv(sku, urls, csv_file="PROJECT_DATA/product_image_urls.csv"):
    """Save product SKU and image URLs to CSV file."""
    csv_path = Path(csv_file)
    file_exists = csv_path.exists()

    # Read existing data to check for duplicates
    existing_skus = set()
    if file_exists:
        with open(csv_path, 'r') as f:
            reader = csv.DictReader(f)
            existing_skus = {row['product_sku'] for row in reader}

    # Format URLs as JSON array string
    urls_json = json.dumps(urls)

    # Append to CSV
    with open(csv_path, 'a', newline='') as f:
        writer = csv.writer(f)

        # Write header if new file
        if not file_exists:
            writer.writerow(['product_sku', 'image_urls'])

        # Check if SKU already exists
        if sku in existing_skus:
            print(f"\n⚠️  Warning: SKU '{sku}' already exists in {csv_file}")
            print(f"   The new URLs will be appended as a duplicate entry.")
            print(f"   You may want to manually edit the CSV to update the existing entry.")

        # Write data
        writer.writerow([sku, urls_json])

    print(f"\n✓ Saved URLs to {csv_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python batch_upload_product.py <SKU> [product_folder]")
        print("\nExample: python batch_upload_product.py A7K9RN42")
        print("Example with product folder: python batch_upload_product.py A7K9RN42 Package4/PRODUCT_1")
        print("\nThis will:")
        print("  1. Find all images for the product SKU (or use provided product_folder)")
        print("  2. Upload them to GitHub")
        print("  3. Save URLs to product_image_urls.csv")
        sys.exit(1)

    sku = sys.argv[1].upper()
    product_folder_arg = None
    if len(sys.argv) >= 3:
        product_folder_arg = sys.argv[2] # Optional product_folder argument

    try:
        # Upload all images
        urls = upload_product_images(sku, product_folder_arg) # Pass product_folder_arg

        if urls:
            # Save to CSV
            save_urls_to_csv(sku, urls)

            print(f"\n{'='*60}")
            print(f"✓ Successfully uploaded {len(urls)} image(s) for SKU: {sku}")
            print(f"{'='*60}")
            print("\nImage URLs:")
            for i, url in enumerate(urls, 1):
                print(f"  {i}. {url}")
        else:
            sys.stderr.write(f"\n✗ No images were uploaded for SKU: {sku}\n")
            sys.exit(1)

    except Exception as e:
        sys.stderr.write(f"\n✗ Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
