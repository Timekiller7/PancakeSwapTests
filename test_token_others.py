import brownie
from brownie import accounts


def test_constructor(token):
    rtotal = 2**256 - 1 - ((2**256 - 1) % (10**10))
    print("rTotal in py: ", rtotal)
    print("rTotal from constructor: ", token.get_rTotal())

    print("Owner of contract (not tokens =_rTotal) is: ", token.owner())
    assert token.owner() == accounts[0]
    assert token.get_rOwned(accounts[1]) == rtotal


def test_deliver(token):
    print("Before: ")
    print("    Total Fee: ", token.totalFees())
    balance = token.get_rOwned(accounts[1])
    print("    _rOwned: ", balance)
    print("    _rTotal: ", token.get_rTotal())

    token.deliver(10, {'from': accounts[1]})

    print("After: ")
    print("    Total Fee: ", token.totalFees())
    print("    _rOwned: ", token.get_rOwned(accounts[1]))
    print("    _rTotal: ", token.get_rTotal())

    assert token.totalFees() == 10
    assert token.get_rOwned(accounts[1]) < balance
    assert token.isExcludedFromReward(accounts[1]) is False
    assert token.isExcludedFromReward(accounts[0]) is False


def test_token_contract_balance(token):
    accounts[0].transfer(token, 2)
    print(token.address)
    balance = token.balanceOf(token.address)
    print("Balance of the contract: ", balance)


def test_reflectionFromToken(token):
    amount = token.reflectionFromToken(10**9, False)
    rate = token.get_rate()
    print("Current rate: ", rate)
    ramount = 10**9 * rate
    assert ramount == amount

    amount2 = token.reflectionFromToken(10**9, True)
    print("The difference: ", ramount - amount2)
    assert ramount == amount2

    token.setAllFeePercent(9, 9, 9, 0, 0, {'from': accounts[0]})
    ramount2 = token.reflectionFromToken(10**9, False)
    amount3 = token.reflectionFromToken(10**9, True)
    assert ramount2 > amount3

