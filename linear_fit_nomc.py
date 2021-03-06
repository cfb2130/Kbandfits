### This defines a function that fits portions before and after flux peak in K band.
### Put in a source id and a spectral id (and spectral type if you want) from bdnyc database or the path to a textfile. 
### The function will output a list with the source id, spectral type, first slope, its unc, second slope, and its unc.

import numpy as np
import pandas as pd
import matplotlib.pyplot as pl
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.pyplot import *



from astrodbkit import astrodb
db = astrodb.Database('/Users/cammyfbuzard/Dropbox/BDNYCdb/BDNYCdev.db')

# Defines the list that will later be populated
fitsdata = []
slopesvals = []


def linear_fit(source_id=None,spectral_id=None,textfile=None,spectral_type='',SNR=0):
	
	if source_id != None and spectral_id != None:			#### run code from BDNYC database
		shortfilename = None
		if SNR == 0:
			spec = db.query("SELECT spectrum FROM spectra WHERE id={}".format(spectral_id), fetch='one')[0]
			spec = spec.data
		else:
			wave_flux = db.query("SELECT spectrum FROM spectra WHERE id={}".format(spectral_id), fetch='one')[0]	
			wave_flux = wave_flux.data		
			err = []
			for i in wave_flux[1]:
				err.append(1.0/SNR*i)
			spec = [wave_flux[0],wave_flux[1],err]	
	
	elif textfile != None:					###### This allows you to run code from a txt file
		shortfilename = textfile.rsplit("/",1)[-1]
		shortfilename = shortfilename.rsplit(".",1)[0]
		file = np.loadtxt(textfile)
		xdata = [i[0] for i in file]
		ydata = [i[1] for i in file]
		yunc = []
		if SNR == 0:
			for i in file:	
				try:
					yunc.append(i[2])
				except IndexError:
					yunc.append(0)
		else:
			for j in ydata:	
				yunc.append(1.0/SNR*j)			
		spec = [xdata,ydata,yunc]
					
	
	## if the spectral type isn't given (in number form), it will look up the optical spec type in the database. If neither of these exist, defaults to 
	## 2.01 - 2.1.. Need to figure out what to do for models
	if not spectral_type:
		try:
			spectral_type = db.list("SELECT spectral_type FROM spectral_types WHERE regime='OPT' AND source_id={}".format(source_id)).fetchone()[0]	
		except:
			None
		
	## Picks just the K band of the spectrum (from 1.97 to 2.40 microns)
	df_toplot = pd.DataFrame(spec[0])					## wavelength	
	df_toplot[1] = spec[1]								## flux
	df_toplot[2] = spec[2]								## uncertainty	
	
	df_toplot = df_toplot[df_toplot[0] < 2.40]
	df_toplot = df_toplot[df_toplot[0] > 1.97]
	
	### Normalizing the flux and unc
	df_toplot[2] = df_toplot[2] / np.nanmean(df_toplot[1])
	df_toplot[1] = df_toplot[1] / np.nanmean(df_toplot[1]) 
	

	## Plots the normalized K band in blue.
	with PdfPages('/Users/cammyfbuzard/Desktop/{}.pdf'.format(shortfilename)) as pdf:
		pl.figure()
		pl.plot(df_toplot[0],df_toplot[1],'gray')
	
	
		#### Fit		
			
		""" Slope 1 """
		### If the spectral type is less than L5, fit from 2.05 to 2.14	
		if spectral_type < 15:
			xmin = 2.05
			xmax = 2.14

			## gets x values of just region being fit
			df_blue_1 = df_toplot.copy()
			
			df_blue_1 = df_blue_1[df_blue_1[0] < xmax]
			df_blue_1 = df_blue_1[df_blue_1[0] > xmin]
			

			## Fits the selected region to a line and gives a covariance matrix.
			fit_1 = np.polyfit(df_blue_1[0],df_blue_1[1],1,cov=True,full=False)				
			
	
			## Plots the line fit on the spectrum. 
			x = np.linspace(xmin,xmax,10000)	
			y = fit_1[0][0]*x + fit_1[0][1]	
			pl.plot(x,y,'b',linewidth=2) 
			
			
		
		### If the spectral type is L5 or above, the fit is from 2.02 to 2.1 microns. Everything else is the same as above.
		elif spectral_type >= 15:
			xmin = 2.02
			xmax = 2.1
		
			df_blue_2 = df_toplot.copy()

		
			df_blue_2 = df_blue_2[df_blue_2[0] < xmax]
			df_blue_2 = df_blue_2[df_blue_2[0] > xmin]
			
			fit_1 = np.polyfit(df_blue_2[0],df_blue_2[1],1,cov=True,full=False)				
			
			x2 = np.linspace(xmin,xmax,10000)	
			y2 = fit_1[0][0]*x2 + fit_1[0][1]		
			pl.plot(x2,y2,'c',linewidth=2)		
			

		""" slope 2 """
		## Slope 2 is fit from 2.214-2.29 (avoids Na line at ~2.2 and goes right up to CO absorption)
		## Everything is same as above.
		xmin = 2.215
		xmax = 2.29
	 
		df_red = df_toplot.copy()
	 	
	 	df_red = df_red[df_red[0] < xmax]
		df_red = df_red[df_red[0] > xmin]	
	 		
		#### Linear fit
		fit_2 = np.polyfit(df_red[0],df_red[1],1,cov=True,full=False)				


		x = np.linspace(xmin,xmax,10000)	## creates lots of x points
		y = fit_2[0][0]*x + fit_2[0][1]		## y as fnc given by polyfit
		pl.plot(x,y,'r',linewidth=2) #,label=('slope =', fit_2[0][0], 'unc =', abs_unc_slope_fit_2))		#r'Slope = -0.75 $\pm$ 0.10 $\mu m^{-1}$'))

		
		
		#### PLOT INFORMATION #####
		#title('{}'.format(source_id))
		#legend(loc=8)
		xscale('linear')
		yscale('linear')
		xlim(1.97,2.4)
		#xlim(2,2.2)
		#ylim(0.6,1.3)
		pl.tick_params(axis='both',labelsize=20)	
		xlabel(r'Wavelength ($\mu m$)',fontsize=30)
		ylabel(r'Normalized Flux ($F_{\lambda}$)',fontsize=30)
		tick_params(axis='both',labelsize=20)
	
		## Uncomment pl.show() to plot spectrum with fits on it.
		#pl.show()
		pdf.savefig()
		pl.close()


	### VERY IMPORTANT
	### This appends to the list 'fitsdata' the source id, spectral type, lower micron fit, its unc, higher micron fit, 
	### and its unc.
	fitsdata.append([source_id,spectral_type,fit_1[0][0],fit_2[0][0],shortfilename])	
		
				
	