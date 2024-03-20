// SPDX-License-Identifier: MIT
pragma solidity ^0.8.10;

// Define the library
library PolicyLibrary {
    struct Account {
        uint256 balance;
        string policy;
    }

    // Library function to get the policy of an account
    function getPolicy(Account storage account) external view returns (string memory) {
        return account.policy;
    }
}

// TokenManager contract
contract TokenManager {
    using PolicyLibrary for PolicyLibrary.Account; // Use the library for Account struct

    mapping(address => PolicyLibrary.Account) public accounts;

    // Function to deposit tokens into an account
    function deposit(address account_id, uint256 token_value) public {
        accounts[account_id].balance += token_value;
    }

    // Function to withdraw tokens from an account
    function withdraw(address account_id, uint256 token_value) public {
        require(accounts[account_id].balance >= token_value, "Insufficient balance to withdraw");
        accounts[account_id].balance -= token_value;
    }

    // Function to query the token balance of an account
    function query(address account_id) public view returns (uint256) {
        return accounts[account_id].balance;
    }

    // Function to set the policy of an account
    function setPolicy(address account_id, string memory str_policy) public {
        accounts[account_id].policy = str_policy;
    }

    // Adjusted function to get the policy of an account using the library
    function getPolicy(address account_id) public view returns (string memory) {
        PolicyLibrary.Account storage account = accounts[account_id];
        return account.getPolicy();
    }
}
