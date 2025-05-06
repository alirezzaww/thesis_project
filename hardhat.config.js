require("@nomicfoundation/hardhat-toolbox"); // ✅ Required for ethers, waffle, console logs, etc.

module.exports = {
  solidity: "0.8.28",
  networks: {
    localhost: {
      url: "http://0.0.0.0:8545"
    }
  }
};
