
#TODO change to a class later

import time, tqdm
from epics import caget, caput
from PyQt5 import QtWidgets, uic, QtCore, QtGui, QtTest
from PyQt5.QtWidgets import QMessageBox, QProgressBar
from PyQt5.QtCore import QTime

class SampleExchangeProtocol():

    def __init__(self):

            #pumping PVs

            self.slowVentClose = 'XF:03IDC-VA{ES:1-SlowVtVlv:Stg2}Cmd:Cls-Cmd'
            self.fastVentClose = 'XF:03IDC-VA{ES:1-FastVtVlv:Stg3}Cmd:Cls-Cmd'

            self.slowVentOpen = 'XF:03IDC-VA{ES:1-SlowVtVlv:Stg2}Cmd:Opn-Cmd'
            self.fastVentOpen = 'XF:03IDC-VA{ES:1-FastVtVlv:Stg3}Cmd:Opn-Cmd'

            self.slowVentStatus = 'XF:03IDC-VA{ES:1-SlowVtVlv:Stg2}Sts:Cls-Sts'
            self.fastVentStatus = 'XF:03IDC-VA{ES:1-FastVtVlv:Stg3}Sts:Cls-Sts'

            self.pumpAON = 'XF:03IDC-VA{ES:1-FrPmp:A}Cmd:Start-Cmd'
            self.pumpBON = 'XF:03IDC-VA{ES:1-FrPmp:B}Cmd:Start-Cmd'

            self.pumpASlowOpen = 'XF:03IDC-VA{ES:1-SlowFrVlv:A}Cmd:Opn-Cmd'
            self.pumpAFastOpen = 'XF:03IDC-VA{ES:1-FastFrVlv:A}Cmd:Opn-Cmd'

            self.pumpBSlowOpen = 'XF:03IDC-VA{ES:1-SlowFrVlv:B}Cmd:Opn-Cmd'
            self.pumpBFastOpen = 'XF:03IDC-VA{ES:1-FastFrVlv:B}Cmd:Opn-Cmd'

            self.pumpAOFF = 'XF:03IDC-VA{ES:1-FrPmp:A}Cmd:Stop-Cmd'
            self.pumpBOFF = 'XF:03IDC-VA{ES:1-FrPmp:B}Cmd:Stop-Cmd'

            self.pumpASlowClose = 'XF:03IDC-VA{ES:1-SlowFrVlv:A}Cmd:Cls-Cmd'
            self.pumpAFastClose = 'XF:03IDC-VA{ES:1-FastFrVlv:A}Cmd:Cls-Cmd'

            self.pumpBSlowClose = 'XF:03IDC-VA{ES:1-SlowFrVlv:B}Cmd:Cls-Cmd'
            self.pumpBFastClose = 'XF:03IDC-VA{ES:1-FastFrVlv:B}Cmd:Cls-Cmd'

            self.pumpBSlowStats = 'XF:03IDC-VA{ES:1-SlowFrVlv:B}Sts:Cls-Sts'
            self.pumpASlowStats = 'XF:03IDC-VA{ES:1-SlowFrVlv:A}Sts:Cls-Sts'
            
            self.pumpBFastStats = 'XF:03IDC-VA{ES:1-FastFrVlv:B}Sts:Cls-Sts'
            self.pumpAFastStats = 'XF:03IDC-VA{ES:1-FastFrVlv:A}Sts:Cls-Sts'

            #He backfill PVs
            self.he_valve = 'XF:03IDC-ES{IO:1}DO:4-Cmd'
            self.startAutoHeBackfill = 'XF:03IDC-VA{ES:1-AutoVt:He}Cmd:Start-Cmd'
        

            self.pressure = "XF:03IDC-VA{VT:Chm-CM:1}P-I"

            

    def triggerPV(self,PV_name):
        caput(PV_name,1)
        QtTest.QTest.qWait(2000)


        

    def start_slow_pumps(self):

        #make sure vents are closed
        [self.triggerPV(pv) for pv in [self.fastVentClose,self.slowVentClose]]

        #turn on pumps 
        #make sure vents are closed
        if caget(self.fastVentStatus)==1 and caget(self.slowVentStatus)==1:

            #turn pumps on and open slow valves
            [self.triggerPV(pv) for pv in [self.pumpAON,self.pumpASlowOpen,self.pumpBON,self.pumpBSlowOpen]]

    
    def start_fast_pumps(self):

            print ("fast pumps triggered")
            attempt = 0
            
            while True:
            
                caput(self.pumpAFastOpen,1)
                caput(self.pumpBFastOpen,1)

                if caget("XF:03IDC-VA{ES:1-FastFrVlv:A}Sts:Cls-Sts") == 0:
                    break
                
                attempt+=1
                QtTest.QTest.qWait(5000)
                if attempt>20:
                    print ("error opening fast pumps")
                    break



    def stop_pumping(self):

        #close pump valves
        [self.triggerPV(pv) for pv in [self.pumpBFastClose,self.pumpAFastClose,
                                    self.pumpBSlowClose,self.pumpASlowClose]]

        #tun off the pumps
        [self.triggerPV(pv) for pv in [self.pumpAOFF,self.pumpBOFF]]
            
        #Done!
        return 

            

    def start_pumps(self, turbo_start_pressure = 400, target_pressure = 1.2 ):
        
        #while lopp end after 1 hour

        endtime = QTime.currentTime().addSecs(3600)
        
        #make sure vents are closed
        [self.triggerPV(pv) for pv in [self.fastVentClose,self.slowVentClose]]
        
        if turbo_start_pressure<target_pressure:
            turbo_start_pressure = target_pressure

        
        #turn on pumps 
        #make sure vents are closed
        if caget(self.fastVentStatus)==1 and caget(self.slowVentStatus)==1:

            #turn pumps on and open slow valves
            [self.triggerPV(pv) for pv in [self.pumpAON,self.pumpASlowOpen,self.pumpBON,self.pumpBSlowOpen]]
            
            
            while caget(self.pressure)>turbo_start_pressure:
                
                print(f"waiting for threshold pressure value {turbo_start_pressure} for turbo")
                QtTest.QTest.qWait(10*1000)
                
            print("FAST Open triggered")
            [self.triggerPV(pv) for pv in [self.pumpBFastOpen,self.pumpAFastOpen]]

            if not target_pressure>turbo_start_pressure:

                while caget(self.pressure)>target_pressure:

                    print(f"waiting for threshold target pressure value = {target_pressure}")
                    QtTest.QTest.qWait(5*1000)
                    if QTime.currentTime() > endtime:
                        break
                    


            QtTest.QTest.qWait(1000)

            #close pump valves
            [self.triggerPV(pv) for pv in [self.pumpBFastClose,self.pumpAFastClose,
                                    self.pumpBSlowClose,self.pumpASlowClose]]

            #tun off the pumps
            [self.triggerPV(pv) for pv in [self.pumpAOFF,self.pumpBOFF]]
            
            #Done!
            return 

    def stop_pumping(self):

        #close pump valves
        [self.triggerPV(pv) for pv in [self.pumpBFastClose,self.pumpAFastClose,
                                    self.pumpBSlowClose,self.pumpASlowClose]]

        #tun off the pumps
        [self.triggerPV(pv) for pv in [self.pumpAOFF,self.pumpBOFF]]
            
        #Done!
        return 

    def open_slow_vent(self):

        #make sure fluorescence detector is out before relasing the vaccuum
        caput('XF:03IDC-ES{Det:Vort-Ax:X}Mtr.VAL',-107)
        QtTest.QTest.qWait(10000)

        self.triggerPV(self.slowVentOpen)


    def open_fast_vent(self):
        
        self.triggerPV(self.fastVentOpen)

    
    
    def start_venting(self):
        
        #make sure fluorescence detector is out before relasing the vaccuum
        caput('XF:03IDC-ES{Det:Vort-Ax:X}Mtr.VAL',-107)
        QtTest.QTest.qWait(10000)
        
        self.triggerPV(self.slowVentOpen)
        
        while caget("XF:03IDC-VA{VT:Chm-CM:1}P-I")<550:

            QtTest.QTest.qWait(10000)
            print(f'waiting for threshold pressure {caget("XF:03IDC-VA{VT:Chm-CM:1}P-I")}<550')
            
        for i in range(5):
            print("fast vent opened ")
            self.triggerPV(self.fastVentOpen)
            QtTest.QTest.qWait(5000)


    def stop_vending(self):
        
        self.triggerPV(self.slowVentClose)
        QtTest.QTest.qWait(1000)
        self.triggerPV(self.fastVentClose)
        
        return 

    def auto_he_backfill(self):

        self.stop_pumping()

        #pump valve status
        HeFillReadiness = [self.pumpBSlowStats,self.pumpASlowStats,self.pumpBFastStats,self.pumpAFastStats]

        if [caget(pvs) == 1 for pvs in HeFillReadiness]:
        
            readyForHe = True
        
        print("He backfill strats in 10 seconds; Make sure the cylider is open")
        
        QtTest.QTest.qWait(10*1000)
        #only execute if pump vales are closed
        
        if readyForHe:
            
            self.triggerPV(self.startAutoHeBackfill)

        else: 
            print("One or more valves is not closed; try again") 

        
            

    def stop_he_backfill(self):
        pass

