// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract DataToken {

    struct Data {
        address owner;
        string filename;
        string fileCID;
        uint256 size;
    }

    mapping(bytes32 => Data) public dataTokens;
    mapping(bytes32 => address[]) public dataTransferLog;

    event TokenRegistered(bytes32 indexed dataHash, address indexed owner);
    event TokenTransferred(bytes32 indexed dataHash, address indexed from, address indexed to);
    event TokenBurned(bytes32 indexed dataHash);

    function register(bytes32 dataHash, string calldata filename, string calldata fileCID, uint256 size) external {
        require(dataTokens[dataHash].owner == address(0), "Token already registered.");
        
        dataTokens[dataHash] = Data(msg.sender, filename, fileCID, size);
        
        emit TokenRegistered(dataHash, msg.sender);
    }

    function query(bytes32 dataHash) external view returns (Data memory) {
        return dataTokens[dataHash];
    }

    function transferData(bytes32 dataHash, address to) external {
        require(dataTokens[dataHash].owner == msg.sender, "Only the owner can transfer the token.");
        require(to != address(0), "Cannot transfer to the zero address.");
        
        dataTransferLog[dataHash].push(dataTokens[dataHash].owner);
        dataTransferLog[dataHash].push(to);
        
        dataTokens[dataHash].owner = to;
        
        emit TokenTransferred(dataHash, msg.sender, to);
    }

    function queryTracker(bytes32 dataHash) external view returns (address[] memory) {
        return dataTransferLog[dataHash];
    }

    function burn(bytes32 dataHash) external {
        require(dataTokens[dataHash].owner == msg.sender, "Only the owner can burn the token.");
        
        delete dataTokens[dataHash];
        
        emit TokenBurned(dataHash);
    }
}
