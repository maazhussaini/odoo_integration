prod = [['maaz'], ['zeeshan', 'shani'], ['hasan']]

name = ['adnan', 'yasir', 'hasan']

a = []
for i in range(len(name)):
    
    if len(prod[i]) > 1:
        a.append([])
        for j in range(len(prod[i])):
            var = {'key': prod[i][j]}
            a[i].append(var)
    else:
        a.append({})
        for j in range(len(prod[i])):
            a[i]['pro'] = prod[i][j]


print(a)