#!/bin/bash

# Upload all products in EBAY_DATA_1 to GitHub
# Script processes 26 products sequentially

echo "Starting bulk upload for EBAY_DATA_1 products..."
echo "Total products to process: 26"
echo ""

success_count=0
fail_count=0

for dir in EBAY_DATA_1/PRODUCT_*; do
  product=$(basename "$dir")

  # Get SKU from first image filename
  first_image=$(ls "$dir" | head -1)
  sku=$(echo "$first_image" | cut -d'_' -f1)

  echo "[$((success_count + fail_count + 1))/26] Processing $product (SKU: $sku)..."

  # Run batch upload
  if python3 batch_upload_product.py "$sku"; then
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
