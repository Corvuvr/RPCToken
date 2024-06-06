// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";

contract RPCToken is ERC20, ERC20Permit {

    // Для демонстративности, обернём действия в enum
    enum RockPaperScissorsActions {
        rock, paper, scissors
    }
    // Инфрмация о конкретной сессии
    struct SessionData {
        address m_Guest;
        uint256 m_Bet;
        RockPaperScissorsActions m_Action;
    }
    // Словарь с записями об активных сессиях
    mapping (address => SessionData ) internal Sessions;

    // Конструктор, в качестве аргумента принимает стартовое число токенов
    constructor(uint256 initialSupply) ERC20("RPCToken", "RPC") ERC20Permit("RPCToken") {
        _mint(msg.sender, initialSupply);
    }

    // Отправляет адресату приглашение на сессию; передаёт ставку посреднику.
    function inviteToSession(address opponent, uint256 bet, RockPaperScissorsActions action) public {
        transfer(address(this), bet);
        Sessions[msg.sender].m_Guest = opponent;
        Sessions[msg.sender].m_Bet = bet;
        Sessions[msg.sender].m_Action = action;
    }
    // Служебные геттеры
    function getSessionBet(address target) public view returns (uint256) {
        return Sessions[target].m_Bet;
    }
    function getSessionGuest(address target) public view returns (address) {
        return Sessions[target].m_Guest;
    }
    // Отмена сессии; возвращение ставки.
    function cancelSession() public {
        RPCToken mt = RPCToken(this);
        mt.approve(msg.sender, Sessions[msg.sender].m_Bet);
        transferFrom(address(this), msg.sender, Sessions[msg.sender].m_Bet);
        delete Sessions[msg.sender];
    }
    // Завершение сессии.
    function shutdownSession(address target) internal {
        delete Sessions[target];
    }
    
    // Камень-ножницы-бумага
    function rockPaperScissors(RockPaperScissorsActions action_1, RockPaperScissorsActions action_2) internal pure returns (bool b_FirstPlayerWins) {
        return (uint(action_1) % 3 == (uint(action_2) + 1) % 3); 
    }
    
    // Начало игры. Проверка готовности игроков. Посредник отправляет токены участнкам в соответствии с результатом игры.
    function startSession(address opponent) public payable returns (address) {
        // Проверки на готовность
        require((getSessionGuest(msg.sender) == opponent) && (getSessionGuest(opponent) == msg.sender), "Player(s) have not accepted the game");
        require(getSessionBet(msg.sender) == getSessionBet(opponent), "Bets are not equal");
        // Инстанциирование контракта для распоряжения токенами.
        RPCToken mt = RPCToken(this);
        address winner = address(0);
        if (rockPaperScissors(Sessions[msg.sender].m_Action, Sessions[opponent].m_Action)) {
            // Игрок_1 (отправитель) побеждает
            mt.approve(msg.sender, 2*getSessionBet(msg.sender));
            transferFrom(address(this), msg.sender, 2*getSessionBet(msg.sender));
            winner = msg.sender;
        } else if (rockPaperScissors(Sessions[opponent].m_Action, Sessions[msg.sender].m_Action)) {
            // Игрок_2 (оппонент) побеждает 
            mt.approve(msg.sender, 2*getSessionBet(opponent));
            transferFrom(address(this), msg.sender, 2*getSessionBet(opponent));
            transfer(opponent, 2*getSessionBet(opponent));
            winner = opponent;
        } else {
            // Ничья
            mt.approve(msg.sender, 2*getSessionBet(msg.sender));
            transferFrom(address(this), msg.sender, 2*getSessionBet(msg.sender));
            transfer(opponent, getSessionBet(opponent));
        }
        // Завершение сессий
        shutdownSession(opponent);
        shutdownSession(msg.sender);
        return winner;
    }
}