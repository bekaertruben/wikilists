import rl_api


LG_NAME     = "<insert username here>"
LG_PASSWORD = "<insert password here>"


# log in and ensure the account supports reading lists:
rl_api.clientlogin(LG_NAME, LG_PASSWORD)
try:
    rl_api.setup()
    print("set up reading lists for account")
except rl_api.ApiException as e:
    if e.code == "readinglists-db-error-already-set-up":
        print("account already has reading lists")
    else:
        raise e


# example 1: create a new list, update it to change the description, then add the page Runes to it
list_id = rl_api.create("testlist", description="this was made using my bot thingy")['id']
rl_api.update(list_id, description="this was totally not made using my bot thingy")
rl_api.create_entry(list_id, "Runes")

# example 2: for every list in the users reading lists, print all titles
lists = rl_api.readinglists()
for lst in lists:
    print(lst['name'], ":")
    entries = rl_api.readinglistentries(lst['id'])
    for entry in entries:
        print("  ", entry['title'])