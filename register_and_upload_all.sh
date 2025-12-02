#!/bin/bash

# Register all SKUs and upload all products in EBAY_DATA_1
# Two-phase process: 1) Register SKUs, 2) Upload images

echo "Phase 1: Registering all SKUs in generated_skus.csv..."
echo ""

# Temporary file for new entries
temp_skus=$(mktemp)

for dir in EBAY_DATA_1/PRODUCT_*; do
  product=$(basename "$dir")

  # Get SKU from first image filename
  first_image=$(ls "$dir" | head -1)
  sku=$(echo "$first_image" | cut -d'_' -f1)

  # Create entry: product_folder,sku,product_title (placeholder)
  echo "EBAY_DATA_1/$product,$sku,Product to be cataloged" >> "$temp_skus"
  echo "  Registered: EBAY_DATA_1/$product -> $sku"
done

# Append to generated_skus.csv
cat "$temp_skus" >> generated_skus.csv
rm "$temp_skus"

echo ""
echo "Phase 1 Complete! All SKUs registered."
echo ""
echo "Phase 2: Uploading images to GitHub..."
echo ""

success_count=0
fail_count=0

for dir in EBAY_DATA_1/PRODUCT_*; do
  product=$(basename "$dir")
  first_image=$(ls "$dir" | head -1)
  sku=$(echo "$first_image" | cut -d'_' -f1)

  echo "[$((success_count + fail_count + 1))/26] Uploading $product (SKU: $sku)..."

  if python3 batch_upload_product.py "$sku" 2>&1 | grep -q "successfully"; then
    echo "✓ Success: $sku uploaded"
    ((success_count++))
  else
    echo "✗ Failed: $sku upload failed"
    ((fail_count++))
  fi

  echo ""
done

echo "========================================="
echo "Upload Complete!"
echo "Success: $success_count products"
echo "Failed: $fail_count products"
echo "========================================="
