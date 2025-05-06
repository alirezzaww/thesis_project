const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();

  console.log("Deploying contract with account:", deployer.address);

  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatUnits(balance, "ether"), "ETH");

  const ContractFactory = await hre.ethers.getContractFactory("EnhancedConsensus");
  const contract = await ContractFactory.deploy();

  // ⬇️ Instead of contract.deployed(), use this:
  await contract.deployTransaction.wait();

  console.log("✅ EnhancedConsensus deployed at:", contract.address);
}

main().catch((error) => {
  console.error("❌ Deployment failed:", error);
  process.exit(1);
});
