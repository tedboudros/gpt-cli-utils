#!/bin/bash

# Get the directory of the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Detect the user's shell and determine the appropriate profile file
if [[ "$SHELL" == */zsh ]]; then
    PROFILE_FILE="$HOME/.zshrc"
elif [[ "$SHELL" == */bash ]]; then
    PROFILE_FILE="$HOME/.bashrc"
else
    echo "Unsupported shell. Please add '$DIR' to your PATH manually."
    exit 1
fi

# Create an alias for gcu
echo "alias gcu='python3 $DIR/main.py'" >> $PROFILE_FILE

echo "Setup complete. Please restart your terminal or run 'source $PROFILE_FILE' to apply the changes."
