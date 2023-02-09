


import numpy as np

#def zp_mossaic_scan(x_start, x_end, y_start, y_end, overlap_per = 70,exposure):
	 

def Mosaic_Grid(exposure_time):
	X_position = np.linspace(-45,45,4)
	Y_position = np.linspace(-45,45,4)
	smarx_i = zps.smarx.position
	smary_i = zps.smary.position
	for i in X_position:
		for j in Y_position:
			print((i,j))
			yield from bps.movr(smarx, i*0.001)
			yield from bps.movr(smary, j*0.001)
			yield from fly2d(dets1, zpssx,-15,15,30,zpssy, -15,15,30, exposure_time)
			insert_xrf_map_to_pdf(-1,'K')

			yield from bps.mov(smarx, smarx_i)
			yield from bps.mov(smary,smary_i)

			while (sclr2_ch2.get() < 5000):
				yield from bps.sleep(60)
				print('IC3 is lower than 5000, waiting...')
	save_page()






def Mosaic_Grid2(x_start = -45, x_end = 45, y_start = -45, y_end = 45, overlap = 20,
				 exposure_time = 0.03, step_size = 300):

	n_points_x = (x_end-x_start)/30 +1
	n_points_y = (y_end-y_start)/30 +1
	#assert n_points_x and n_points_y == int, "Number of steps cannot be a fraction"
	overlap_faction = 30*(1-(overlap/100))
	n_steps = 30000/step_size
	X_position = np.linspace(x_start,x_end,int(n_points_x))
	Y_position = np.linspace(y_start,y_end,int(n_points_y))

	smarx_i = zps.smarx.position
	smary_i = zps.smary.position

	for i in X_position:
		for j in Y_position:
			x_grid_center = i*overlap_faction
			y_grid_center = j*overlap_faction
			print(x_grid_center, y_grid_center)
			yield from bps.movr(smarx, x_grid_center*0.001)
			yield from bps.movr(smary, y_grid_center*0.001)
			yield from fly2d(dets1, zpssx,-15,-15,n_steps,zpssy, -15,-15,n_steps, exposure_time)
			yield from bps.mov(smarx, smarx_i)
			yield from bps.mov(smary,smary_i)
			# add pdf export here
			#
			while (sclr2_ch2.get() < 5000):
				yield from bps.sleep(60)
				print('IC3 is lower than 5000, waiting...')
	save_page()


def OwlScan_Multi():
    OwlScan(0.05)
    #OwlScan(0.25)
    #OwlScan(0.5)
	
		
		
'''
	yield from bps.mov(ssx, 0)        
            
            
	yield from bps.mov(ssy, 0)
	yield from fly2d(dets2, ssx, -2, 2, 400, ssy, -2, 2, 400, 0.05)
	plot_img_sum(-1,det = 'merlin2')  
	insertFig(note = 'Night Scans, 03/13/2019', title = ' ')
	plt.close()
	merlin2.unstage() 
	
	yield from smll_kill_piezos()
	yield from bps.movr(p_sbz, 50)
	yield from smll_sync_piezos()
	yield from fermat(dets2,ssx,ssy, 5, 5, 0.05, 1, 1)  
	'''

                                                                                                                                         
