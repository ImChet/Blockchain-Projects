var DataToken = artifacts.require("./DataToken.sol");

module.exports = function(deployer) {
  deployer.deploy(DataToken);
};