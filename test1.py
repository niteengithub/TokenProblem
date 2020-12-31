a = {}

try:
    del a['a']
except KeyError as ex:
    print('Token Deleted!')
