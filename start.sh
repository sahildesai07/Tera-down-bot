#!/bin/bash
echo "Starting aria2c..."
aria2c --enable-rpc --rpc-listen-all=false --rpc-allow-origin-all --daemon
echo "Waiting for aria2c to start..."
sleep 5  # Wait for 5 seconds
echo "aria2c started, now starting Python script..."
python terabox.py
