try:
	
	from lenstools import ConvergenceMap,ShearMap
	from lenstools.defaults import load_fits_default_convergence,load_fits_default_shear

except ImportError:
	
	import sys
	sys.path.append("..")
	from lenstools import ConvergenceMap,ShearMap
	from lenstools.defaults import load_fits_default_convergence,load_fits_default_shear

import numpy as np
import matplotlib.pyplot as plt

from astropy.io import fits
from astropy.units import deg,arcsec

def two_file_loader(filename1,filename2):

	shear_file_1 = fits.open(filename1)
	angle = shear_file_1[0].header["ANGLE"]
	gamma = shear_file_1[0].data.astype(np.float)
	shear_file_1.close()

	shear_file_2 = fits.open(filename2)
	assert shear_file_2[0].header["ANGLE"] == angle
	gamma = np.array((gamma,shear_file_2[0].data.astype(np.float)))
	shear_file_2.close()

	return angle*deg,gamma




test_map = ShearMap.fromfilename("Data/shear1.fit","Data/shear2.fit",loader=two_file_loader)
test_map_conv = ConvergenceMap.fromfilename("Data/conv.fit",loader=load_fits_default_convergence)

l_edges = np.arange(200.0,50000.0,200.0)

def test_visualize1():

	assert hasattr(test_map,"gamma")
	assert hasattr(test_map,"side_angle")
	assert test_map.gamma.shape[0] == 2

	test_map.setAngularUnits(arcsec)
	test_map.visualize()
	test_map.savefig("shear.png")
	test_map.setAngularUnits(deg)

def test_EB_decompose():

	l,EE,BB,EB = test_map.decompose(l_edges,keep_fourier=True)

	assert l.shape == EE.shape == BB.shape == EB.shape

	fig,ax = plt.subplots()
	ax.plot(l,l*(l+1)*EE/(2.0*np.pi),label=r"$P_{EE}$")
	ax.plot(l,l*(l+1)*BB/(2.0*np.pi),label=r"$P_{BB}$")
	ax.plot(l,l*(l+1)*np.abs(EB)/(2.0*np.pi),label=r"$\vert P_{EB}\vert$")

	ax.set_xscale("log")
	ax.set_yscale("log")
	ax.set_xlabel(r"$l$")
	ax.set_ylabel(r"$l(l+1)P_l/2\pi$")
	
	ax.legend(loc="Upper left")

	plt.savefig("EB.png")
	plt.clf()

	fig,ax = plt.subplots()
	ax.plot(l,np.abs(EB)/np.sqrt(EE*BB))
	ax.set_xlabel(r"$l$")
	ax.set_ylabel(r"$P_{EB}/\sqrt{P_{EE}P_{BB}}$")

	plt.savefig("EB_corr.png")
	plt.clf()

def test_visualize2():

	fig,ax = plt.subplots()
	
	test_map_conv.visualize(fig,ax,cmap=plt.cm.Reds)
	test_map.sticks(fig=fig,ax=ax,pixel_step=40)

	fig.savefig("sticks.png")

def test_visualize3():

	fig,ax = plt.subplots(1,2)
	test_map.visualizeComponents(fig,ax,components="EE,BB",region=(200,20000,-20000,20000))
	fig.tight_layout()

	test_map.savefig("auto.png")

	fig,ax = plt.subplots()
	test_map.visualizeComponents(fig,ax,components="EB",region=(200,20000,-20000,20000))
	fig.tight_layout()

	test_map.savefig("cross.png")

def test_reconstruct():

	conv_reconstructed = test_map.convergence()

	fig,ax = plt.subplots(1,2,figsize=(16,8))
	
	ax0=ax[0].imshow(test_map_conv.kappa,origin="lower",interpolation="nearest",extent=[0.0,test_map_conv.side_angle.value,0.0,test_map_conv.side_angle.value])
	ax[0].set_title("Original")
	plt.colorbar(ax0,ax=ax[0])
	ax[0].set_xlabel(r"$x$(deg)")
	ax[0].set_ylabel(r"$y$(deg)")

	ax1=ax[1].imshow(conv_reconstructed.kappa,origin="lower",interpolation="nearest",extent=[0.0,conv_reconstructed.side_angle.value,0.0,conv_reconstructed.side_angle.value])
	ax[1].set_title("Reconstructed from shear")
	plt.colorbar(ax1,ax=ax[1])
	ax[1].set_xlabel(r"$x$(deg)")
	ax[1].set_ylabel(r"$y$(deg)")

	fig.tight_layout()

	plt.savefig("comparison.png")
	plt.clf()

def test_Emode():

	pure_E = np.zeros((512,257),dtype=np.complex128)
	pure_B = np.zeros((512,257),dtype=np.complex128)

	pure_E[0,250] = 2.0 + 0.0j
	pure_E[250,0] = 2.0 + 0.0j
	pure_E[250,250] = 2.0 + 0.0j

	new_shear_map = ShearMap.fromEBmodes(pure_E,pure_B,angle=1.95*deg)

	fig,ax = plt.subplots(1,3,figsize=(24,8))
	ax1 = ax[1].imshow(new_shear_map.gamma[0],origin="lower",cmap=plt.cm.PRGn,extent=[0,new_shear_map.side_angle.value,0,new_shear_map.side_angle.value])
	ax2 = ax[2].imshow(new_shear_map.gamma[1],origin="lower",cmap=plt.cm.PRGn,extent=[0,new_shear_map.side_angle.value,0,new_shear_map.side_angle.value])
	plt.colorbar(ax1,ax=ax[1])
	plt.colorbar(ax2,ax=ax[2])
	new_shear_map.sticks(ax[0],pixel_step=10,multiplier=1.5)

	ax[0].set_xlabel(r"$x$(deg)")
	ax[0].set_ylabel(r"$y$(deg)")
	
	ax[1].set_xlabel(r"$x$(deg)")
	ax[1].set_ylabel(r"$y$(deg)")
	ax[1].set_title(r"$\gamma_1$")
	
	ax[2].set_xlabel(r"$x$(deg)")
	ax[2].set_ylabel(r"$y$(deg)")
	ax[2].set_title(r"$\gamma_2$")

	fig.tight_layout()

	plt.savefig("pure_E.png")
	plt.clf()

def test_Bmode():

	pure_E = np.zeros((512,257),dtype=np.complex128)
	pure_B = np.zeros((512,257),dtype=np.complex128)

	pure_B[0,250] = 2.0 + 0.0j
	pure_B[250,0] = 2.0 + 0.0j
	pure_B[250,250] = 2.0 + 0.0j

	new_shear_map = ShearMap.fromEBmodes(pure_E,pure_B,angle=1.95*deg)

	fig,ax = plt.subplots(1,3,figsize=(24,8))
	ax1 = ax[1].imshow(new_shear_map.gamma[0],origin="lower",cmap=plt.cm.PRGn,extent=[0,new_shear_map.side_angle.value,0,new_shear_map.side_angle.value])
	ax2 = ax[2].imshow(new_shear_map.gamma[1],origin="lower",cmap=plt.cm.PRGn,extent=[0,new_shear_map.side_angle.value,0,new_shear_map.side_angle.value])
	plt.colorbar(ax1,ax=ax[1])
	plt.colorbar(ax2,ax=ax[2])
	new_shear_map.sticks(ax[0],pixel_step=10,multiplier=1.5)

	ax[0].set_xlabel(r"$x$(deg)")
	ax[0].set_ylabel(r"$y$(deg)")
	
	ax[1].set_xlabel(r"$x$(deg)")
	ax[1].set_ylabel(r"$y$(deg)")
	ax[1].set_title(r"$\gamma_1$")
	
	ax[2].set_xlabel(r"$x$(deg)")
	ax[2].set_ylabel(r"$y$(deg)")
	ax[2].set_title(r"$\gamma_2$")

	fig.tight_layout()

	plt.savefig("pure_B.png")
	plt.clf()


