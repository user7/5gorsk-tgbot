import json
import os

dumpfile = "ex-3.json"

def dump_save(data):
    with open(dumpfile, 'w', encoding = 'utf-8') as f:
        json.dump(data, f)

def dump_load():
    with open(dumpfile, 'r', encoding = 'utf-8') as f:
        return json.load(f)

def sjson(d):
    return json.dumps(d, sort_keys = True, indent = 2)

old = { 'a' : [1, 2, 3], 'b' : 'x', 'c' : 99,
        'truth' : { 'bool' : True, 'num0' : 0, 'num1' : 1, 'empty' : '', 'full' : '0' } }
dump_save(old)
new = dump_load()
os.remove(dumpfile)
jold = sjson(old)
jnew = sjson(new)

def check_truth(dic, key):
    s = "false"
    try:
        if dic[key]:
            s = "true"
    except KeyError:
        s = "KeyError"
    except:
        s = "generic exception"
    print(f'{key} -> {s}')


if jold != jnew:
    print(f'comparison failed:\n\na: {jold}\n\nb: {jnew}\n')
    exit(1)
else:
    d = old['truth']
    check_truth(d, 'bool')
    check_truth(d, 'num0')
    check_truth(d, 'num1')
    check_truth(d, 'empty')
    check_truth(d, 'full')
    check_truth(d, 'undef')
    print('ok')
