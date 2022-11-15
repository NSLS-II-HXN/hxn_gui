
#TODO change to a class later

import time, tqdm
from epics import caget, caput
from PyQt5 import QtWidgets, uic, QtCore, QtGui, QtTest
from PyQt5.QtWidgets import QMessageBox, QProgressBar

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
            self.startAutoHeBackfill = 'XF:03IDC-VA{ES:1-AutoVt:He}Cmd:Start-Cmd'
        

            self.pressure = "XF:03IDC-VA{VT:Chm-CM:1}P-I"

            

    @staticmethod
    def triggerPV(PV_name):
        caput(PV_name,1)
        tTest.QTest.qWait(2000)

    def start_pumping(self, turbo_start_pressure = 300, target_pressure = 1.2 ):
        
        
        #make sure vents are closed
        [triggerPV(pv) for pv in [self.fastVentClose,self.slowVentClose]]
        
        
        #turn on pumps 
        #make sure vents are closed
        if caget(self.fastVentStatus)==1 and caget(self.slowVentStatus)==1:

            #turn pumps on and open slow valves
            [triggerPV(pv) for pv in [self.pumpAON,self.pumpASlowOpen,self.pumpBON,self.pumpBSlowOpen]]
            
            
            while caget(self.pressure)>turbo_start_pressure:
                
                print("waiting for threshold pressure value")
                QtTest.QTest.qWait(10000)
                
            print("FAST Open triggered")
            [triggerPV(pv) for pv in [self.pumpBFastOpen,self.pumpAFastOpen]]

            
            while caget(self.pressure)>target_pressure:
                print("waiting for threshold pressure value")
                QtTest.QTest.qWait(10000)


            QtTest.QTest.qWait(10*1000)

            #close pump valves
            [triggerPV(pv) for pv in [self.pumpBFastClose,self.pumpAFastClose,
                                    self.pumpBSlowClose,self.pumpASlowClose]]

            #tun off the pumps
            [triggerPV(pv) for pv in [self.pumpAOFF,self.pumpBOFF]]
            
            #Done!
            return 

    def stop_pumping(self):

        #close pump valves
        [triggerPV(pv) for pv in [self.pumpBFastClose,self.pumpAFastClose,
                                    self.pumpBSlowClose,self.pumpASlowClose]]

        #tun off the pumps
        [triggerPV(pv) for pv in [self.pumpAOFF,self.pumpBOFF]]
            
        #Done!
        return 

    def start_vending(self, fast_open_pressure = 550):
        


        #make sure fluorescence detector is out before relasing the vaccuum
        caput('XF:03IDC-ES{Det:Vort-Ax:X}Mtr.VAL',-107)
        QtTest.QTest.qWait(10000)
        
        triggerPV(self.slowVentOpen)
        
        while caget("XF:03IDC-VA{VT:Chm-CM:1}P-I")<fast_open_pressure:

            if caget('XF:03IDC-ES{Det:Vort-Ax:X}Mtr.VAL') > -105:

                QtTest.QTest.qWait(30000)
                print("waiting for threshold pressure ")

            
            else:
                break
        
        
        triggerPV(self.fastVentOpen)
        
        return 


    def stop_vending(self):
        
        triggerPV(self.slowVentClose)
        QtTest.QTest.qWait(1000)
        triggerPV(self.fastVentClose)
        
        return 

    def auto_he_backfill(self):

        #pump valve status

        HeFillReadiness = [self.pumpBSlowStats,self.pumpASlowStats,self.pumpBFastStats,self.pumpAFastStats]

        if [caget(pvs) == 1 for pvs in HeFillReadiness]:
        
            readyForHe = True
        
        print("He backfill strats in 30 seconds; Make sure the cylider is open")
        
        QtTest.QTest.qWait(30*1000)
        #only execute if pump vales are closed
        
        if readyForHe:    
            triggerPV(self.startAutoHeBackfill)

            return 
            
        else: 
            print("One or more valves is not closed; try again")  
            return 

    def stop_he_backfill(self):
        pass



def triggerPV(PV_name):
    caput(PV_name,1)
    time.sleep(2)
    
def waitWithProgessBar(time_in_minues, pBarName):
    
    print(f"Timer started for {time_in_minues} minutes")

    timeNow = 0
    perTime = 0
    for _ in range(time_in_minues*60):
        QtTest.QTest.qWait(500)
        perTime += (timeNow+1)*100/(time_in_minues*60)
        pBarName.setValue(int(round(perTime)))
        QtTest.QTest.qWait(500)

def StartPumpingProtocol(pBarName, start = True):

        #pumping PVs

    slowVentClose = 'XF:03IDC-VA{ES:1-SlowVtVlv:Stg2}Cmd:Cls-Cmd'
    fastVentClose = 'XF:03IDC-VA{ES:1-FastVtVlv:Stg3}Cmd:Cls-Cmd'

    slowVentStatus = 'XF:03IDC-VA{ES:1-SlowVtVlv:Stg2}Sts:Cls-Sts'
    fastVentStatus = 'XF:03IDC-VA{ES:1-FastVtVlv:Stg3}Sts:Cls-Sts'

    pumpAON = 'XF:03IDC-VA{ES:1-FrPmp:A}Cmd:Start-Cmd'
    pumpBON = 'XF:03IDC-VA{ES:1-FrPmp:B}Cmd:Start-Cmd'

    pumpASlowOpen = 'XF:03IDC-VA{ES:1-SlowFrVlv:A}Cmd:Opn-Cmd'
    pumpAFastOpen = 'XF:03IDC-VA{ES:1-FastFrVlv:A}Cmd:Opn-Cmd'

    pumpBSlowOpen = 'XF:03IDC-VA{ES:1-SlowFrVlv:B}Cmd:Opn-Cmd'
    pumpBFastOpen = 'XF:03IDC-VA{ES:1-FastFrVlv:B}Cmd:Opn-Cmd'

    pumpAOFF = 'XF:03IDC-VA{ES:1-FrPmp:A}Cmd:Stop-Cmd'
    pumpBOFF = 'XF:03IDC-VA{ES:1-FrPmp:B}Cmd:Stop-Cmd'

    pumpASlowClose = 'XF:03IDC-VA{ES:1-SlowFrVlv:A}Cmd:Cls-Cmd'
    pumpAFastClose = 'XF:03IDC-VA{ES:1-FastFrVlv:A}Cmd:Cls-Cmd'

    pumpBSlowClose = 'XF:03IDC-VA{ES:1-SlowFrVlv:B}Cmd:Cls-Cmd'
    pumpBFastClose = 'XF:03IDC-VA{ES:1-FastFrVlv:B}Cmd:Cls-Cmd'

    
    if start:

        #make sure vents are closed
        
        [triggerPV(pv) for pv in [fastVentClose,slowVentClose]]
        
        
        #turn on pumps 
        #make sure vents are closed
        if caget(fastVentStatus)==1 and caget(slowVentStatus)==1:

            #turn pumps on and open slow valves
            [triggerPV(pv) for pv in [pumpAON,pumpASlowOpen,pumpBON,pumpBSlowOpen]]
            
            #wait for vaccum to reach below 300 for fast open
            waitWithProgessBar(8,pBarName[0])
            
            while caget("XF:03IDC-VA{VT:Chm-CM:1}P-I")>300:
                
                print("waiting for threshold pressure value")
                QtTest.QTest.qWait(30000)

            print("FAST Open triggered")
            [triggerPV(pv) for pv in [pumpBFastOpen,pumpAFastOpen]]

                    #wait for vaccum to reach ~1  
            waitWithProgessBar(15,pBarName[1])
            
            while caget("XF:03IDC-VA{VT:Chm-CM:1}P-I")>1.2:
                print("waiting for threshold pressure value")
                QtTest.QTest.qWait(30000)

            QtTest.QTest.qWait(2*1000)

            #close pump valves
            [triggerPV(pv) for pv in [pumpBFastClose,pumpAFastClose,
                                    pumpBSlowClose,pumpASlowClose]]

            #tun off the pumps
            [triggerPV(pv) for pv in [pumpAOFF,pumpBOFF]]
            
            #Done!
            
            return "Pumping completed Successfully, Ready for He Backfill"
            
        else: return "Closing the vents failed; Try Manually closing them"


    else:

            #close pump valves
            [triggerPV(pv) for pv in [pumpBFastClose,pumpAFastClose,
                                    pumpBSlowClose,pumpASlowClose]]

            #tun off the pumps
            [triggerPV(pv) for pv in [pumpAOFF,pumpBOFF]]

def StartAutoHeBackFill(pBarName):

    #pump valve status

    pumpBSlowStats = 'XF:03IDC-VA{ES:1-SlowFrVlv:B}Sts:Cls-Sts'
    pumpASlowStats = 'XF:03IDC-VA{ES:1-SlowFrVlv:A}Sts:Cls-Sts'
    
    pumpBFastStats = 'XF:03IDC-VA{ES:1-FastFrVlv:B}Sts:Cls-Sts'
    pumpAFastStats = 'XF:03IDC-VA{ES:1-FastFrVlv:A}Sts:Cls-Sts'
    
    #He backfill PVs
    startAutoHeBackfill = 'XF:03IDC-VA{ES:1-AutoVt:He}Cmd:Start-Cmd'
    
    HeFillReadiness = [pumpBSlowStats,pumpASlowStats,pumpBFastStats,pumpAFastStats]

    if [caget(pvs) == 1 for pvs in HeFillReadiness]:
    
        readyForHe = True
    
    print("He backfill strats in 30 seconds; Make sure the cylider is open")
    
    QtTest.QTest.qWait(30*1000)
    #only execute if pump vales are closed
    if readyForHe:    
        triggerPV(startAutoHeBackfill)
        waitWithProgessBar(15,pBarName)
        return "He backfilled; Please close the cyclinder"
        
    else: return "One or more valves is not closed; try again"
            
def ventChamber(pBarName):

    '''
    choice = QMessageBox.question(self, 'Detector has to be moved out',
                                      "Make sure this motion is safe. \n Move?", QMessageBox.Yes |
                                      QMessageBox.No, QMessageBox.No)

    if choice == QMessageBox.Yes:
        caput("XF:03IDC-ES{Diff-Ax:X}Mtr.VAL", -600)
    else:
        pass
    '''
    #make sure fluorescence detector is out before relasing the vaccuum
    caput('XF:03IDC-ES{Det:Vort-Ax:X}Mtr.VAL',-107)
    QtTest.QTest.qWait(10000)

    slowVentOpen = 'XF:03IDC-VA{ES:1-SlowVtVlv:Stg2}Cmd:Opn-Cmd'
    fastVentOpen = 'XF:03IDC-VA{ES:1-FastVtVlv:Stg3}Cmd:Opn-Cmd'

    
    triggerPV(slowVentOpen)
    waitWithProgessBar(3,pBarName[0])
    
    while caget("XF:03IDC-VA{VT:Chm-CM:1}P-I")<550:
        QtTest.QTest.qWait(30000)
        print("waiting for threshold pressure ")
    
    
    triggerPV(fastVentOpen)
    waitWithProgessBar(1,pBarName[1])

    return "vending completed"
    

    
    
class TaskThread(QtCore.QThread):
    taskFinished = QtCore.pyqtSignal()
    def run(self):
        time.sleep(3)
        self.taskFinished.emit()     
    

