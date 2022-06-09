


import time, tqdm
from epics import caget, caput
from PyQt5 import QtWidgets, uic, QtCore, QtGui, QtTest
from PyQt5.QtWidgets import QMessageBox

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

def StartPumpingProtocol(pBarName):

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
        waitWithProgessBar(10,pBarName[1])
        
        while caget("XF:03IDC-VA{VT:Chm-CM:1}P-I")>1.2:
            print("waiting for threshold pressure value")
            QtTest.QTest.qWait(30000)

        QtTest.QTest.qWait(60000)

        #close pump valves
        [triggerPV(pv) for pv in [pumpBFastClose,pumpAFastClose,
                                  pumpBSlowClose,pumpASlowClose]]

        #tun off the pumps
        [triggerPV(pv) for pv in [pumpAOFF,pumpBOFF]]
        
        #Done!
        
        return "Pumping completed Successfully, Ready for He Backfill"
        
    else: return "Closing the vents failed; Try Manually closing them"
    
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
    
    time.sleep(30)
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
    

