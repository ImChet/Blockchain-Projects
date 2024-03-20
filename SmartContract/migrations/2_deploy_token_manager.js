const PolicyLibrary = artifacts.require("PolicyLibrary");
const TokenManager = artifacts.require("TokenManager");

module.exports = function (deployer) {
  const gasLimit = 10000000; // Adjust the gas limit value as needed
  deployer.deploy(PolicyLibrary).then(function() {
    return deployer.link(PolicyLibrary, TokenManager).then(function() {
      return deployer.deploy(TokenManager, { gas: gasLimit });
    });
  });
};
