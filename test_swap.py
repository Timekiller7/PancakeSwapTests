import brownie
from brownie import accounts


# INSUFFICIENT_LIQUIDITY
def test_transfer_swap_1(Token, pancakeRouter, interface, WBNB):
    token = Token.deploy(accounts[1], "Token", "TKN", 18, 4 * (10 ** 18), 255, 255, accounts[1], {'from': accounts[0]})
    pair = token.pair()
    pancakePair = interface.PancakePair(pair)
    token.changeNumTokensSellToAddToLiquidity({'from': accounts[2]})

    tx = token.approve(token.address, "1 ether", {'from': accounts[1]})
    print(tx.events)
    print(token.allowance(accounts[1], token.address))
    token.transferFrom(accounts[1], token.address, "0.8 ether", {'from': token.address})

    token.approve(token.address, 2 * 10 ** 18, {'from': accounts[1]})
    token.transferFrom(accounts[1], pancakePair, 1.7 * 10 ** 18, {'from': token.address})

    print(pancakePair.getReserves())
    
    token.set_buybackFee(9, {'from': accounts[0]})
    assert token.get_buybackFee() == 9
    token.setAllFeePercent(2, 2, 2, 2, 2, {'from': accounts[0]})
    assert token.get_buybackFee() == 2

    token.setBuybackUpperLimit(0, {'from': accounts[0]})
    with brownie.reverts('PancakeLibrary: INSUFFICIENT_LIQUIDITY'):
        tx = token.transferFrom(accounts[1], pair, 1 * 10 ** 18, {'from': accounts[1]})


# checking event of SwapAndLiquify
def test_transfer_swap_2(Token, pancakeRouter, interface, WBNB):
    token = Token.deploy(accounts[1], "Token", "TKN", 18, 4 * (10 ** 18), 255, 255, accounts[1], {'from': accounts[0]})
    pair = token.pair()
    pancakePair = interface.PancakePair(pair)
    token.changeNumTokensSellToAddToLiquidity({'from': accounts[2]})
    token.transfer(token, 1 * 10 ** 18, {'from': accounts[1]})
    token.transfer(pancakePair, 2 * 10 ** 18, {'from': accounts[1]})
    accounts[0].transfer(WBNB, 3 * 10 ** 18)
    WBNB.transfer(pancakePair, 2 * 10 ** 18, {'from': accounts[0]})

    pancakePair.mint(WBNB.address, {'from': accounts[0]})

    print("Reserves: ", pancakePair.getReserves())
    token.setAllFeePercent(2, 2, 2, 2, 0, {'from': accounts[0]})
    token.setBuybackUpperLimit(0, {'from': accounts[0]})
    tx = token.transfer(pair, 1 * 10 ** 18, {'from': accounts[1]})

    print("Event SwapAndLiquify: ")
    print('    tokensSwapped: ', tx.events["SwapAndLiquify"]['tokensSwapped'])
    print('    ethReceived: ', tx.events["SwapAndLiquify"]['ethReceived'])
    print('    tokensIntoLiqudity: ', tx.events["SwapAndLiquify"]['tokensIntoLiqudity'])


# check event in WBNB
def test_transfer_swap_3(Token, pancakeRouter, interface, WBNB):
    token = Token.deploy(accounts[1], "Token", "TKN", 18, 4 * (10 ** 18), 255, 255, accounts[1], {'from': accounts[0]})
    pair = token.pair()
    pancakePair = interface.PancakePair(pair)
    token.changeNumTokensSellToAddToLiquidity({'from': accounts[2]})
    token.transfer(token, 1 * 10 ** 18, {'from': accounts[1]})
    token.transfer(pancakePair, 2 * 10 ** 18, {'from': accounts[1]})
    accounts[0].transfer(WBNB, 3 * 10 ** 18)
    WBNB.transfer(pancakePair, 2 * 10 ** 18, {'from': accounts[0]})

    pancakePair.mint(WBNB.address, {'from': accounts[0]})

    reserve1, reserve2, time = pancakePair.getReserves()
    print(reserve1, reserve2)

    token.setAllFeePercent(2, 2, 2, 2, 2, {'from': accounts[0]})  # with buyBackTokens()
    token.setBuybackUpperLimit(0, {'from': accounts[0]})

    tx = token.transfer(pair, 1 * 10 ** 18, {'from': accounts[1]})
    reserve3, reserve4, time = pancakePair.getReserves()

    assert reserve1 != reserve3 and reserve2 != reserve4

    print(reserve3, reserve4,)
    print(tx.events['Swap'])
