// SPDX-License-Identifier: MIT
pragma solidity ^0.8.28;

contract TransactionStorage {
    struct Transaction {
        uint256 id;
        string details;
        bool isFraudulent;
    }

    mapping(uint256 => Transaction) public transactions;
    uint256 public transactionCount;

    event TransactionAdded(uint256 id, string details, bool isFraudulent);
    event TransactionFlagged(uint256 id);

    function storeTransaction(uint256 _id, string memory _details, bool _isFraudulent) public {
        transactions[_id] = Transaction(_id, _details, _isFraudulent);
        transactionCount++;

        emit TransactionAdded(_id, _details, _isFraudulent);
    }

    function flagTransaction(uint256 _id) public {
        require(transactions[_id].id != 0, "Transaction does not exist.");
        transactions[_id].isFraudulent = true;

        emit TransactionFlagged(_id);
    }

    function getTransaction(uint256 _id) public view returns (Transaction memory) {
        return transactions[_id];
    }
}
