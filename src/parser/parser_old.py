class package: 
    def __init__(self, data, i=0): 
        self.data = data 
        self.index = i 

def load_arr(data, i=1, json={}): 

    string = "" 
    arr = [] 

    while i < len(data):
        if data[i] == '{': 
            packet = load_dict(data, i+1, json)
            i = packet.index
            arr.append(packet.data)
            continue 
        if data[i] == ']':
            string = string.split(',')
            for j, k in enumerate(string, 0): 
                string[j] = k.strip() 
                string[j] = string[j].replace('"', '') 
                if len(string[j]) > 0: 
                    arr.append(string[j]) 
            break 

        if data[i] not in ['\n']: 
            string += data[i] 

        i+=1 
    return package(arr, i+1) 


def load_dict(data, i=1, json={}, final={}):
    temp = {} 
    string = key = '' 
    while i < len(data): 
        if data[i] in ['{', '}', '[']: 
            if type(string) == str: 
                string = string.splitlines()

            for j, k in enumerate(string, 0):
                if type(k) != list: 
                    string[j] = k.rstrip("',',': '") 
                    string[j] = string[j].lstrip()

                    string[j] = string[j].replace('"', '') 

                    key = value = '' 
                    CHECK = KEY = True 
                    VALUE = False 

                    for letter in string[j]: 
                        if letter == ':' and CHECK and KEY: 
                            KEY = CHECK = False 
                            VALUE = True 
                            continue 
                        if not VALUE: 
                            key += letter 
                        if not KEY: 
                            value += letter 

                    value = value.lstrip() 

                    if key != '':
                        temp[key] = value

            string = ""
            if data[i] == '{': 
                packet = load_dict(data, i+1, json)
                i = packet.index 
                if key != '':
                    temp[key] = packet.data 
                else:  
                    for key in packet.data: 
                        json[key] = packet.data[key] 

                if i < len(data)-1: 
                    continue 
                else: 
                    if key:
                        if key == str(next(iter(temp))): 
                            return package(temp) 
                        else: 
                            final[key] = json 
                            return package(final) 
                    else: 
                        return package(json) 
            elif data[i] == '}': 
                return package(temp, i+1) 
            elif data[i] == '[': 
                packet = load_arr(data, i+1, json)
                i = packet.index
                temp[key] = packet.data
                continue 

        string += data[i] 
        i+=1
    return package(final) 


def load(infile): 
    return load_dict(infile.read()).data