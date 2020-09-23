import numpy as np
import random, sys
from collections import Counter

#call like this: py -i script.py 10000
#where 10000 is any evenly divisible integer above 2.

s = np.random.randint(sys.argv[1]) #size
luckyNum = np.random.randint(sys.argv[1]) #must be 50% or higher
luckyZone = np.ones(int(s/2))*luckyNum
randomZone = np.random.randint(sys.argv[1], size=int(s/2))
#arr = np.c_[randomZone, luckyZone]
arr = np.concatenate([randomZone,luckyZone])
arr = np.append(arr,luckyNum)

countDict = dict(Counter(arr))

answer = max(countDict, key=countDict.get)

print(f'The value {answer} occurs {countDict[answer]} times and the length of the array is {s}')

#print(f'unshuffled: {arr}\nshuffled:{random.sample(list(arr),len(arr))}')
#print(f'{Counter(arr)}')
