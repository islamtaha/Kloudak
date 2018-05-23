import json

f = open('/home/maged/gradproject/Network/conf.json')
text = ''
for line in f:
    text += line
conf_dict = json.loads(text)
key = conf_dict['key']
broker = conf_dict['broker']
dbserver = conf_dict['dbserver']
f.close()