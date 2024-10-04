from itertools import product
from functools import reduce

def enumerateAttrs(attrs):
    for key, value in attrs.items():
        names = value.split(".")
        name = names[0]
        yield key, name

def flattenList(inList, outItem, attrs):
    for item in inList:
        assert isinstance(item, dict), f"in list only dicts are expected"
        for row in flatten(item, outItem, attrs):
            # print("flatList", row)
            yield row
            
def flattenDict(inDict, outItem, attrs):
    result = {**outItem}
    # print("flatDict.result", result)
    complexAttrs = []
    for key, value in enumerateAttrs(attrs):
        attributeValue = inDict.get(value, None)
        if isinstance(attributeValue, list):
            complexAttrs.append((key, value))
        elif isinstance(attributeValue, dict):
            complexAttrs.append((key, value))
        else:
            result[key] = attributeValue
    lists = []
    for key, value in complexAttrs:
        attributeValue = inDict.get(value, None)
        prefix = f"{value}."
        prefixlen = len(prefix)
        subAttrs = {key: value[prefixlen:] for key, value in attrs.items() if value.startswith(prefix)}
        items = list(flatten(attributeValue, result, subAttrs))
        lists.append(items)
                     
    if len(lists) == 0:
        yield result
    else:
        for element in product(*lists):
            reduced = reduce(lambda a, b: {**a, **b}, element, {})
            yield reduced
        
def flatten(inData, outItem, attrs):
    if isinstance(inData, dict):
        for item in flattenDict(inData, outItem, attrs):
            yield item
    elif isinstance(inData, list):
        for item in flattenList(inData, outItem, attrs):
            yield item
    else:
        assert False, f"Unexpected type on inData {inData}"


from itertools import product
def flatten(inData, outItem, attrs):
    convertedattrs = {}
    for key, value in attrs.items():
        convertedattrs[key] = value.split(".")
    
    def flattenList(inData, attrs):
        for item in inData:
            assert isinstance(item, dict), f"{item} is not type of dict"
            yield from flattenDict(item, attrs)
    
    def flattenDict(inData, convertedattrs):
        result = {}
        listKeys = set()
        dictKeys = set()
        for key, paths in convertedattrs.items():
            path = paths[0]
            value = inData.get(path, None)
            if isinstance(value, dict):
                dictKeys.add(path)
            elif isinstance(value, list):
                listKeys.add(path)
            else:
                result[key] = value
            
        if len(dictKeys) + len(listKeys) == 0:
            yield result
            return
        valuesToCombine = []
        for path in listKeys:
            filteredattrs = {key: value[1:] for key, value in convertedattrs.items() if path == value[0]}
            newValues = list(flattenList(inData[path], filteredattrs))
            if len(newValues) == 1:
                result = {**result, **newValues[0]}
            else:
                valuesToCombine.append(newValues)
        
        for path in dictKeys:
            filteredattrs = {key: value[1:] for key, value in convertedattrs.items() if path == value[0]}
            newValues = list(flattenDict(inData[path], filteredattrs))
            if len(newValues) == 1:
                result = {**result, **newValues[0]}
            else:
                valuesToCombine.append(newValues)
            
        if len(valuesToCombine) == 0:
            yield result
            return
        
        for ts in product(*valuesToCombine):
            toYield = {**result}
            for i in ts:
                toYield = {**toYield, **i}
            yield toYield
        
       
    if isinstance(inData, list):
        yield from flattenList(inData, convertedattrs)
    elif isinstance(inData, dict):
        yield from flattenDict(inData, convertedattrs)