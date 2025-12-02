# GitHub Image Hosting Setup

## Quick Setup (5 minutes)

### 1. Create a GitHub Repository

Go to https://github.com/new and create a new **public** repository:
- Name: `ebay-images` (or whatever you want)
- Make sure it's **PUBLIC** (private repos won't work for direct URLs)
- Don't initialize with README

### 2. Connect This Folder to GitHub

```bash
cd ~/ebay_test
git remote add origin https://github.com/YOUR-USERNAME/ebay-images.git
git branch -M main
git add .
git commit -m "Initial commit"
git push -u origin main
```

### 3. Configure the Upload Script

Edit `upload_image.py` and change these lines:
```python
GITHUB_USERNAME = "your-username"  # Your actual GitHub username
REPO_NAME = "ebay-images"          # Your repo name
```

### 4. Upload an Image

```bash
python upload_image.py path/to/your/image.jpg
```

Or with a custom name:
```bash
python upload_image.py photo.jpg product-001
```

This will output a URL like:
```
https://raw.githubusercontent.com/YOUR-USERNAME/ebay-images/main/images/product-001.jpg
```

## Usage Examples

```python
# In your Python code:
from upload_image import GitHubImageUploader

uploader = GitHubImageUploader("ebay-images", "your-username")
url = uploader.upload_image("product.jpg", "product-123")
print(url)
# Output: https://raw.githubusercontent.com/your-username/ebay-images/main/images/product-123.jpg
```

## Notes

- Images are stored in the `images/` folder
- Each upload creates a new git commit
- URLs are permanent and publicly accessible
- Free unlimited storage (within GitHub's reasonable use policy)
- Works great for product images, thumbnails, etc.

## Troubleshooting

**"Please edit this script and set your GITHUB_USERNAME"**
- Edit upload_image.py and change the configuration variables

**"Git error"**
- Make sure you've pushed to GitHub at least once
- Check that your git remote is set up: `git remote -v`

**"Permission denied"**
- Make sure the script is executable: `chmod +x upload_image.py`
- Or run with: `python upload_image.py image.jpg`
