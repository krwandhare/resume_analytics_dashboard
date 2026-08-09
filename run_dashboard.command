#!/bin/zsh
# Change to the directory where this script is located
cd "$(dirname "$0")"

echo "======================================"
echo "🚀 Starting Resume Analytics Dashboard"
echo "======================================"

# Activate the virtual environment
source .venv/bin/activate

# Run the Streamlit app
streamlit run src/myproject/main.py
