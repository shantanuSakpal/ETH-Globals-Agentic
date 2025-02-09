// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract Vault is ReentrancyGuard {
    address public agent;
    address public user;

    event Deposit(address indexed from, uint256 amount);
    event Withdraw(address indexed to, uint256 amount);

    modifier onlyAuthorized() {
        require(msg.sender == agent || msg.sender == user, "Not authorized");
        _;
    }

    constructor(address _agent, address _user) {
        require(_agent != address(0) && _user != address(0), "Invalid addresses");
        agent = _agent;
        user = _user;
    }

    // Allow deposits (ETH)
    function deposit() external payable nonReentrant {
        require(msg.value > 0, "No ether sent");
        emit Deposit(msg.sender, msg.value);
    }

    // Allow authorized withdrawal
    function withdraw(uint256 amount) external nonReentrant onlyAuthorized {
        require(address(this).balance >= amount, "Insufficient balance");
        payable(msg.sender).transfer(amount);
        emit Withdraw(msg.sender, amount);
    }
} 