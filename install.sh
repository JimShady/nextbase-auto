#!/bin/bash
# Installation script for nextbase-auto dependencies

echo "Installing system dependencies..."
sudo apt update
sudo apt install -y tesseract-ocr

echo ""
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

echo ""
echo "Installation complete!"
echo ""
echo "Next steps:"
echo "1. Edit form_data.txt with your information"
echo "2. Add your dashcam image path to form_data.txt"
echo "3. Run: python3 fill_form.py"
