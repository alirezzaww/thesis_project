// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract TransactionStorage {
    struct Transaction {
        uint id;
        address sender;
        address receiver;
        uint amount;
        bool isFraudulent;
    }

    Transaction[] public transactions;
    mapping(uint => bool) public flaggedTransactions;

    event TransactionAdded(uint id, address sender, address receiver, uint amount);
    event FraudDetected(uint id);

    function addTransaction(uint _id, address _receiver, uint _amount) public {
        transactions.push(Transaction(_id, msg.sender, _receiver, _amount, false));
        emit TransactionAdded(_id, msg.sender, _receiver, _amount);
    }

    function flagTransaction(uint _id) public {
        flaggedTransactions[_id] = true;
        emit FraudDetected(_id);
    }
}
