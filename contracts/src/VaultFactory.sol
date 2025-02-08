// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./Vault.sol";

contract VaultFactory {
    event VaultDeployed(address vaultAddress, address indexed agent, address indexed user);

    function deployVault(address agent, address user) external returns (address) {
        Vault vault = new Vault(agent, user);
        emit VaultDeployed(address(vault), agent, user);
        return address(vault);
    }
} 