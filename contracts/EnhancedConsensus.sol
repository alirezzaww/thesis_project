// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract EnhancedConsensus {
    struct Transaction {
        uint id;
        address sender;
        address receiver;
        uint amount;
        bool isFraudulent;
        uint[] parentTxs;
        uint approvals;
        bool committed;
    }

    mapping(uint => Transaction) public transactions;
    mapping(address => bool) public validators;
    mapping(address => uint) public energyScore;
    mapping(address => uint) public fraudCount;
    address[] public validatorList;

    uint public transactionCount;
    uint public constant MIN_APPROVALS = 2;
    address[] public leaderHistory;

    event TransactionAdded(uint id, address indexed sender, address indexed receiver);
    event TransactionApproved(uint id, address validator);
    event TransactionCommitted(uint id);
    event FraudFlagged(uint id);
    event LeaderRotated(address newLeader);

    modifier onlyValidator() {
        require(validators[msg.sender], "Not a validator");
        _;
    }

    constructor() {
        validators[msg.sender] = true;
        validatorList.push(msg.sender);
    }

    function addValidator(address _validator) external onlyValidator {
        validators[_validator] = true;
        validatorList.push(_validator);
    }

    function addTransaction(address _receiver, uint _amount, uint[] memory _parents) external returns (uint) {
        uint id = transactionCount++;
        transactions[id] = Transaction({
            id: id,
            sender: msg.sender,
            receiver: _receiver,
            amount: _amount,
            isFraudulent: false,
            parentTxs: _parents,
            approvals: 0,
            committed: false
        });
        emit TransactionAdded(id, msg.sender, _receiver);
        return id;
    }

    function approveTransaction(uint _id) external onlyValidator {
        require(!transactions[_id].committed, "Already committed");
        transactions[_id].approvals++;
        emit TransactionApproved(_id, msg.sender);

        if (transactions[_id].approvals >= MIN_APPROVALS) {
            transactions[_id].committed = true;
            emit TransactionCommitted(_id);
        }
    }

    function flagFraudulent(uint _id) external onlyValidator {
        transactions[_id].isFraudulent = true;
        fraudCount[transactions[_id].sender]++;
        emit FraudFlagged(_id);
    }

    function updateEnergyScore(address _validator, uint _score) external onlyValidator {
        energyScore[_validator] = _score;
    }

    function getReputation(address _validator) external view returns (uint) {
        uint fraud = fraudCount[_validator];
        uint energy = energyScore[_validator];
        if (fraud >= energy) return 0;
        return energy - fraud;
    }

    function rotateLeader() external onlyValidator {
        require(validatorList.length > 0, "No validators");
        uint index = uint(keccak256(abi.encodePacked(block.timestamp, block.prevrandao))) % validatorList.length;
        address leader = validatorList[index];
        leaderHistory.push(leader);
        emit LeaderRotated(leader);
    }

    function getCurrentLeader() external view returns (address) {
        if (leaderHistory.length == 0) return address(0);
        return leaderHistory[leaderHistory.length - 1];
    }

    function getAllValidators() external view returns (address[] memory) {
        return validatorList;
    }
}
