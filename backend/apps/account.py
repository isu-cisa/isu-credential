import json

def remove(account):
    f = open("static/accounts.txt", "r")
    list_content = f.read().splitlines()
    f.close()

    for obj in list_content:
        obj_json = json.loads(obj)
        if account == obj_json["account"]:
            list_content.remove(obj)

    # Write to file
    with open('static/accounts.txt', 'w') as f:
        for item in list_content:
            f.write("%s\n" % item)
