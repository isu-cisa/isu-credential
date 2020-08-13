from iota import Iota
from iota import TryteString

#TXN_BUNDLE = "ZEEJHWV9IDAGYGAVQKOULBGJFDXYZYWBI9IFSVKPYJF9P9LVSXKVQBXSHEIQOSIFZJVLF9EJLULCDQFY9"

def findmessages(TXN_BUNDLE):
    #print("hello bundle is : " + str(TXN_BUNDLE))
    api = Iota('http://node.deviceproof.org:14265')
    dict_txn = api.find_transactions(bundles = [TXN_BUNDLE.rstrip()])
    #print("Transaction = ",dict_txn['hashes'])

    tail_hash = dict_txn['hashes']
    test = str(tail_hash)[19:100]
    #print("Transaction hash = ",test)

    bundle = api.get_bundles(test)
    signature_message_fragment = str(bundle["bundles"][0][0].signature_message_fragment)
    
    ans = TryteString(signature_message_fragment).decode()
    return ans

#TXN_BUNDLE = "KDEUKSKBHGIJKWVULZNEVYIRUBXUJWXIWJLQRAEPDCSAHHBHTDNHRSPJYFKOSXCPCDESBQYXQVEGEEDGB"
#print(findmessages(TXN_BUNDLE))
