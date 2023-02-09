#Last Update 07/29/2021
#EXAMPLE:<zp_list_xanes2d(e_list,dets1, zpssx,-3,3,50,zpssy,-3,3,50,0.03)
#calib = np.arange(9.66,9.7,0.0005)

import numpy as np
from datetime import datetime
import pandas as pd
import os

ZnXANES= {'high_e':9.7, 'low_e':9.6, 
          'high_e_ugap':6480, 'low_e_ugap':6430,
          'high_e_crl':7, 'low_e_crl':2,
          'high_e_zpz1':50.92, 'zpz1_slope':-5.9,
          'energyList':[]}
'''
Real Scan: <zp_list_xanes2d(e_list,dets1,zpssx,-4,3,70,zpssy,-7,0,70,0.15,
                    xcen = 1.4, ycen = 2.34, alignElem = 'Fe', 
                    alignX = (-1,1,100,0.1),
                    alignY = (-1,1,100,0.1), pdfElem = ['Fe','Zn'],
                    saveLogFolder = '/data/users/2021Q2/Satish_2021Q2/CM1')


For Calibration: <zp_list_xanes2d(e_list,dets6,mot1,x_s,x_e,x_num,mot2,y_s,y_e,y_num,accq_t,
                    xcen = 0, ycen = 0, doAlignScan = False, pdfLog = False, 
                    foilCalibScan = True, peakBeam = False)
                    
'''
    
    
####---------------------------------------------------------------------#####
####---------------------------------------------------------------------#####
####---------------------------------------------------------------------#####


def generateEPoints(ePointsGen=None):
                
    if ePointsGen is None:
        ePointsGen = [(9.645, 9.665, 0.005), (9.666, 9.7, 0.0006), (9.705, 9.725, 0.005)]
    e_points = []
    for values in ePointsGen:
        e_points.extend(np.arange(values[0],values[1],values[2]))
        
    return np.round(e_points,5)
    
    
def generateEList(XANESParam=None):

    if XANESParam is None:
        XANESParam = ZnXANES
    energies = XANESParam ['energyList']
    
    e_list = pd.DataFrame()
    e_list['energy'] = energies

    high_e, low_e = XANESParam['high_e'],XANESParam['low_e']
    high_e_ugap, low_e_ugap = XANESParam['high_e_ugap'],XANESParam['low_e_ugap']
    ugap_slope = (high_e_ugap - low_e_ugap)/(high_e-low_e)
    ugap_list = high_e_ugap + (e_list['energy'] - high_e)*ugap_slope
    e_list['ugap'] = ugap_list

    high_e_crl, low_e_crl =XANESParam['high_e_crl'],XANESParam['low_e_crl']
    crl_slope = (high_e_crl - low_e_crl)/(high_e-low_e)
    crl_list = high_e_crl + (e_list['energy'] - high_e)*crl_slope
    e_list['crl_theta'] = crl_list

    zpz1_ref, zpz1_slope = XANESParam['high_e_zpz1'],XANESParam['zpz1_slope']
    zpz1_list = zpz1_ref + (e_list['energy'] - high_e)*zpz1_slope
    e_list['ZP focus'] = zpz1_list
    
    return e_list 


def peak_the_flux():
    
    yield from bps.sleep(2)
    yield from peak_bpm_y(-2,2,4)
    yield from peak_bpm_x(-15,15,5)
    yield from peak_bpm_y(-2,2,4)
    
def move_energy(e_,ugap_,zpz_,crl_th_, ignoreCRL= False, ignoreZPZ = False):
    yield from bps.sleep(1)
            
    #tuning the scanning pv on to dispable c bpms
    caput('XF:03IDC-ES{Status}ScanRunning-I', 1)  

    yield from bps.mov(e,e_)
    yield from bps.sleep(1)
    yield from bps.mov(ugap, ugap_)
    yield from bps.sleep(2)
    if not ignoreZPZ: yield from mov_zpz1(zpz_)
    yield from bps.sleep(1)
    if not ignoreCRL: yield from bps.mov(crl.p,crl_th_)
    yield from bps.sleep(1)
    

def zp_list_xanes2d(e_list,dets,mot1,x_s,x_e,x_num,mot2,y_s,y_e,y_num,accq_t,
                    xcen = 0, ycen = 0, alignX = (True,-2,2,100,0.05,'Fe', 0.7),
                    alignY = (True,-2,2,100,0.05,'Fe', 0.7), pdfElem = ('Fe','Zn'),
                    doScan = True, moveOptics = True, doAlignScan = True, 
                    pdfLog = True, foilCalibScan = False, peakBeam = True,
                    saveLogFolder = '/home/xf03id/Downloads'):

    e_list['E Readback'] = np.nan #add real energy to the dataframe
    e_list['Scan ID'] = np.nan #add scan id to the dataframe
    e_list['TimeStamp'] = pd.Timestamp.now()
    e_list['IC3'] = sclr2_ch4.get() #Ic values are useful for calibration
    e_list['IC0'] = sclr2_ch2.get() #Ic values are useful for calibration   
    e_list['Peak Flux'] = False
    
    print(e_list.head())
    yield from bps.sleep(10)#time to quit if anything wrong
    
    ic_0 = sclr2_ch2.get()
    
    #opening fast shutter for initial ic3 reading
    caput('XF:03IDC-ES{Zeb:2}:SOFT_IN:B0',1) 
    yield from bps.sleep(2)
    
    #get the initial ic3 reading for peaking the beam
    ic_3_init =  sclr2_ch4.get()
     
    #close fast shutter after initial ic3 reading
    caput('XF:03IDC-ES{Zeb:2}:SOFT_IN:B0',0) 
    
    #remeber the start positions
    zpssx_i = zpssx.position
    zpssy_i = zpssy.position


    for i in range (len(e_list)):

        yield from check_for_beam_dump(threshold=0.1*ic_0)
        
        e_t, ugap_t, crl_t, zpz_t, *others = e_list.iloc[i]
        
        if moveOptics: 
            yield from move_energy(e_t,ugap_t,zpz_t,crl_t,
                                   ignoreCRL= foilCalibScan, 
                                   ignoreZPZ = foilCalibScan)

        else: pass
        caput('XF:03IDC-ES{Zeb:2}:SOFT_IN:B0',1) #opening fast shutter
        yield from bps.sleep(2)
        if sclr2_ch4.get()<ic_3_init*0.9:
        
            if peakBeam: yield from peak_the_flux()
            fluxPeaked = True
        else:
            fluxPeaked = False
        
        ic_3 = sclr2_ch4.get()
        ic_0 = sclr2_ch2.get()

        # move to particle location for alignemnt scan
        if doAlignScan:
        
            yield from bps.mov(zpssx, xcen)
            yield from bps.mov(zpssy, ycen)
        
        #do the alignemnt scan on the xanes elem after it excited , 
        #otherwise skip or use another element

        if doAlignScan and e_list['energy'][i]<0:
            if alignX[0]:
                yield from fly1d(dets,zpssx,alignX[1],alignX[2],alignX[3],alignX[4])
                xcen = return_line_center(-1,alignX[5],alignX[6])
                yield from bps.mov(zpssx, xcen)

            if alignY[0]:
                yield from fly1d(dets,zpssy,alignY[1],alignY[2],alignY[3],alignY[4])
                ycen = return_line_center(-1,alignY[5],alignY[6])
                yield from bps.mov(zpssy, ycen)


        print(f'Current scan: {i+1}/{len(e_list)}')

        # do the fly2d scan

        if dets == dets_fs: #for fast xanes scan, no transmission (merlin) in the list

            if doScan: yield from fly2d(dets, mot1,x_s,x_e,x_num,mot2,y_s,y_e,y_num,accq_t, dead_time=0.001) 
            #dead_time = 0.001 for 0.015 dwell

        else:

            if doScan: yield from fly2d(dets, mot1,x_s,x_e,x_num,mot2,y_s,y_e,y_num,accq_t)
        yield from bps.sleep(1)
        
        # after scan done go to 0,0 to rest
        
        if doScan: yield from bps.mov(zpssx, 0)
        if doScan: yield from bps.mov(zpssy, 0)

        #ycen, xcen = return_center_of_mass_blurr(-1,'S') 
        # some cases use 2D mass center for alignemnt
        #print(ycen,xcen)

        # get some scan details and add to the list of scan id and energy

        last_sid = int(caget('XF:03IDC-ES{Status}ScanID-I'))
        e_pos = e.position
        
        #Add more info to the dataframe
        e_list['E Readback'].at[i] = e_pos #add real energy to the dataframe
        e_list['Scan ID'].at[i] = int(last_sid) #add scan id to the dataframe
        e_list['TimeStamp'].at[i] = pd.Timestamp.now()
        e_list['IC3'].at[i] = ic_3 #Ic values are useful for calibration
        e_list['IC0'].at[i] = ic_0 #Ic values are useful for calibration
        e_list['Peak Flux'].at[i] = fluxPeaked # recoed if peakflux was excecuted
        fluxPeaked = False #reset
        
        if pdfLog:
            for elem in pdfElem:
                insert_xrf_map_to_pdf(-1,elem)# plot data and add to pdf

        # save the DF in the loop so quitting a scan won't affect
        filename = f"HXN_nanoXANES_StartID{int(e_list['Scan ID'][0])}_{len(e_list)}_e_points.csv"
        e_list.to_csv(os.path.join(saveLogFolder, filename), float_format= '%.5f')

    #go back to max energy point if scans done reverese
    max_e_id = e_list['energy'].idxmax()
    e_max, ugap_max, zpz_max, crl_max, *others = e_list.iloc[max_e_id]
    
    if not np.isclose(e_list['energy'].max(), e.position):
    
        yield from move_energy(e_max,ugap_max,zpz_max,crl_max,
                               ignoreCRL= foilCalibScan,
                               ignoreZPZ = foilCalibScan)
        
        yield from peak_the_flux()

    
    else: pass
        
    
    if pdfLog: save_page() #save the pdf



