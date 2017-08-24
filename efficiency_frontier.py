'''
Module will calculate an efficency frontier. Point to whatever file path
contains the data in csv format.

Data should have NO header, but be in order of label, x, y

I use y and x as used in an ICER calculation (y/x) (cost / qaly, for example)
'''

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Update folder location where we will read in data and write to
base_path = 'C:/Users/Ayman/Desktop/calculate_efficiency_frontier/'

data = []
f = open(base_path + 'data_example.csv', 'r')

# Read in data in format of a list of ... 
# []
got_header = False
for line in f:
    split_line = line.split(',')
    row = []
    row.append(split_line[0])
    row.append(float(split_line[1]))
    row.append(float(split_line[2]))
    data.append(row)

plt.style.use('seaborn-bright')
# Plot original data
originalx = [x[1] for x in data]
originaly = [y[2] for y in data] 
plt.scatter(originalx, originaly, s = 3.25, c = 'b', label = 'Original Data')

# sort inplace by the x value
data.sort(key = lambda x: x [1])

# Then, iteratively go through dataframe dropping strategies that are
# dominated; i.e. strategies where the y value is lower than the one before
# it (we already know that the x value is higher)

while True:
    end = False
    for index in range(len(data)):
        if index == len(data) - 1:
            end = True
            break
        else:
            if data[index][2] > data[index+1][2]:
                # Del instead of pop because we don't care what was deleted
                del data[index]
                # Restart from the top
                break
    if end is True:
        break

# Now comes a tricky part. We calculate ICERs between adjacent pairs and
# drop the strategies where the ICER is greater than the next pair

def get_icers():
    icers = []
    for i in range(1, len(data)):
        icers.append((data[i][2] - data[i-1][2])/
                     (data[i][1] - data[i-1][1]))
    return icers

while True:
    end = False
    icers = get_icers()
    # length of ICER's is 1 less than the length of data
    for index in range(len(icers)):
        if index == len(icers) - 1:
            end = True
            break
        else:
            if icers[index] > icers[index + 1]:
                # Del instead of pop because we don't care what was deleted
                # This is a little tricky, but assume we have icers like this:
                # 2 vs 1 -> 100
                # 3 vs 2 -> 300
                # 4 vs 3 --> 200
                # Then because 3 vs 2 is greater than 4 vs 3, we delete
                # the third strategy which is index 1 in our ICERs BUT is
                # actually index 2 in our data
                del data[index +1]
                # Restart from the top
                break
    if end is True:
        # Append ICER's
        data[0].append("N/A")
        for i in range(1, len(data)):
            data[i].append(icers[i-1])
        break

# Write final output
header = ['Label', 'X', 'Y', 'ICER']
df = pd.DataFrame(data, columns = header)
df.to_csv(base_path + 'frontier_data.csv', index = False)

finalx = [x[1] for x in data]
finaly = [y[2] for y in data]
plt.plot(finalx, finaly, 'r--', label = 'Efficiency Frontier')
plt.legend()
plt.savefig(base_path + 'graphed_data.png', dpi = 300)
plt.show()