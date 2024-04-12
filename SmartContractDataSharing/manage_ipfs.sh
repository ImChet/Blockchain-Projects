#!/bin/bash

# Function to start IPFS nodes
start_nodes() {
    NODE_COUNT=2  # Number of nodes to start
    for i in $(seq 1 $NODE_COUNT); do
        docker run -d --name "ipfs_node_$i" \
            -p $((5000 + $i)):5001 \
            -p $((8080 + $i)):8080 \
            -p $((4000 + $i)):4001 \
            ipfs/go-ipfs:latest
    done
    echo "Started $NODE_COUNT IPFS nodes."
}

# Function to stop IPFS nodes
stop_nodes() {
    docker stop $(docker ps -q --filter ancestor=ipfs/go-ipfs:latest)
    docker rm $(docker ps -a -q --filter ancestor=ipfs/go-ipfs:latest)
    echo "Stopped and removed all IPFS nodes."
}

# Main menu for script
PS3='Please enter your choice: '
options=("Start IPFS Nodes" "Stop IPFS Nodes" "Quit")
select opt in "${options[@]}"
do
    case $opt in
        "Start IPFS Nodes")
            start_nodes
            ;;
        "Stop IPFS Nodes")
            stop_nodes
            ;;
        "Quit")
            break
            ;;
        *) echo "invalid option $REPLY";;
    esac
done
