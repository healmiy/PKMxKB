#!/bin/bash

echo "Stopping any existing Tailscale daemons..."
sudo killall tailscaled 2>/dev/null
osascript -e 'quit app "Tailscale"' 2>/dev/null

echo "Starting standalone tailscaled with WARP SOCKS5 proxy..."

# Find the brew-installed tailscaled
TAILSCALED_PATH=$(brew --prefix)/bin/tailscaled
TAILSCALE_CLI=$(brew --prefix)/bin/tailscale

if [ ! -f "$TAILSCALED_PATH" ]; then
    echo "Error: tailscaled not found at $TAILSCALED_PATH. Did 'brew install tailscale' succeed?"
    exit 1
fi

echo "Running tailscaled in the background. Please leave this terminal open or use a tool like screen/tmux."
echo "Once it's running, open a new terminal tab and type:"
echo "  $TAILSCALE_CLI --socket=/var/run/tailscaled.socket up"
echo ""
echo "(We must use the explicit brew CLI and socket to prevent it from accidentally talking to the Mac App Store version!)"
echo ""

# Explicitly pass environment variables through sudo (sudo -E often drops proxy variables for security!)
sudo ALL_PROXY="socks5://127.0.0.1:40000" \
     HTTPS_PROXY="socks5://127.0.0.1:40000" \
     HTTP_PROXY="socks5://127.0.0.1:40000" \
     NO_PROXY="localhost,127.0.0.1,::1,*.local" \
     "$TAILSCALED_PATH"
