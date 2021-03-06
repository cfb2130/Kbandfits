import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from astrodbkit import astrodb
db = astrodb.Database('/Users/cammyfbuzard/Code/Python/BDNYC/BDNYCdev.db')

import montecarlotest_2 as mc

sources = pd.DataFrame(db.list("SELECT source_id FROM spectral_types WHERE gravity=('g') and regime='OPT'").fetchall())
sources = sources.drop_duplicates()

#### no unresolved binaries

comp = []
for i in sources[0]:
	try:
		comp.append(db.list("SELECT components FROM sources WHERE id={}".format(i)).fetchone()[0])
	except TypeError:
		comp.append(1)	
for index,item in enumerate(comp):
	if item == None:
		comp[index] = 1
	else:
		comp[index] = None	
sources[1] = comp				
sources = sources.dropna()	


### No companions

comp = []
for i in sources[0]:
	try:
		comp.append(db.list("SELECT companions FROM sources WHERE id={}".format(i)).fetchone()[0])
	except TypeError:
		comp.append(1)	
for index,item in enumerate(comp):
	if item == None:
		comp[index] = 1
	else:
		comp[index] = None	
sources[1] = comp				
sources = sources.dropna()	


#### no objects that appear elsewhere

elsewhere = []
for i in sources[0]:
	if i == 241 or i == 825 or i == 869 or i == 51 or i == 778 or i == 69 or i == 287 or i == 458 or i == 725 or i == 1309 or i == 1721 or i == 1352 or i == 1307 or i == 1508 or i == 1378:
		elsewhere.append(None)
	else:
		elsewhere.append(i)
sources[1] = elsewhere
sources = sources.dropna()


#### no T dwarfs (those will use IR spectral types)

tdwarfs = []
for i in sources[0]:
	tdwarfs.append(db.list("SELECT spectral_type FROM spectral_types WHERE regime='OPT' AND source_id={}".format(i)).fetchone()[0])
noTs = []
for i in tdwarfs:
	if i >= 7.0 and i <= 19.5:
		noTs.append(i)
	else:
		noTs.append(None)
sources[1] = noTs
sources = sources.dropna()		


#### any betas?? Not anymore!

grav = []
for i in sources[0]:
	grav.append(db.list("SELECT gravity FROM spectral_types WHERE regime='OPT' AND source_id={}".format(i)).fetchone()[0])
for num,i in enumerate(grav):
	if i == 'g':
		grav[num] = 1
	else:
		grav[num] = None
sources[1] = grav
sources = sources.dropna()			


#### spectral ids

spectral_ids = []
for i in sources[0]:
	try:
		spectral_ids.append(db.list("SELECT id FROM spectra WHERE source_id={} AND regime='NIR' AND instrument_id=6 AND mode_id=1".format(i)).fetchone()[0])
	except TypeError:
		spectral_ids.append(None)		
sources[1] = spectral_ids					
sources = sources.dropna()



lowgrav = []			
for i,j in zip(sources[0],sources[1]):
	lowgrav.append([i,j])

##### Add in the ones not in planet_sample
J1147 = [1516,2719]
PSO318 = [1721,23]
lowgrav.append(J1147)
lowgrav.append(PSO318)
	
	
### Run

for i in range(len(lowgrav)):
	mc.linear_fit(lowgrav[i][0],lowgrav[i][1])
	
	
### Gather info

source_id = []
for i in range(len(mc.slopesvals)):
	source_id.append(mc.slopesvals[i][0])	
spectral_id = []
for i in range(len(mc.slopesvals)):
	spectral_id.append(mc.slopesvals[i][1])	
blue_slope = []
for i in range(len(mc.slopesvals)):
	blue_slope.append(mc.slopesvals[i][2])	
blue_std = []
for i in range(len(mc.slopesvals)):
	blue_std.append(mc.slopesvals[i][3])
red_slope = []
for i in range(len(mc.slopesvals)):
	red_slope.append(mc.slopesvals[i][4])
red_std = []
for i in range(len(mc.slopesvals)):
	red_std.append(mc.slopesvals[i][5])	
sptype = []
for i in range(len(mc.slopesvals)):
	sptype.append(mc.slopesvals[i][6])	
filename = []
for i in range(len(mc.slopesvals)):
	filename.append(mc.slopesvals[i][7])

df = pd.DataFrame(source_id)
df[1] = spectral_id
df[2] = blue_slope
df[3] = blue_std
df[4] = red_slope
df[5] = red_std
df[6] = sptype
df[7] = filename

df.columns = ['source_id','spectral_id','blue_slope','blue_std','red_slope','red_std','sp_type','filename']		

df.to_csv('/Users/cammyfbuzard/Desktop/Monte_Carlo/06_09_16/Low_gravities/montecarlo_fits.txt',sep=',',index=False)										
			

					
