import brownie
from brownie import accounts


def test_exclude(token):
    assert False is token.isExcludedFromReward(accounts[1], {'from': accounts[0]})

    token.excludeFromReward(accounts[1], {'from': accounts[0]})
    
    assert token.get_tOwned(accounts[1]) > 0
    assert True is token.isExcludedFromReward(accounts[1], {'from': accounts[0]})


def test_include(token):
    token.excludeFromReward(accounts[1], {'from': accounts[0]})
    token.includeInReward(accounts[1], {'from': accounts[0]})
    
    assert token.get_tOwned(accounts[1]) == 0
    assert False is token.isExcludedFromReward(accounts[1], {'from': accounts[0]})

