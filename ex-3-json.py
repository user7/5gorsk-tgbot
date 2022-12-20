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

old = { 'a' : [1, 2, 3], 'b' : 'x', 'c' : 99 }
dump_save(old)
new = dump_load()
os.remove(dumpfile)
jold = sjson(old)
jnew = sjson(new)
if jold != jnew:
    print(f'comparison failed:\n\na: {jold}\n\nb: {jnew}\n')
    exit(1)
else:
    print(f'old.a={old["a"]}\n');
    print('ok')
