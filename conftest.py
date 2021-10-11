import pytest
import brownie

@pytest.fixture(scope="function", autouse=True)
def isolate(fn_isolation):
    pass


@pytest.fixture(scope="module")
def token(Token, accounts):
    return Token.deploy(accounts[1], "Token", "TKN", 5, 10**10, 10, 80, accounts[1], {'from': accounts[0]})

@pytest.fixture
def pancakeRouter(interface):
    yield interface.PancakeRouter('0x10ED43C718714eb63d5aA57B78B54704E256024E')

@pytest.fixture
def WBNB(interface):
    yield interface.ERC20('0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c')