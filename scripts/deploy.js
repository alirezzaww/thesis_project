const hre = require("hardhat");

async function main() {
  // Get the contract factory
  const TransactionStorage = await hre.ethers.getContractFactory("TransactionStorage");

  // Deploy the contract
  const transactionStorage = await TransactionStorage.deploy();
  await transactionStorage.waitForDeployment();  // ✅ Corrected from `deployed()`

  // Get deployed contract address
  const contractAddress = await transactionStorage.getAddress();
  console.log(`🚀 Contract deployed to: ${contractAddress}`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
