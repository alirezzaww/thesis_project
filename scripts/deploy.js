const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();

  console.log("Deploying contract with account:", deployer.address);

  const balance = await hre.ethers.provider.getBalance(deployer.address);
  console.log("Account balance:", hre.ethers.formatUnits(balance, "ether"), "ETH");

  const ContractFactory = await hre.ethers.getContractFactory("EnhancedConsensus");
  const contract = await ContractFactory.deploy();

  // Wait for the contract deployment to finish
  await contract.waitForDeployment();

  // Support both Ethers v5 (address) and v6 (target/getAddress)
  const deployedAddress = contract.address || contract.target || (await contract.getAddress());
  console.log("✅ EnhancedConsensus deployed at:", deployedAddress);
}

main().catch((error) => {
  console.error("❌ Deployment failed:", error);
  process.exit(1);
});
