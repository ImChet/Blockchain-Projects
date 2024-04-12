#!/bin/bash

# Define project root directory
PROJECT_ROOT="./"

# Start Ganache CLI in the background with a fixed network id
ganache-cli -i 5777 --gasLimit 10000000 > /dev/null &
GANACHE_PID=$!
echo "Ganache CLI started with PID $GANACHE_PID"

# Wait for Ganache to fully start
sleep 5

# Compile and migrate contracts with Truffle
echo "Compiling and migrating contracts..."
cd $PROJECT_ROOT
truffle compile --all && truffle migrate --reset

# Extract the deployed contract address (Ensure only the last address is captured)
CONTRACT_ADDRESS=$(grep -oE '0x[a-fA-F0-9]{40}' build/contracts/DataToken.json | tail -1)
echo "DataToken contract deployed at $CONTRACT_ADDRESS"

# Check if contract address is not empty
if [ -z "$CONTRACT_ADDRESS" ]; then
  echo "Error: Contract deployment failed."
  exit 1
fi

# Export the contract address for the middleware to use
export CONTRACT_ADDRESS

# Start the Middleware
echo "Starting the middleware..."
python3 $PROJECT_ROOT/eth_middleware.py &
MIDDLEWARE_PID=$!
echo "Middleware started with PID $MIDDLEWARE_PID"

# Start the Gateway
echo "Starting the gateway..."
python3 $PROJECT_ROOT/gateway_server.py &
GATEWAY_PID=$!
echo "Gateway started with PID $GATEWAY_PID"

# Function to clean up background processes on script exit
function cleanup {
    echo "Stopping the Gateway..."
    kill $GATEWAY_PID
    echo "Stopping the Middleware..."
    kill $MIDDLEWARE_PID
    echo "Stopping Ganache CLI..."
    kill $GANACHE_PID
}

# Trap script exit signals to clean up background processes
trap cleanup EXIT

# Keep the script running to maintain the background processes
wait
