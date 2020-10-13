from iota import Iota
from iota import TryteString

def findmessages(TXN_BUNDLE):
    api = Iota('http://node.deviceproof.org:14265')
    dict_txn = api.find_transactions(bundles = [TXN_BUNDLE.rstrip()])

    if len(dict_txn["hashes"]) == 0:
        return ""

    tail_hash = dict_txn['hashes']
    test = str(tail_hash)[19:100]

    bundle = api.get_bundles(test)
    signature_message_fragment = str(bundle["bundles"][0][0].signature_message_fragment)

    ans = TryteString(signature_message_fragment).decode()
    return ans
