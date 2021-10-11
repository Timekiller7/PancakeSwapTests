import brownie
from brownie import accounts


# without swapping  & fee
def test_transfer_standard_1(token):
    before_rtotal = token.get_rTotal()
    before_rOwned = token.get_rOwned(accounts[1])
    rate = token.get_rate()
    ramount = 10 ** 6 * rate
    print("Difference in total's (before tx): ", before_rtotal - 10**10)
    tx = token.transfer(accounts[2], 10**6, {'from': accounts[1]})
    print("Difference in rates: ", token.get_rate() - rate)

    assert token.get_rOwned(token.address) == 0  # because of _takeLiquidity()
    print("Difference in get_rOwned(sender): ", before_rOwned - token.get_rOwned(accounts[1]))

    assert token.get_rTotal() == before_rtotal
    assert token.get_rOwned(accounts[2]) == ramount

    assert tx.events['Transfer']['from'] == accounts[1]
    assert tx.events['Transfer']['to'] == accounts[2]
    assert tx.events['Transfer']['value'] == 10**6


# without swapping, without fee (because accounts[1] - excluded)
def test_transfer_standard_2(token):
    token.setAllFeePercent(8, 8, 8, 8, 8, {'from': accounts[0]})
    rate = token.get_rate()
    ramount = 10 ** 6 * rate
    tx = token.transfer(accounts[2], 10 ** 6, {'from': accounts[1]})

    assert token.get_rOwned(accounts[2]) == ramount
    assert tx.events['Transfer']['value'] == 10 ** 6


# without swapping, with excluded accounts and fee
def test_transfer_mix_3(token):
    token.setAllFeePercent(8, 8, 8, 8, 8, {'from': accounts[0]})
    rate = token.get_rate()
    ramount = 10 ** 9 * rate

    assert token.isExcludedFromReward(accounts[1]) is False
    assert token.isExcludedFromReward(accounts[2]) is False

    # standard
    token.transfer(accounts[2], 10 ** 9, {'from': accounts[1]})
    print("_tOwned by accounts[2]: ", token.get_tOwned(accounts[2]))

    assert token.isExcludedFromFee(accounts[2]) is False
    assert token.isExcludedFromFee(accounts[3]) is False

    token.excludeFromReward(accounts[2], {'from': accounts[0]})
    token.excludeFromReward(accounts[3], {'from': accounts[0]})

    before_rtotal = token.get_rTotal()
    before_ttotal = token.get_tTotal()
    before_rowned2 = token.get_rOwned(accounts[2])

    assert before_rowned2 == ramount

    assert token.get_tFeeTotal() == 0

    # both excludes
    token.transfer(accounts[3], 10 ** 8, {'from': accounts[2]})

    assert token.get_tFeeTotal() > 0

    assert before_rtotal > token.get_rTotal()
    assert before_ttotal == token.get_tTotal()
    assert token.get_rOwned(token.address) > 0

    assert 10 ** 7 < token.get_rOwned(accounts[2]) < before_rowned2
    assert 10 ** 9 < token.get_rOwned(accounts[3])
    assert 10 ** 7 < token.get_tOwned(accounts[3]) < 10 ** 9

    # from excluded
    token.includeInReward(accounts[2])
    before_rowned2 = token.get_rOwned(accounts[2])
    before_rowned3 = token.get_rOwned(accounts[3])
    before_towned3 = token.get_tOwned(accounts[3])
    token.transfer(accounts[2], 10 ** 7, {'from': accounts[3]})

    assert 10 ** 8 < before_rowned2 < token.get_rOwned(accounts[2])
    assert before_rowned3 > token.get_rOwned(accounts[3]) > 10 ** 8
    assert before_towned3 > token.get_tOwned(accounts[3]) > 10 ** 7

    # to excluded
    token.includeInReward(accounts[3])
    token.excludeFromReward(accounts[2])

    before_rowned2 = token.get_rOwned(accounts[2])
    before_rowned3 = token.get_rOwned(accounts[3])
    token.transfer(accounts[2], 10 ** 7, {'from': accounts[3]})

    assert 10 ** 15 < before_rowned2 < token.get_rOwned(accounts[2])
    assert before_rowned3 > token.get_rOwned(accounts[3]) > 10 ** 8
    assert token.get_tOwned(accounts[3]) == 0


def test_transfer_to_pair_without_swap(token):
    pair = token.pair()
    tx = token.transfer(pair, 10 ** 6, {'from': accounts[1]})
    assert tx.events['Transfer']['value'] > 0


def test_transfer_recover_bep20(token, WBNB):
    with brownie.reverts("Self withdraw"):
        tx = token.recoverBEP20(token, "2 ether", {'from': accounts[0]})
    with brownie.reverts():
        tx = token.recoverBEP20(WBNB, "2 ether", {'from': accounts[0]})

    accounts[0].transfer(WBNB, "3 ether")
    WBNB.transfer(token, "2.5 ether", {'from': accounts[0]})
    tx = token.recoverBEP20(WBNB, "2 ether", {'from': accounts[0]})
    print("Transfer value of recovering BEP20: ", tx.events['Transfer']['value'])

