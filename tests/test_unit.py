from project.helpers import convert_to_crypto, convert_to_usd

def test_converters():
    amounts = [1.0, 99.0, 500.0, 1_000_000.0]
    total = 0.0
    user = {
        "BTC": 0.0,
        "ETH": 0.0,
        "DOGE": 0.0,
        "USDT": 0.0,
        "BNB": 0.0,
    }
    rets = {
        "BTC": [],
        "ETH": [],
        "DOGE": [],
        "USDT": [],
        "BNB": [],
    }

    for sym in user:
        for usd in amounts:
            converted = convert_to_crypto(usd, sym)
            total += -usd
            rets[sym].append(converted)
            user[sym] += converted
    for sym in user:
        for bit in rets[sym]:
            converted = convert_to_usd(bit, sym)
            total += converted
            user[sym] += -bit

    assert abs(total) < 0.000000000001
    for v in user.values():
        assert abs(v) < 0.000000000001

    
    


