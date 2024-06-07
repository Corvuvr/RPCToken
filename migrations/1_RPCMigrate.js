const RPCToken = artifacts.require("RPCToken");

module.exports = function (deployer) {
  deployer.deploy(RPCToken, 1000000); // Убедитесь, что здесь указан правильный параметр конструктора
};
