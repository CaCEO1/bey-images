#!/usr/bin/env python3
"""
GitHub Image Uploader
Upload images to GitHub and get direct URLs for them.
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

class GitHubImageUploader:
    def __init__(self, repo_name, github_username):
        """
        Initialize the uploader.

        Args:
            repo_name: Name of your GitHub repository
            github_username: Your GitHub username
        """
        self.repo_name = repo_name
        self.github_username = github_username
        self.repo_path = Path(__file__).parent
        self.images_dir = self.repo_path / "images"
        self.images_dir.mkdir(exist_ok=True)

    def upload_image(self, image_path, custom_name=None):
        """
        Upload an image to GitHub and return its URL.

        Args:
            image_path: Path to the image file
            custom_name: Optional custom name for the image (default: original name)

        Returns:
            URL to access the image
        """
        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Determine the destination name
        if custom_name:
            if not Path(custom_name).suffix:
                # Add original extension if not provided
                custom_name = f"{custom_name}{image_path.suffix}"
            dest_name = custom_name
        else:
            dest_name = image_path.name

        # Copy image to images directory
        dest_path = self.images_dir / dest_name
        shutil.copy2(image_path, dest_path)
        print(f"✓ Copied {image_path.name} to images/{dest_name}")

        # Git add, commit, and push
        try:
            subprocess.run(["git", "add", f"images/{dest_name}"],
                         cwd=self.repo_path, check=True)
            subprocess.run(["git", "commit", "-m", f"Add image: {dest_name}"],
                         cwd=self.repo_path, check=True)
            subprocess.run(["git", "push"],
                         cwd=self.repo_path, check=True)
            print(f"✓ Pushed to GitHub")
        except subprocess.CalledProcessError as e:
            print(f"✗ Git error: {e}")
            print("Make sure you've set up your GitHub remote!")
            return None

        # Generate and return URL
        url = f"https://raw.githubusercontent.com/{self.github_username}/{self.repo_name}/main/images/{dest_name}"
        return url

def main():
    # Configuration - UPDATE THESE!
    GITHUB_USERNAME = "your-username"  # Change this to your GitHub username
    REPO_NAME = "ebay-images"          # Change this to your repo name

    if GITHUB_USERNAME == "your-username":
        print("⚠️  Please edit this script and set your GITHUB_USERNAME and REPO_NAME")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python upload_image.py <image_path> [custom_name]")
        print("Example: python upload_image.py photo.jpg")
        print("Example: python upload_image.py photo.jpg product-123")
        sys.exit(1)

    image_path = sys.argv[1]
    custom_name = sys.argv[2] if len(sys.argv) > 2 else None

    uploader = GitHubImageUploader(REPO_NAME, GITHUB_USERNAME)
    url = uploader.upload_image(image_path, custom_name)

    if url:
        print(f"\n✓ Image URL:")
        print(f"  {url}")
        print(f"\nYou can now use this URL anywhere!")

if __name__ == "__main__":
    main()
