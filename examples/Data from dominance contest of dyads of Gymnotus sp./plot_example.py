## Importing libraries

import numpy as np
import pylab as pl


## Parameters

# Parameters
tf      = 300.   # in miliseconds
channel = 4      # channel id

# Definitions
freq    = 45454.545454
npoints = tf * freq / 1000
color = (0.3,0.3,0.3)

t = np.linspace(0, tf, npoints)


## Preparing plot

# Creating plot
f = pl.figure(figsize=(9., 6.))
ax = pl.subplot(2, 2, 1 )

# Creating each position
ax_f1 = pl.subplot2grid((2,2), (0,0))
ax_f2 = pl.subplot2grid((2,2), (0,1))
ax_2f = pl.subplot2grid((2,2), (1,0), colspan=2)


# Plotting fish 1
X = np.memmap("15o04000.abf.memampf32", dtype=np.float32)
Ch = X[channel::11]
ax_f1.plot(t, Ch[:npoints], '-', color=color)

ax_f1.set_title("Fish 1")
ax_f1.set_xlabel("Time (ms)")
ax_f1.set_xticks(np.arange(0,301,100))
ax_f1.set_ylabel("Electrode potential (V)")
ax_f1.set_ylim(-0.2,0.2)
ax_f1.set_yticks(np.arange(-0.2,0.21,0.1))


# Plotting fish 2
X = np.memmap("15o04001.abf.memampf32", dtype=np.float32)
Ch = X[channel::11]
ax_f2.plot(t, Ch[:npoints], '-', color=color)

ax_f2.set_title("Fish 2")
ax_f2.set_xlabel("Time (ms)")
ax_f2.set_xticks(np.arange(0,301,100))
ax_f2.set_ylabel("Electrode potential (V)")
ax_f2.set_ylim(-0.2,0.2)
ax_f2.set_yticks(np.arange(-0.2,0.21,0.1))


# Plotting both fish together
X = np.memmap("15o03000.abf.memampf32", dtype=np.float32)
Ch = X[channel::11]
ax_2f.plot(t, Ch[:npoints], '-', color=color)

ax_2f.set_title("Both fish ")
ax_2f.set_xlabel("Time (ms)")
ax_2f.set_xticks(np.arange(0,301,50))
ax_2f.set_ylabel("Electrode potential (V)")
ax_2f.set_ylim(-0.2,0.2)
ax_2f.set_yticks(np.arange(-0.2,0.21,0.1))



# Finilizing the plot
pl.tight_layout(pad=1., rect=(0,0,1,0.93))
pl.savefig("Example of Plot.png", dpi=200)
