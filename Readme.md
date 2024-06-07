# Installation

1. Install NodeJS
2. Install Truffle: `npm install -g truffle` and create wokspace with port: `8545` _(or set a wanted port number in `truffle-config.js` and `src/WebApp.py` (line 6))_
3. Install Openzeppelin ERC20 in repository's root folder: `npm install @openzeppelin/contracts`
4. Compile truffle: `truffle compile`
5. Migrate: `truffle migrate -f 1 --to 1`
6. Install flask, web3: `pip install flask web3`
7. Go in `src` directory and run flask app: `cd src && flask --app WebApp run`
8. Connect to the dedicated url shown in terminal 