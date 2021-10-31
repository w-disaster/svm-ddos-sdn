#!/usr/bin/python3
#import pylab as plb
import matplotlib.pyplot as plt

fig1=plt.figure(1)
ax = fig1.add_subplot(1,2,1)

ax.plot([1,2,3],[4,5,6],'ro-')

ax1 = fig1.add_subplot(1,2,2)
ax1.plot([1,2,3],[2,2,2],'ro-')
#fig1.show()  # this does not show a figure if uncommented
plt.ion()     # turns on interactive mode
plt.show()    # now this should be non-blocking

"""print("doing something else now")
input('Press Enter to continue...')

#fig1=plt.figure(1)
ax = fig1.add_subplot(1,2,1)
ax1 = fig1.add_subplot(1,2,2)
ax.plot([1,2,3],[7,8,9], 'ro-')
ax1.plot([4,4,5],[5,9,19], 'ro-')
plt.ion()
plt.show()

input('daje')"""