from flask import Flask, request, jsonify, render_template
from web3 import Web3
import json
import sys
app = Flask(__name__)
ganache_url = "http://127.0.0.1:8545"
web3 = Web3(Web3.HTTPProvider(ganache_url))
if web3.is_connected():
    print("Successfully connected to Ganache")
else:
    print("Failed to connect to Ganache")
with open('../build/contracts/RPCToken.json', 'r', encoding='UTF-8') as f:
    contract_json = json.load(f)
    contract_abi = contract_json['abi']
    contract_address = contract_json['networks']['5777']['address']
    contract = web3.eth.contract(address=contract_address, abi=contract_abi)
accounts = web3.eth.accounts

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def status():
    is_connected = web3.is_connected()
    return jsonify({'connected': is_connected})

#==================================METHODS==================================

@app.route('/transferTokens', methods=['POST'])
def transferTokens():
    try:
        data = request.json
        print(f'\nTransferred {int(data['TokensToSend'])} RPC token(s) to:\nP0:\t{data['P0']}\nP1:\t{data['P1']}', file=sys.stderr)
        tx_hash = contract.functions.transfer(data['P0'], int(data['TokensToSend'])).transact({
            'from': data['TokenSender']
        })
        tx_hash = contract.functions.transfer(data['P1'], int(data['TokensToSend'])).transact({
            'from': data['TokenSender']
        })
        return jsonify({'Status': tx_hash.hex()})
    except:
        return jsonify({'Status': 'Failed'})

@app.route('/inviteToSession', methods=['POST'])
def inviteToSession():
    try:
        data = request.json    
        print(f'\nSession Initiated:\nFrom:\t{data['From']}\nTo:\t{data['Opponent']}\nBet:\t{int(data['BetAmount'])}\nAction:\t{int(data['Action'])}', file=sys.stderr)
        contract.functions.inviteToSession(
            data['Opponent'],
            int(data['BetAmount']),
            int(data['Action'])
        ).transact({'from': data['From']})
        return jsonify({'Status': f'Invited {data['Opponent']}'})
    except:
        return jsonify({'Status': 'Failed'})

@app.route('/getSessionData', methods=['POST'])
def getSessionData():
    try:
        data    = request.json
        guest   = contract.functions.getSessionGuest(data['Target']).call()
        bet     = contract.functions.getSessionBet(data['Target']).call()
        print(f'\nSession state:\nTarget:\t{data['Target']}\nOp.:\t{guest}\nBet info:\t{int(bet)}', file=sys.stderr)
        return jsonify({'Guest': guest, 'Bet': bet})
    except:
        return jsonify({'Guest': 'Failed to get', 'Bet': 'Failed to get'})

@app.route('/startSession', methods=['POST'])
def startSession():
    try:
        data = request.json
        print(f'\nGame started:\nP0:\t{data['Sender']}\nP1:\t{data['Opponent']}', file=sys.stderr)
        winner = contract.functions.startSession(data['Sender']).call({
            'from': data['Opponent']
        })# .hex()
        return jsonify({'Status': 'Started', 'Winner': winner})
    except:
        print(f'\nAn error occured. Possibly, due to the fact that the session doesn\'t exist.')
        return jsonify({'Status': 'Failed', 'Winner': 'None'})

@app.route('/balanceOf', methods=['POST'])
def balanceOf():
    try:
        data = request.json
        balance = contract.functions.balanceOf(data['Target']).call()
        print(f'\nTarget:\t\t{data['Target']}\nBalance:\t{int(balance)}', file=sys.stderr)
        return jsonify({'Balance': balance})
    except:
        return jsonify({'Balance': 'Failed to get'})

@app.route('/cancelSession', methods=['POST'])
def cancelSession():
    try:
        data = request.json
        contract.functions.cancelSession().transact({
            'from': data['Target']
        })
        return jsonify({'Status': 'Session cancelled'})
    except:
        return jsonify({'Status': 'Cancellation failed'})

if __name__ == '__main__':
    app.run(debug=True)
