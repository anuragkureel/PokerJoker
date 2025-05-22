#!/bin/bash
# process_poker_image.sh

# Check if image path is provided
if [ -z "$1" ]; then
    echo "Please provide an image path"
    exit 1
fi

# Set Node version using nvm (Node Version Manager)
if [ -f "$HOME/.nvm/nvm.sh" ]; then
    source "$HOME/.nvm/nvm.sh"
    nvm use 23.6.0  # or whatever version you need
else
    echo "nvm not found. Please install nvm or set the correct Node version manually"
    exit 1
fi

# Verify Node version
NODE_VERSION=$(node -v)
echo "Using Node version: $NODE_VERSION"

# Run Python script
python3 hello_tessract.py "$1"

# Check if Python script was successful
if [ $? -eq 0 ]; then
    # Run JavaScript code
    node googleImageRead.js
else
    echo "Python processing failed"
    exit 1
fi