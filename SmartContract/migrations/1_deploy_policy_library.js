const PolicyLibrary = artifacts.require("PolicyLibrary");

module.exports = function (deployer) {
  deployer.deploy(PolicyLibrary);
};
