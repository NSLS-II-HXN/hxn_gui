
# __Author__: Ajith Pattammattel
# Original Date:06-23-2020

import os
import signal
import subprocess
import sys
import collections
import webbrowser
import pyqtgraph as pg
import json
import matplotlib
from functools import partial 
from scipy.ndimage import rotate
from epics import caget, caput

from PyQt5 import QtWidgets, uic, QtCore, QtGui, QtTest
from PyQt5.QtWidgets import QMessageBox, QFileDialog, QApplication, QLCDNumber, QLabel, QErrorMessage
from PyQt5.QtCore import QObject, QTimer, QThread, pyqtSignal, pyqtSlot, QRunnable, QThreadPool, QDate

from pdf_log import *
from xanes2d import *
from xanesFunctions import *
from HXNSampleExchange import *
HXNSampleExchanger = SampleExchangeProtocol()



ui_path = os.path.dirname(os.path.abspath(__file__))

class Ui(QtWidgets.QMainWindow):
   
    def __init__(self):
        super(Ui, self).__init__()
        
        uic.loadUi(os.path.join(ui_path,'hxn_gui_v3.ui'), self)
        self.initParams()
        self.ImageCorrelationPage()
        self.client = webbrowser.get('firefox')
        self.threadpool = QThreadPool()
        self.tw_hxn_contact.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        self.energies = []
        self.roiDict = {}

        self.motor_list = {'zpssx': zpssx, 'zpssy': zpssy, 'zpssz': zpssz,
        'dssx': dssx, 'dssy': dssy, 'dssz': dssz}


        

        self.dwell.valueChanged.connect(self.initParams)
        self.x_step.valueChanged.connect(self.initParams)
        self.y_step.valueChanged.connect(self.initParams)
        self.x_start.valueChanged.connect(self.initParams)
        self.y_start.valueChanged.connect(self.initParams)
        self.x_end.valueChanged.connect(self.initParams)
        self.y_end.valueChanged.connect(self.initParams)

        # logic control for 1d or 2d scan selection
        self.rb_1d.clicked.connect(self.disableMot2)
        self.rb_2d.clicked.connect(self.enableMot2)
        self.rb_1d.clicked.connect(self.initParams)
        self.rb_2d.clicked.connect(self.initParams)

        #Abort scan plan
        self.pb_reqPause.clicked.connect(self.requestScanPause)
        self.pb_REAbort.clicked.connect(self.scanAbort)
        self.pb_REResume.clicked.connect(self.scanResume)

        # text files and editor controls
        self.pb_save_cmd.clicked.connect(self.save_file)
        self.pb_clear_cmd.clicked.connect(self.clear_cmd)
        self.pb_new_macro_gedit.clicked.connect(self.open_gedit)
        self.pb_new_macro_vi.clicked.connect(self.open_vi)
        self.pb_new_macro_emacs.clicked.connect(self.open_emacs)
        self.pb_browse_a_macro.clicked.connect(self.get_a_file)
        self.pb_ex_macro_open.clicked.connect(self.open_a_macro)

        # plotting controls
        self.pb_close_all_plot.clicked.connect(self.close_all_plots)
        self.pb_plot.clicked.connect(self.plot_me)
        self.pb_erf_fit.clicked.connect(self.plot_erf_fit)
        self.pb_plot_line_center.clicked.connect(self.plot_line_center)


        # xanes parameters
        self.pb_gen_elist.clicked.connect(self.generateDataFrame)
        self.pb_set_epoints.clicked.connect(self.generate_epoints)
        self.pb_print_xanes_param.clicked.connect(lambda: self.ple_info.setPlainText(str(self.xanesParamsDict)))
        self.pb_display_xanes_plan.clicked.connect(self.displayXANESPlan)
        #self.pb_Start_Xanes.clicked.connect(self.runZPXANES)
        self.pb_xanes_rsr_fldr.clicked.connect(self.getXanesUserFolder)

        # scans and motor motion
        self.start.clicked.connect(self.initFlyScan)
        #self.start.clicked.connect(self.liveUpdateThread)
        #self.start.clicked.connect(self.flyThread)


        if False: #self.rb_mll.isChecked():
            #zpmotors
            self.pb_move_smarx_pos.clicked.connect(self.move_dsx)
            self.pb_move_smary_pos.clicked.connect(self.move_dsy)
            self.pb_move_smarz_pos.clicked.connect(self.move_dsz)
            self.pb_move_dth_pos.clicked.connect(self.move_dsth)
            self.pb_move_zpz_pos.clicked.connect(self.move_zpz1)

            self.pb_move_smarx_neg.clicked.connect(lambda: self.move_dsx(neg_=True))
            self.pb_move_smary_neg.clicked.connect(lambda: self.move_dsy(neg_=True))
            self.pb_move_smarz_neg.clicked.connect(lambda: self.move_dsz(neg_=True))
            self.pb_move_dth_pos_neg.clicked.connect(lambda: self.move_dsth(neg_=True))
            self.pb_move_zpz_neg.clicked.connect(lambda: self.move_zpz1(neg_=True))

        else:


            self.pb_move_smarx_pos.clicked.connect(self.move_smarx)
            self.pb_move_smary_pos.clicked.connect(self.move_smary)
            self.pb_move_smarz_pos.clicked.connect(self.move_smarz)
            self.pb_move_dth_pos.clicked.connect(self.move_dsth)
            self.pb_move_zpz_pos.clicked.connect(self.move_zpz1)

            self.pb_move_smarx_neg.clicked.connect(lambda: self.move_smarx(neg_=True))
            self.pb_move_smary_neg.clicked.connect(lambda: self.move_smary(neg_=True))
            self.pb_move_smarz_neg.clicked.connect(lambda: self.move_smarz(neg_=True))
            self.pb_move_dth_pos_neg.clicked.connect(lambda: self.move_dsth(neg_=True))
            self.pb_move_zpz_neg.clicked.connect(lambda: self.move_zpz1(neg_=True))

        # Detector/Camera Motions

        #Merlin
        self.pb_merlinOUT.clicked.connect(self.merlinOUT)
        self.pb_merlinIN.clicked.connect(self.merlinIN)
        #fluorescence det
        self.pb_vortexOUT.clicked.connect(self.vortexOUT)
        self.pb_vortexIN.clicked.connect(self.vortexIN)
        #cam06
        self.pb_cam6IN.clicked.connect(self.cam6IN)
        self.pb_cam6OUT.clicked.connect(self.cam6OUT)
        self.pb_CAM6_IN.clicked.connect(self.cam6IN)
        self.pb_CAM6_OUT.clicked.connect(self.cam6OUT)
        #cam11
        self.pb_cam11IN.clicked.connect(self.cam11IN)

        # sample exchange
        #self.pb_start_pump.clicked.connect (lambda:StartPumpingProtocol([self.prb_pump_slow,self.prb_pump_fast]))
        #self.pb_auto_he_fill.clicked.connect(lambda: StartAutoHeBackFill(self.prb_he_backfill))
        #self.pb_vent.clicked.connect(lambda:ventChamber([self.prb_vent_slow,self.prb_vent_fast]))

        # sample exchange
        #self.pb_start_pump.clicked.connect(self.pumpThread)
        #self.pb_auto_he_fill.clicked.connect(self.heBackFillThread)
        #self.pb_vent.clicked.connect(self.ventThread)
        self.pb_vent.clicked.connect(HXNSampleExchanger.start_vending)
        self.pb_stop_vent.clicked.connect(HXNSampleExchanger.stop_vending)
        self.pb_start_pump.clicked.connect(self.pumping_start_thread)
        self.pb_stop_pump.clicked.connect(self.pumping_stop)
        self.pb_auto_he_fill.clicked.connect(HXNSampleExchanger.auto_he_backfill)

        #SSA2 motion
        self.pb_SSA2_Open.clicked.connect(lambda:self.SSA2_Pos(2.1, 2.1))
        self.pb_SSA2_Close.clicked.connect(lambda:self.SSA2_Pos(0.05, 0.03))
        self.pb_SSA2_Close.clicked.connect(lambda:self.SSA2_Pos(0.05, 0.03))
        self.pb_SSA2_HClose.clicked.connect(lambda:self.SSA2_Pos(0.1, 2.1))
        self.pb_SSA2_VClose.clicked.connect(lambda:self.SSA2_Pos(2.1, 0.1))

        #s5 slits
        self.pb_S5_Open.clicked.connect(lambda:self.S5_Pos(4,4))
        self.pb_S5_Close.clicked.connect(lambda:self.S5_Pos(0.28,0.28))
        self.pb_S5_HClose.clicked.connect(lambda:self.S5_Pos(0.1,0.28))
        self.pb_S5_VClose.clicked.connect(lambda:self.S5_Pos(0.28,0.1))

        #front end
        self.pb_FS_IN.clicked.connect(self.FS_IN)
        self.pb_FS_OUT.clicked.connect(self.FS_OUT)

        #OSA Y Pos
        self.pb_osa_out.clicked.connect(self.ZP_OSA_OUT)
        self.pb_osa_in.clicked.connect(self.ZP_OSA_IN)

        #alignment
        self.pb_ZPZFocusScanStart.clicked.connect(self.zpFocusScan)
        self.pb_MoveZPZ1AbsPos.clicked.connect(self.zpMoveAbs)


        # sample position
        self.pb_save_pos.clicked.connect(self.generatePositionDict)
        self.pb_roiList_import.clicked.connect(self.importROIDict)
        self.pb_roiList_export.clicked.connect(self.exportROIDict)
        self.pb_roiList_clear.clicked.connect(self.clearROIList)
        #self.sampleROI_List.itemClicked.connect(self.showROIPos)
        #self.sampleROI_List.itemClicked.connect(lambda: self.ple_info.appendPlainText(
            #(str(self.roiDict[self.sampleROI_List.currentItem().text()]))))

        self.sampleROI_List.itemClicked.connect(self.showROIPosition)

        self.pb_move_pos.clicked.connect(self.gotoROIPosition)
        self.pb_recover_scan_pos.clicked.connect(self.gotoPosSID)
        self.pb_show_scan_pos.clicked.connect(self.viewScanPosSID)
        self.pb_print_scan_meta.clicked.connect(self.viewScanMetaData)
        self.pb_copy_curr_pos.clicked.connect(self.copyPosition)

        # Quick fill scan Params
        self.pb_3030.clicked.connect(self.fill_common_scan_params)
        self.pb_2020.clicked.connect(self.fill_common_scan_params)
        self.pb_66.clicked.connect(self.fill_common_scan_params)
        self.pb_22.clicked.connect(self.fill_common_scan_params)

        #copy scan plan
        self.pb_scan_copy.clicked.connect(self.copyScanPlan)
        self.pb_batchscan_copy.clicked.connect(self.copyForBatch)

        # elog
        self.pb_pdf_wd.clicked.connect(self.select_pdf_wd)
        self.pb_pdf_image.clicked.connect(self.select_pdf_image)
        self.pb_save_pdf.clicked.connect(self.force_save_pdf)
        self.pb_createpdf.clicked.connect(self.generate_pdf)
        self.pb_fig_to_pdf.clicked.connect(self.InsertFigToPDF)
        self.dateEdit_elog.setDate(QDate.currentDate())

        # admin control
        self.pb_apply_user_settings.clicked.connect(self.setUserLevel)

        # close the application
        self.actionClose_Application.triggered.connect(self.close_application)

        self.create_live_pv_dict()
        self.create_pump_pv_dict()
        

        self.liveUpdateThread()
        self.scanStatusThread()
        self.pump_update_thread()

        self.show()
  
    def create_live_pv_dict(self):
        '''
        generate a dictionary of slots and signals , 
        later change to a json for flexibity ,; like mll specific?
        '''

        self.live_PVs = {

            self.lcd_ic3:"XF:03IDC-ES{Sclr:2}_cts1.D",
            self.lcd_monoE:"XF:03ID{}Energy-I",
            self.lcdPressure:"XF:03IDC-VA{VT:Chm-CM:1}P-I",
            self.lcd_scanNumber:"XF:03IDC-ES{Status}ScanID-I",
            self.db_smarx:smarx,
            self.db_smary:smary,
            self.db_smarz:smarz,
            self.db_zpsth:zpsth,
            self.lcd_ZpTh:zpsth,
            self.db_zpz1:zp.zpz1,
            self.db_ssa2_x:ssa2.hgap,
            self.db_ssa2_y:ssa2.vgap,
            self.db_fs:"XF:03IDA-OP{FS:1-Ax:Y}Mtr.RBV",
            self.db_cam6:"XF:03IDC-OP{Stg:CAM6-Ax:X}Mtr.RBV",
            self.db_fs_det:fdet1.x,
            self.db_diffx:diff.x,
            self.db_cam06x:"XF:03IDC-OP{Stg:CAM6-Ax:X}Mtr.RBV",
            self.db_s5_x:s5.hgap,
            self.db_s5_y:s5.vgap,

            }
        
    def create_pump_pv_dict(self):
        '''
        1--> valves closed, 0--> open
        could not find PVs
        self.rb_pumpA_on:
        self.rb_pumpB_on:
        self.rb_he_backfill_fail:
        '''


        self.pump_PVs = {

            self.rb_slow_vent:"XF:03IDC-VA{ES:1-SlowVtVlv:Stg2}Sts:Cls-Sts",
            self.rb_fast_vent:"XF:03IDC-VA{ES:1-FastVtVlv:Stg3}Sts:Cls-Sts",
            self.rb_pumpA_slow:"XF:03IDC-VA{ES:1-SlowFrVlv:A}Cmd:Opn-Cmd",
            self.rb_pumpA_fast:"XF:03IDC-VA{ES:1-FastFrVlv:A}Cmd:Opn-Cmd",
            self.rb_pumpB_slow:"XF:03IDC-VA{ES:1-SlowFrVlv:B}Cmd:Opn-Cmd",
            self.rb_pumpB_fast:"XF:03IDC-VA{ES:1-FastFrVlv:B}Cmd:Opn-Cmd",
            
            }

    def handle_value_signals(self,pv_val_list):
        #print ("updating live values")
        livePVs = {key:value for key, value in zip(self.live_PVs.keys(),pv_val_list)}
        for item in livePVs.items():
                item[0].setValue(item[1])

    def handle_bool_signals(self,pv_val_list):
    
        #self.pump_PVs.keys() = pv_val_list (works?)
        livePVs = {key:value for key, value in zip(self.pump_PVs.keys(),pv_val_list)}
        for item in livePVs.items():
                item[0].setChecked(item[1])
                

    def scanStatus(self,sts):

        if sts==1:
            self.label_scanStatus.setText("        Scan in Progress       ")
            self.label_scanStatus.setStyleSheet("background-color:rgb(0, 255, 0);color:rgb(255,0, 0)")
        else:
            self.label_scanStatus.setText("         Idle        ")
            self.label_scanStatus.setStyleSheet("background-color:rgb(255, 255, 0);color:rgb(0, 255, 0)")

    def scanStatusThread(self):

        self.scanStatus_thread = liveStatus("XF:03IDC-ES{Status}ScanRunning-I")
        self.scanStatus_thread.current_sts.connect(self.scanStatus)
        self.scanStatus_thread.start()

    def liveUpdateThread(self):
        print("Thread Started")

        self.liveWorker = liveUpdate(self.live_PVs)
        self.liveWorker.current_positions.connect(self.handle_value_signals)
        self.liveWorker.start()

    def pump_update_thread(self):
        print("Pump Update Thread Started")
        self.pump_update_worker = liveUpdate(self.pump_PVs,update_interval_ms = 2000)
        self.pump_update_worker.current_positions.connect(self.handle_bool_signals)
        self.pump_update_worker.start()

    def scanStatusMonitor(self):
        scanStatus = caget("XF:03IDC-ES{Status}ScanRunning-I")
        if scanStatus == 1:
            self.label_scanStatus.setText("Scan in Progress")
            self.label_scanStatus.setStyleSheet("background-color:rgb(0, 255, 0);color:rgb(255,0, 0)")

        else:
            self.label_scanStatus.setText("Idle")
            self.label_scanStatus.setStyleSheet("background-color:rgb(255, 255, 0);color:rgb(0, 255, 0)")

    def setUserLevel(self):

        self.userButtonEnabler(self.cb_det_user, self.gb_det_control)
        self.userButtonEnabler(self.cb_xanes_user, self.rb_xanes_scan)
        self.userButtonEnabler(self.cb_xanes_user, self.gb_xanes_align)

    def userButtonEnabler(self, checkbox_name, control_btn_grp_name):

        if checkbox_name.isChecked():
            control_btn_grp_name.setEnabled(True)
        else:
            control_btn_grp_name.setEnabled(False)

    def getScanValues(self):
        self.det = self.pb_dets.currentText()

        self.mot1_s = self.x_start.value()
        self.mot1_e = self.x_end.value()
        self.mot1_steps = self.x_step.value()

        self.mot2_s = self.y_start.value()
        self.mot2_e = self.y_end.value()
        self.mot2_steps = self.y_step.value()

        self.dwell_t = self.dwell.value()

        self.motor1 = self.cb_motor1.currentText()
        self.motor2 = self.cb_motor2.currentText()


        self.det_list = {'dets1': dets1, 'dets2': dets2, 'dets3': dets3,
                         'dets4': dets4, 'dets_fs': dets_fs}

    def initParams(self):
        self.getScanValues()

        cal_res_x = abs(self.mot1_e - self.mot1_s) / self.mot1_steps
        cal_res_y = abs(self.mot2_e - self.mot2_s) / self.mot2_steps
        tot_t_2d = self.mot1_steps * self.mot2_steps * self.dwell_t / 60
        tot_t_1d = self.mot1_steps * self.dwell_t / 60

        if self.rb_1d.isChecked():
            self.label_scan_info_calc.setText(f'X: {(cal_res_x * 1000):.2f} nm, Y: {(cal_res_y * 1000):.2f} nm \n'
                                              f'{tot_t_1d:.2f} minutes + overhead')
            self.scan_plan = f'fly1d({self.det},{self.motor1}, {self.mot1_s},{self.mot1_e}, ' \
                        f'{self.mot1_steps}, {self.dwell_t:.3f})'



        else:
            self.label_scan_info_calc.setText(f'X: {(cal_res_x * 1000):.2f} nm, Y: {(cal_res_y * 1000):.2f} nm \n'
                                              f'{tot_t_2d:.2f} minutes + overhead')
            self.scan_plan = f'fly2d({self.det}, {self.motor1},{self.mot1_s}, {self.mot1_e}, {self.mot1_steps},' \
                        f'{self.motor2},{self.mot2_s},{self.mot2_e},{self.mot2_steps},{self.dwell_t:.3f})'

        self.text_scan_plan.setText(self.scan_plan)

    def copyForBatch(self):
        self.text_scan_plan.setText('yield from '+self.scan_plan)
        self.text_scan_plan.selectAll()
        self.text_scan_plan.copy()

    def copyScanPlan(self):
        self.text_scan_plan.setText('<'+self.scan_plan)
        self.text_scan_plan.selectAll()
        self.text_scan_plan.copy()

    def initFlyScan(self):
        self.getScanValues()

        if self.rb_1d.isChecked():
            RE(fly1d(self.det_list[self.det], self.motor_list[self.motor1],
                     self.mot1_s, self.mot1_e, self.mot1_steps, self.dwell_t))

        else:
            if self.motor_list[self.motor1] == self.motor_list[self.motor2]:
                msg = QErrorMessage(self)
                msg.setWindowTitle("Flyscan Motors are the same")
                msg.showMessage(f"Choose two different motors for 2D scan. You selected {self.motor_list[self.motor1].name}")
                return
            else:

                RE(fly2d(self.det_list[self.det], self.motor_list[self.motor1], self.mot1_s, self.mot1_e, self.mot1_steps,
                        self.motor_list[self.motor2], self.mot2_s, self.mot2_e, self.mot2_steps, self.dwell_t))

    def flyThread(self):
        flyWorker = Worker(self.initFlyScan)
        self.threadpool.start(flyWorker)

    def disableMot2(self):
        self.y_start.setEnabled(False)
        self.y_end.setEnabled(False)
        self.y_step.setEnabled(False)

    def enableMot2(self):
        self.y_start.setEnabled(True)
        self.y_end.setEnabled(True)
        self.y_step.setEnabled(True)

    def fill_common_scan_params(self):
        button_name = self.sender()
        button_names = {'pb_2020': (20, 20, 100, 100, 0.03),
                        'pb_3030': (30, 30, 30, 30, 0.03),
                        'pb_66': (6, 6, 100, 100, 0.05),
                        'pb_22': (2, 2, 100, 100, 0.03)
                        }
        if button_name.objectName() in button_names.keys():
            valsToFill = button_names[button_name.objectName()]
            self.x_start.setValue(valsToFill[0] / -2)
            self.x_end.setValue(valsToFill[0] / 2)
            self.y_start.setValue(valsToFill[1] / -2)
            self.y_end.setValue(valsToFill[1] / 2)
            self.x_step.setValue(valsToFill[2])
            self.y_step.setValue(valsToFill[3])
            self.dwell.setValue(valsToFill[4])

    def requestScanPause(self):
        RE.request_pause(True)
        self.pb_REAbort.setEnabled(True)
        self.pb_REResume.setEnabled(True)

    def scanAbort(self):
        RE.abort()
        self.pb_REAbort.setEnabled(False)
        self.pb_REResume.setEnabled(False)

    def scanResume():
        RE.resume()
        self.pb_REAbort.setEnabled(False)
        self.pb_REResume.setEnabled(False)

    def moveAMotor(self, val_box, mot_name, unit_conv_factor: float = 1, neg=False):

        if neg:
            move_by = val_box.value() * -1
        else:
            move_by = val_box.value()

        RE(bps.movr(mot_name, move_by * unit_conv_factor))
        self.ple_info.appendPlainText(f'{mot_name.name} moved by {move_by} um ')

    def move_smarx(self, neg_=False):
        self.moveAMotor(self.db_move_smarx, smarx, 0.001, neg=neg_)

    def move_smary(self, neg_=False):
        self.moveAMotor(self.db_move_smary, smary, 0.001, neg=neg_)

    def move_smarz(self, neg_=False):
        self.moveAMotor(self.db_move_smarz, smarz, 0.001, neg=neg_)

    def move_dsth(self, neg_=False):
        self.moveAMotor(self.db_move_dth, zpsth, neg=neg_)

    def move_zpz1(self, neg_=False):
        if neg_:

            RE(movr_zpz1(self.db_move_zpz.value() * 0.001 * -1))

        else:
            RE(movr_zpz1(self.db_move_zpz.value() * 0.001))

    #mll

    def move_dsx(self, neg_=False):
        self.moveAMotor(self.db_move_smarx, dsx, 1, neg=neg_)

    def move_dsy(self, neg_=False):
        self.moveAMotor(self.db_move_smary, dsy, 1, neg=neg_)

    def move_dsz(self, neg_=False):
        self.moveAMotor(self.db_move_smarz, dsz, 1, neg=neg_)

    def move_dsth(self, neg_=False):
        self.moveAMotor(self.db_move_dth, dsth, neg=neg_)



    def ZP_OSA_OUT(self):
        curr_pos = caget("XF:03IDC-ES{ANC350:5-Ax:1}Mtr.VAL")
        if curr_pos >2000:
            self.ple_info.appendPlainText('OSAY is out of IN range')
        else:
            caput("XF:03IDC-ES{ANC350:5-Ax:1}Mtr.VAL",curr_pos+2700)

        self.ple_info.appendPlainText('OSA Y moved OUT')

    def ZP_OSA_IN(self):
        curr_pos = caget("XF:03IDC-ES{ANC350:5-Ax:1}Mtr.VAL")

        if curr_pos > 2500:
            caput("XF:03IDC-ES{ANC350:5-Ax:1}Mtr.VAL",curr_pos-2700)
            self.ple_info.appendPlainText('OSA Y is IN')
        else:
            self.ple_info.appendPlainText('OSA Y is close to IN position')
            pass

    def merlinIN(self):
        self.client.open('http://10.66.17.43')
        choice = QMessageBox.question(self, 'Detector Motion Warning',
                                      "Make sure this motion is safe. \n Move?", QMessageBox.Yes |
                                      QMessageBox.No, QMessageBox.No)

        if choice == QMessageBox.Yes:
            RE(go_det('merlin'))
        else:
            pass

    def merlinOUT(self):
        self.client.open('http://10.66.17.43')
        choice = QMessageBox.question(self, 'Detector Motion Warning',
                                      "Make sure this motion is safe. \n Move?", QMessageBox.Yes |
                                      QMessageBox.No, QMessageBox.No)

        if choice == QMessageBox.Yes:
            RE(bps.mov(diff.x, -600))
        else:
            pass

    def vortexIN(self):
        RE(bps.mov(fdet1.x, -7))
        caput("XF:03IDC-ES{Det:Vort-Ax:X}Mtr.VAL", -7)
        self.ple_info.appendPlainText('FS det Moving')

    def vortexOUT(self):
        #RE(bps.mov(fdet1.x, -107))
        caput("XF:03IDC-ES{Det:Vort-Ax:X}Mtr.VAL", -107)
        self.ple_info.appendPlainText('FS det Moving')

    def cam11IN(self):
        self.client.open('http://10.66.17.43')
        QtTest.QTest.qWait(5000)
        choice = QMessageBox.question(self, 'Detector Motion Warning',
                                      "Make sure this motion is safe. \n Move?", QMessageBox.Yes |
                                      QMessageBox.No, QMessageBox.No)

        if choice == QMessageBox.Yes:
            RE(go_det('cam11'))
            self.ple_info.appendPlainText('CAM11 is IN')
        else:
            pass

    def cam6IN(self):
        caput('XF:03IDC-OP{Stg:CAM6-Ax:X}Mtr.VAL', 0)
        QtTest.QTest.qWait(1000)
        self.ple_info.appendPlainText('CAM6 Moving!')

    def cam6OUT(self):
        caput('XF:03IDC-OP{Stg:CAM6-Ax:X}Mtr.VAL', -50)
        QtTest.QTest.qWait(1000)
        self.ple_info.appendPlainText('CAM6 Moving!')

    def FS_IN(self):
        caput('XF:03IDA-OP{FS:1-Ax:Y}Mtr.VAL', -57.)
        caput("XF:03IDA-BI{FS:1-CAM:1}cam1:Acquire",1)
        QtTest.QTest.qWait(20000)
        #self.ple_info.appendPlainText('FS Motion Done!')

    def FS_OUT(self):
        caput('XF:03IDA-OP{FS:1-Ax:Y}Mtr.VAL', -20.)
        caput("XF:03IDA-BI{FS:1-CAM:1}cam1:Acquire",0)
        QtTest.QTest.qWait(20000)
        #self.ple_info.appendPlainText('FS Motion Done!')

    def SSA2_Pos(self, x, y):
        caput('XF:03IDC-OP{Slt:SSA2-Ax:XAp}Mtr.VAL', x)
        caput('XF:03IDC-OP{Slt:SSA2-Ax:YAp}Mtr.VAL', y)
        QtTest.QTest.qWait(15000)

    def S5_Pos(self, x, y):
        caput('XF:03IDC-ES{Slt:5-Ax:Vgap}Mtr.VAL', x) #PV names seems flipped
        caput('XF:03IDC-ES{Slt:5-Ax:Hgap}Mtr.VAL', y)
        QtTest.QTest.qWait(15000)

    def plot_me(self):
        sd = self.pb_plot_sd.text()
        elem = self.pb_plot_elem.text()

        if ',' in sd:
            slist_s, slist_e = sd.split(",")

            f_sd = int(slist_s.strip())
            l_sd = int(slist_e.strip())
            space = abs(int(slist_e.strip())-int(slist_s.strip()))+1

            s_list = np.linspace(f_sd, l_sd, space)
            for sd_ in s_list:
                plot_data(int(sd_), elem, 'sclr1_ch4')

        else:
            plot_data(int(sd), elem, 'sclr1_ch4')

    def plot_erf_fit(self):
        sd = self.pb_plot_sd.text()
        elem = self.pb_plot_elem.text()
        erf_fit(int(sd), elem, linear_flag=self.cb_erf_linear_flag.isChecked())

    def plot_line_center(self):
        sd = self.pb_plot_sd.text()
        elem = self.pb_plot_elem.text()
        return_line_center(int(sd), elem, threshold=self.dsb_line_center_thre.value())

    def close_all_plots(self):
        plt.close('all')

    #xanes
    def getXanesUserFolder(self):
        self.xanes_folder = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.le_xanes_user_folder.setText(self.xanes_folder)

    def generate_epoints(self):

        pre = (self.dsb_pre_s.value(), self.dsb_pre_e.value(), self.sb_pre_p.value())
        XANES1 = (self.dsb_ed1_s.value(), self.dsb_ed1_e.value(), self.sb_ed1_p.value())
        XANES2 = (self.dsb_ed2_s.value(), self.dsb_ed2_e.value(), self.sb_ed2_p.value())
        post = (self.dsb_post_s.value(), self.dsb_post_e.value(), self.sb_post_p.value())

        self.energies = generateEPoints(ePointsGen=[pre,XANES1,XANES2,post])
        self.ple_info.setPlainText(str(self.energies))

    def importEPoints(self):
        file_name = QFileDialog().getOpenFileName(self, "Save Parameter File", ' ',
                                                                 'txt file(*txt)')

        if file_name:
            self.energies = np.loadtxt(file_name[0])
        else:
            pass

    def exportEPoints(self):
        self.generate_epoints()
        file_name = QFileDialog().getSaveFileName(self, "Save Parameter File",
                                                            'xanes_e_points.txt',
                                                            'txt file(*txt)')
        if file_name:
            np.savetxt(file_name[0],np.array(self.energies))
        else:
            pass

    def importXanesParams(self):

        file_name = QFileDialog().getOpenFileName(self, "Load Parameter File", ' ',
                                                                 'json file(*json)')
        if file_name:
            with open(file_name[0], 'r') as fp:
                self.xanesParam = json.load(fp)
        else:
            pass

        self.fillXanesParamBoxes(self.xanesParam)

    def exportXanesParams(self):
        self.xanesParam = {}
        e_pos = {'low': self.dsb_monoe_l.value(), 'high':self.dsb_monoe_h.value()}
        zpz1_pos = {'low': self.dsb_zpz_l.value(), 'high': self.dsb_zpz_h.value()}

        self.xanesParam['mono_e'] = e_pos
        self.xanesParam['zpz1'] = zpz1_pos

        file_name = QFileDialog().getSaveFileName(self, "Save Parameter File",
                                                            'hxn_xanes_parameters.json',
                                                            'json file(*json)')
        if file_name:

            with open(f'{file_name[0]}', 'w') as fp:
                json.dump(self.xanesParam,fp, indent=4)
        else:
            pass

    def fillXanesParamBoxes(self,xanesParam:dict ):

        e_low, e_high = xanesParam['mono_e']['low'], xanesParam['mono_e']['high']
        ugap_low, ugap_high = xanesParam['ugap']['low'], xanesParam['ugap']['high']
        zpz1_low, zpz1_high = xanesParam['zpz1']['low'], xanesParam['zpz1']['high']

        self.dsb_monoe_l.setValue(e_low), self.dsb_monoe_h.setValue(e_high)
        self.dsb_zpz_l.setValue(zpz1_low), self.dsb_zpz_h.setValue(zpz1_high)
        self.le_crl_combo_xanes.setText(crl_combo)

    def loadCommonXanesParams(self):
        with open(os.path.join('.','xanes_common_elem_params.json'), 'r') as fp:
            self.commonXanesParam = json.load(fp)

    def insertCommonXanesParams(self):
        mot_list = [self.dsb_monoe_l, self.dsb_monoe_h, self.dsb_zpz_l, self.dsb_zpz_h]
        commonElems = self.commonXanesParam.keys()

        button_name = self.sender().objectName()
        if button_name in commonElems:
            elemParam = self.commonXanesParam[button_name]
            self.fillXanesParamBoxes(elemParam)

        else:
            pass

    def generateDataFrame(self):
        self.xanesParamsDict = {'high_e': self.dsb_monoe_h.value(), 'low_e': self.dsb_monoe_l.value(),
                   'high_e_zpz1': self.dsb_zpz_h.value(), 'zpz1_slope': self.dsb_zpz_slope.value(),
                   'energy': list(self.energies)}

        if not len(self.energies) == 0:
            self.e_list = generateEList(XANESParam=self.xanesParamsDict)
            # print(energies)
            self.ple_info.setPlainText(str(self.e_list))

        else:
            self.statusbar.showMessage('No energy list found; set or load an e list first')

    def initXANESParams(self):
        self.getScanValues()

        self.doXAlign, self.doYAlign = self.cb_x_align.isChecked(),self.cb_y_align.isChecked()
        self.x_align_s, self.x_align_e = self.x_align_start.value(), self.x_align_end.value()
        self.x_align_stp, self.x_align_dw = self.x_align_steps.value(), self.x_align_dwell.value()
        self.align_x_thr, self.x_align_elem = self.align_x_threshold.value(), self.le_x_align_elem.text()

        self.y_align_s, self.y_align_e = self.y_align_start.value(), self.y_align_end.value()
        self.y_align_stp, self.y_align_dw = self.y_align_steps.value(), self.y_align_dwell.value()
        self.align_y_thr, self.y_align_elem = self.align_y_threshold.value(), self.le_y_align_elem.text()

        self.elemPlot = tuple(self.plot_elem_xanes.text().split(','))
        self.xanes_folder = self.le_xanes_user_folder.text()

    def displayXANESPlan(self):
        self.generateDataFrame()
        self.initXANESParams()

        scan_plan = f"<zp_list_xanes2d({self.xanesParamsDict}, {self.det},{self.motor1},{self.mot1_s}, {self.mot1_e}, {self.mot1_steps}," \
                    f"{self.motor2},  {self.mot2_s}, {self.mot2_e}, {self.mot2_steps}, {self.dwell_t}," \
                    f"alignX={(self.x_align_s, self.x_align_e, self.x_align_stp, self.x_align_dw,self.x_align_elem, self.align_x_thr,self.doXAlign)}," \
                    f"alignY={(self.y_align_s, self.y_align_e, self.y_align_stp,self.y_align_dw, self.y_align_elem, self.align_y_thr,self.doYAlign,)}," \
                    f"pdfElem={self.elemPlot},saveLogFolder={self.xanes_folder})"

        self.te_xanes_plan.setText(str(scan_plan))

    def fillCurrentPos(self):
         e_ = e.position
         zpz1_ = zp.zpz1.position

         self.dsb_monoe_h.setValue(e_)
         self.dsb_zpz_h.setValue(zpz1_)

    def runZPXANES(self):
        self.initXANESParams()

        dE = e.position - self.e_list['energy'][0]

        if dE < 1:
            '''
            RE(zp_list_xanes2d(self.xanesParamsDict,
                               self.det_list[self.det],
                               self.motor_list[self.motor1],
                               self.mot1_s,
                               self.mot1_e,
                               self.mot1_steps,
                               self.motor_list[self.motor2],
                               self.mot2_s,
                               self.mot2_e,
                               self.mot2_steps,
                               self.dwell_t,
                               alignX=(self.x_align_s,
                                       self.x_align_e,
                                       self.x_align_stp,
                                       self.x_align_dw,
                                       self.x_align_elem,
                                       self.align_x_thr,
                                       self.doXAlign),
                               alignY=(self.y_align_s,
                                       self.y_align_e,
                                       self.y_align_stp,
                                       self.y_align_dw,
                                       self.y_align_elem,
                                       self.align_y_thr,
                                       self.doYAlign),
                               pdfElem=self.elemPlot,
                               saveLogFolder=self.xanes_folder))
            '''
            print (" Test Passed")
        else:

            msg = QErrorMessage
            msg.setWindowTitle("Energy change error")
            msg.showMessage("Requested energy change is far from current position")
            return

    #tomo
    def zpTomoStepResCalc(self):
        pass

    def zpTomo(self):

        startAngle = self.sb_tomo_start_angle.value()
        endAngle = self.sb_tomo_end_angle.value()
        stepsAngle = self.sb_tomo_steps.value()

        xAlignStart = None
        xAlignEnd = None
        xAlignSteps = None
        xAlignDwell = None
        xAlignElem = None
        xAlignThreshold = None

        yAlignStart = None
        yAlignEnd = None
        yAlignSteps = None
        yAlignDwell = None
        yAlignElem = None
        yAlignThreshold = None

    #special scans
    def zpMosaic(self):
        pass

    def zpFocusScan(self):
        zpStart = self.sb_ZPZ1RelativeStart.value()*0.001
        zpEnd = self.sb_ZPZ1RelativeEnd.value()*0.001
        zpSteps = self.sb_ZPZ1Steps.value()

        scanMotor = self.motor_list[self.cb_foucsScanMotor.currentText()]
        scanStart = self.sb_FocusScanMtrStart.value()
        scanEnd = self.sb_FocusScanMtrEnd.value()
        scanSteps = self.sb_FocusScanMtrStep.value()
        scanDwell = self.dsb_FocusScanDwell.value()

        fitElem = self.le_FocusingElem.text()
        linFlag = self.cb_linearFlag_zpFocus.isChecked()

        RE(zp_z_alignment(zpStart,zpEnd,zpSteps,scanMotor,scanStart,scanEnd,scanSteps,scanDwell,
                          elem= fitElem, linFlag = linFlag))

    def zpMoveAbs(self):
        zpTarget = self.dsb_ZPZ1TargetPos.value()
        choice = QMessageBox.question(self, "Zone Plate Z Motion",
                                      f"You're making an Absolute motion of ZP to {zpTarget}. \n Proceed?",
                                      QMessageBox.Yes |
                                      QMessageBox.No, QMessageBox.No)
        QtTest.QTest.qWait(500)
        if choice == QMessageBox.Yes:
            RE(mov_zpz1(zpTarget))

        else:
            pass

    def zpRotAlignment(self):
        pass

    #custom macros

    def save_file(self):
        S__File = QFileDialog.getSaveFileName(None, 'SaveFile', '/', "Python Files (*.py)")

        Text = self.pte_run_cmd.toPlainText()
        if S__File[0]:
            with open(S__File[0], 'w') as file:
                file.write(Text)

    def clear_cmd(self):
        self.pte_run_cmd.clear()

    def open_gedit(self):
        subprocess.Popen(['gedit'])

    def open_vi(self):
        subprocess.Popen(['vi'])

    def open_emacs(self):
        subprocess.Popen(['emacs'])

    def get_a_file(self):
        file_name = QFileDialog().getOpenFileName(self, "Open file")
        self.le_ex_macro.setText(str(file_name[0]))

    def open_a_macro(self):
        editor = self.cb_ex_macro_with.currentText()
        filename = self.le_ex_macro.text()

        subprocess.Popen([editor, filename])

    def abort_scan(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        RE.abort()

    #Sample Chamber
    def qMessageExcecute(self,funct):
        QtTest.QTest.qWait(500)
        choice = QMessageBox.question(self, 'Sample Chamber Operation Warning',
                                      "Make sure this action is safe. \n Proceed?", QMessageBox.Yes |
                                      QMessageBox.No, QMessageBox.No)
        QtTest.QTest.qWait(500)
        if choice == QMessageBox.Yes:
            RE(funct)

        else:
            pass

    # PDF Log

    def select_pdf_wd(self):
        folder_path = QFileDialog().getExistingDirectory(self, "Select Folder")
        self.le_folder_log.setText(str(folder_path))

    def select_pdf_image(self):
        file_name = QFileDialog().getOpenFileName(self, "Select an Image")
        self.le_elog_image.setText(str(file_name[0]))

    def generate_pdf(self):
        dt = self.dateEdit_elog.date()
        tmp_date = dt.toString(self.dateEdit_elog.displayFormat())
        tmp_file = os.path.join(self.le_folder_log.text(), self.le_elog_name.text())
        tmp_sample = self.le_elog_sample.text()
        tmp_experimenter = self.le_elog_experimenters.text()
        tmp_pic = self.le_elog_image.text()

        setup_pdf_for_gui(tmp_file, tmp_date, tmp_sample, tmp_experimenter, tmp_pic)
        insertTitle_for_gui()
        self.statusbar.showMessage(f'pdf generated as {tmp_file}')

    def force_save_pdf(self):
        save_page_for_gui()

    def InsertFigToPDF(self):
        insertFig_for_gui(note=self.le_pdf_fig_note.text(),
                          title=self.le_pdf_fig_title.text())
        self.statusbar.showMessage("Figure added to the pdf")

    # Sample Stage Navigation
    def recordPositions(self):

        fx, fy, fz = zpssx.position, zpssy.position, zpssz.position
        cx, cy, cz = smarx.position, smary.position, smarz.position
        zpz1_pos = zp.zpz1.position
        zp_sx, zp_sz = zps.zpsx.position, zps.zpsz.position
        th = zpsth.position
        self.roi = {
            zpssx: fx, zpssy: fy, zpssz: fz,
            smarx: cx, smary: cy, smarz: cz,
            zp.zpz1: zpz1_pos, zpsth: th,
            zps.zpsx: zp_sx, zps.zpsz: zp_sz
        }

    def generatePositionDict(self):

        self.recordPositions()
        roi_name = 'ROI' + str(self.sampleROI_List.count())
        self.roiDict[roi_name] = self.roi
        self.sampleROI_List.addItem(roi_name)

        #make the item editable
        item = self.sampleROI_List.item(self.sampleROI_List.count()-1)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)

    def applyDictWithLabel(self):
        label_ = {}
        for idx in range(self.sampleROI_List.count()):
            label = self.sampleROI_List.item(idx).text()
            label_[label] = idx
        self.roiDict['user_labels'] = label_

    def exportROIDict(self):
        self.applyDictWithLabel()
        file_name = QFileDialog().getSaveFileName(self, "Save Parameter File",
                                                  'hxn_zp_roi_list.json',
                                                  'json file(*json)')
        if file_name:

            with open(file_name[0], 'w') as fp:
                json.dump(self.roiDict, fp, indent=4)
        else:
            pass

    def importROIDict(self):

        file_name = QFileDialog().getOpenFileName(self, "Open Parameter File",
                                                  ' ', 'json file(*json)')
        if file_name:
            self.roiDict = {}
            with open(file_name[0], 'r') as fp:
                self.roiDict = json.load(fp)

            print(self.roiDict['user_labels'])

            self.sampleROI_List.clear()
            for num,items in enumerate(self.roiDict['user_labels']):
                self.sampleROI_List.addItem(items)
                item = self.sampleROI_List.item(num)
                item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
        else:
            pass

    def clearROIList(self):
        self.sampleROI_List.clear()

    def showROIPos(self,item):
        item_num = self.sampleROI_List.row(item)
        for key, value in self.roiDict[f'ROI{item_num}'].items():
            self.ple_info.appendPlainText(f'{key.name}:{value:.4f}')

    def gotoROIPosition(self):
        roi_num = self.sampleROI_List.currentRow()
        param_file = self.roiDict[f'ROI{roi_num}']
        for key, value in param_file.items():
            if not key == zp.zpz1:
                RE(bps.mov(key, value))
            elif key == zp.zpz1:
                RE(mov_zpz1(value))
            self.ple_info.appendPlainText(f'Sample moved to {key.name}:{value:.4f} ')

    def showROIPosition(self, item):
        item_num = self.sampleROI_List.row(item)
        param_file = self.roiDict[f'ROI{item_num}']
        self.ple_info.appendPlainText(('*' * 20))
        for key, value in param_file.items():
            self.ple_info.appendPlainText(f'{key.name}:{value:.4f}')

        #self.sampleROI_List.itemClicked.connect(lambda: self.ple_info.appendPlainText(
        # (self.roiDict[self.sampleROI_List.currentItem().text()])))

    def gotoPosSID(self):
        sd = self.le_sid_position.text()
        zp_flag = self.cb_sid_moveZPZ.isChecked()

        sdZPZ1 = (db[int(sd)].table("baseline")["zpz1"].values)[0]
        currentZPZ1 = zp.zpz1.position
        #current_energy = caget("XF:03ID{}Energy-I")
        zDiff = abs(sdZPZ1-currentZPZ1)

        if zDiff>1 and zp_flag:
                choice = QMessageBox.question(self, 'Warning',
                "You are recovering positions from a scan done at a different Focus."
                "The ZPZ1 motion could cause collision. Are you sure??",
                QMessageBox.Yes |QMessageBox.No, QMessageBox.No)

                if choice == QMessageBox.Yes:
                    RE(recover_zp_scan_pos(int(sd), zp_flag, 1))
                else:
                    return
        else:

            RE(recover_zp_scan_pos(int(sd), zp_flag, 1))

        self.ple_info.appendPlainText(f'Positions recovered from {sd}')

    def viewScanPosSID(self):
        sd = self.le_sid_position.text()
        data = db.get_table(db[int(sd)],stream_name='baseline')

        zpz1 = data.zpz1[1]
        zpx = data.zpx[1]
        zpy = data.zpy[1]
        smarx = data.smarx[1]
        smary = data.smary[1]
        smarz = data.smarz[1]
        zpsz = data.zpsz[1]

        info1 = f"scan id: {db[int(sd)].start['scan_id']}, zpz1:{zpz1 :.3f}, zpsz:{zpsz :.3f} \n"
        info2 = f"smarx: {smarx :.3f}, smary: {smary :.3f}, smarz: {smarz :.3f} \n"
        info3 = f"zpssx: {data.zpssx[1] :.3f}, zpssy: {data.zpssy[1] :.3f}, zpssz: {data.zpssz[1] :.3f} \n "


        self.ple_info.appendPlainText(str(info1+info2+info3))

    def viewScanMetaData(self):
        sd = self.le_sid_position.text()
        h = db[int(sd)]
        self.ple_info.appendPlainText(str(h.start))

    def copyPosition(self):

        self.recordPositions()

        stringToCopy = ' '
        for item in self.roi.items():
            stringToCopy += (f'{item[0].name}:{item[1]:.4f} \n')

        #stringToCopy = str([item[0].name, item[1] for item in self.roi.items()])

        cb = QApplication.clipboard()
        cb.clear(mode=cb.Clipboard)
        cb.setText(stringToCopy, mode=cb.Clipboard)

    #Pumping the chamber
    def pumpThread(self):

        pumpWorker = Worker(StartPumpingProtocol([self.prb_pump_slow,self.prb_pump_fast]))
        self.threadpool.start(pumpWorker)

    def heBackFillThread(self):
        heBackFillWorker = Worker(StartAutoHeBackFill(self.prb_he_backfill))
        self.threadpool.start(heBackFillWorker)

    def ventThread(self):
        ventWorker =  Worker(ventChamber([self.prb_vent_slow,self.prb_vent_fast]))
        self.threadpool.start(ventWorker)

    #Image correlation tool

    def ImageCorrelationPage(self):

        self.coords = collections.deque(maxlen=4)

        # connections
        self.pb_RefImageLoad.clicked.connect(self.loadRefImage)
        self.pb_apply_calculation.clicked.connect(self.scalingCalculation)
        self.dsb_x_off.valueChanged.connect(self.offsetCorrectedPos)
        self.dsb_y_off.valueChanged.connect(self.offsetCorrectedPos)
        self.pb_grabXY_1.clicked.connect(self.insertCurrentPos1)
        self.pb_grabXY_2.clicked.connect(self.insertCurrentPos2)
        self.pb_import_param.clicked.connect(self.importScalingParamFile)
        self.pb_export_param.clicked.connect(self.exportScalingParamFile)
        self.pb_gotoTargetPos.clicked.connect(self.gotoTargetPos)

    def loadRefImage(self):
        self.file_name = QtWidgets.QFileDialog().getOpenFileName(self, "Select Ref Image", '',
                                                                 'image file(*png *jpeg *tiff *tif )')
        if self.file_name:
            self.ref_image = plt.imread(self.file_name[0])
            if self.ref_image.ndim == 3:
                self.ref_image = self.ref_image.sum(2)
            self.statusbar.showMessage(f'{self.file_name[0]} selected')
        else:
            self.statusbar.showMessage("No file has selected")
            pass

        try:
            self.ref_view.clear()
        except:
            pass

        # A plot area (ViewBox + axes) for displaying the image
        self.p1 = self.ref_view.addPlot(title="")

        # Item for displaying image data
        self.img = pg.ImageItem()
        hist = pg.HistogramLUTItem()
        hist.setImageItem(self.img)
        self.ref_view.addItem(hist)

        self.p1.addItem(self.img)
        self.ref_image = rotate(self.ref_image, -90)
        self.img.setImage(self.ref_image)
        self.img.setCompositionMode(QtGui.QPainter.CompositionMode_Plus)
        # self.img.translate(100, 50)
        # self.img.scale(0.5, 0.5)
        self.img.hoverEvent = self.imageHoverEvent
        self.img.mousePressEvent = self.MouseClickEvent

    def imageHoverEvent(self, event):
        """Show the position, pixel, and value under the mouse cursor.
        """
        if event.isExit():
            self.p1.setTitle("")
            return
        pos = event.pos()
        i, j = pos.x(), pos.y()
        i = int(np.clip(i, 0, self.ref_image.shape[0] - 1))
        j = int(np.clip(j, 0, self.ref_image.shape[1] - 1))
        val = self.ref_image[i, j]
        ppos = self.img.mapToParent(pos)
        x, y = np.around(ppos.x(), 2), np.around(ppos.y(), 2)
        self.p1.setTitle(f'pos: {x, y}  pixel: {i, j}  value: {val}')

    def MouseClickEvent(self, event):
        """Show the position, pixel, and value under the mouse cursor.
        """
        if event.button() == QtCore.Qt.LeftButton:

            pos = event.pos()
            i, j = pos.x(), pos.y()
            i = int(np.clip(i, 0, self.ref_image.shape[0] - 1))
            j = int(np.clip(j, 0, self.ref_image.shape[1] - 1))
            self.coords.append((i, j))
            val = self.ref_image[i, j]
            ppos = self.img.mapToParent(pos)
            # x, y = np.around(ppos.x(), 2) , np.around(ppos.y(), 2)
            x, y = smarx.position, smary.position
            self.coords.append((x, y))
            if len(self.coords) == 2:
                self.le_ref1_pxls.setText(f'{self.coords[0][0]}, {self.coords[0][1]}')
                self.dsb_ref1_x.setValue(self.coords[1][0])
                self.dsb_ref1_y.setValue(self.coords[1][1])
            elif len(self.coords) == 4:
                self.le_ref1_pxls.setText(f'{self.coords[0][0]}, {self.coords[0][1]}')
                self.dsb_ref1_x.setValue(self.coords[1][0])
                self.dsb_ref1_y.setValue(self.coords[1][1])
                self.le_ref2_pxls.setText(f'{self.coords[2][0]}, {self.coords[2][1]}')
                self.dsb_ref2_x.setValue(self.coords[-1][0])
                self.dsb_ref2_y.setValue(self.coords[-1][1])

    def createLabAxisImage(self):
        # A plot area (ViewBox + axes) for displaying the image

        try:
            self.labaxis_view.clear()
        except:
            pass

        self.p2 = self.labaxis_view.addPlot(title="")

        # Item for displaying image data
        self.img2 = pg.ImageItem()
        hist = pg.HistogramLUTItem()
        hist.setImageItem(self.img2)
        self.labaxis_view.addItem(hist)
        self.p2.addItem(self.img2)
        self.img2.setImage(self.ref_image)
        self.img2.setCompositionMode(QtGui.QPainter.CompositionMode_Plus)
        # self.img2.setImage(self.ref_image.T,opacity = 0.5)

    def getScalingParams(self):

        self.lm1_px, self.lm1_py = self.le_ref1_pxls.text().split(',')  # r chooses this pixel
        self.lm2_px, self.lm2_py = self.le_ref2_pxls.text().split(',')  # chooses this pixel

        # motor values from the microscope at pixel pos 1
        self.lm1_x, self.lm1_y = self.dsb_ref1_x.value(), self.dsb_ref1_y.value()
        # motor values from the microscope at pixel pos 2
        self.lm2_x, self.lm2_y = self.dsb_ref2_x.value(), self.dsb_ref2_y.value()

    def exportScalingParamFile(self):
        self.getScalingParams()
        self.scalingParam = {}
        ref_pos1 = {'px1': int(self.lm1_px), 'py1':int(self.lm1_py), 'cx1':self.lm1_x, 'cy1':self.lm1_y}
        ref_pos2 = {'px2': int(self.lm2_px), 'py2': int(self.lm2_py), 'cx2': self.lm2_x, 'cy2': self.lm2_y}
        self.scalingParam['lm1_vals'] = ref_pos1
        self.scalingParam['lm2_vals'] = ref_pos2

        file_name = QtWidgets.QFileDialog().getSaveFileName(self, "Save Parameter File", 'scaling_parameters.json',
                                                                 'json file(*json)')
        if file_name:

            with open(f'{file_name[0]}', 'w') as fp:
                json.dump(self.scalingParam,fp, indent=4)
        else:
            pass

    def importScalingParamFile(self):
        file_name = QtWidgets.QFileDialog().getOpenFileName(self, "Open Parameter File", '',
                                                                 'json file(*json)')
        if file_name:
            with open(file_name[0], 'r') as fp:
                self.scalingParam = json.load(fp)
        else:
            pass

        px1, py1 = self.scalingParam['lm1_vals']['px1'], self.scalingParam['lm1_vals']['py1']
        px2, py2 = self.scalingParam['lm2_vals']['px2'], self.scalingParam['lm2_vals']['py2']

        self.le_ref1_pxls.setText(f'{px1},{py1}')
        self.dsb_ref1_x.setValue(self.scalingParam['lm1_vals']['cx1'])
        self.dsb_ref1_y.setValue(self.scalingParam['lm1_vals']['cy1'])
        self.le_ref2_pxls.setText(f'{px2},{py2}')
        self.dsb_ref2_x.setValue(self.scalingParam['lm2_vals']['cx2'])
        self.dsb_ref2_y.setValue(self.scalingParam['lm2_vals']['cy2'])

    def scalingCalculation(self):
        self.getScalingParam()
        self.yshape, self.xshape = np.shape(self.ref_image)
        self.pixel_val_x = (self.lm2_x - self.lm1_x) / (int(self.lm2_px) - int(self.lm1_px))  # pixel value of X
        self.pixel_val_y = (self.lm2_y - self.lm1_y) / (int(self.lm2_py) - int(self.lm1_py))  # pixel value of Y; ususally same as X

        self.xi = self.lm1_x - (self.pixel_val_x * int(self.lm1_px))  # xmotor pos at origin (0,0)
        xf = self.xi + (self.pixel_val_x * self.xshape)  # xmotor pos at the end (0,0)
        self.yi = self.lm1_y - (self.pixel_val_y * int(self.lm1_py))  # xmotor pos at origin (0,0)
        yf = self.yi + (self.pixel_val_y * self.yshape)  # xmotor pos at origin (0,0)
        self.createLabAxisImage()

        self.label_scale_info.setText(f'Scaling: {self.pixel_val_x:.4f}, {self.pixel_val_y:.4f}, \n '
                                      f' X Range {self.xi:.2f}:{xf:.2f}, \n'
                                      f'Y Range {self.yi:.2f}:{yf:.2f}')
        self.img2.scale(abs(self.pixel_val_x), abs(self.pixel_val_y))
        self.img2.translate(self.xi, self.yi)
        # self.img2.setRect(QtCore.QRect(xi,yf,yi,xf))
        self.img2.hoverEvent = self.imageHoverEvent2
        self.img2.mousePressEvent = self.MouseClickEventToPos

    def imageHoverEvent2(self, event):
        """Show the position, pixel, and value under the mouse cursor.
        """
        if event.isExit():
            self.p2.setTitle("")
            return
        pos = event.pos()
        i, j = pos.x(), pos.y()
        i = int(np.clip(i, 0, self.ref_image.shape[0] - 1))
        j = int(np.clip(j, 0, self.ref_image.shape[1] - 1))
        val = self.ref_image[i, j]
        x = self.xi + (self.pixel_val_x * i)
        y = self.yi + (self.pixel_val_y * j)
        self.p2.setTitle(f'pos: {x:.2f},{y:.2f}  pixel: {i, j}  value: {val:.2f}')

    def MouseClickEventToPos(self, event):
        """Show the position, pixel, and value under the mouse cursor.
        """
        if event.button() == QtCore.Qt.LeftButton:
            pos = event.pos()
            i, j = pos.x(), pos.y()
            i = int(np.clip(i, 0, self.ref_image.shape[0] - 1))
            j = int(np.clip(j, 0, self.ref_image.shape[1] - 1))
            self.xWhere = self.xi + (self.pixel_val_x * i)
            self.yWhere = self.yi + (self.pixel_val_y * j)
            self.offsetCorrectedPos()

    def offsetCorrectedPos(self):
        self.dsb_calc_x.setValue(self.xWhere + (self.dsb_x_off.value() * 0.001))
        self.dsb_calc_y.setValue(self.yWhere + (self.dsb_y_off.value() * 0.001))

    def insertCurrentPos1(self):
        posX = smarx.position
        posY = smary.position

        self.dsb_ref1_x.setValue(posX)
        self.dsb_ref1_y.setValue(posY)

    def insertCurrentPos2(self):
        posX = smarx.position
        posY = smary.position

        self.dsb_ref2_x.setValue(posX)
        self.dsb_ref2_y.setValue(posY)

    def gotoTargetPos(self):
        targetX = self.dsb_calc_x.value()
        targetY = self.dsb_calc_y.value()
        RE(bps.mov(smarx, targetX))
        RE(bps.mov(smary, targetY))

    #exit gui

    def closeEvent(self,event):
        reply = QMessageBox.question(self, 'Quit GUI', "Are you sure you want to close the window?")
        if reply == QMessageBox.Yes:
            event.accept()
            self.scanStatus_thread.terminate()
            self.liveWorker.terminate()
            plt.close('all')
            #self.updateTimer.stop()
            QApplication.closeAllWindows()

        else:
            event.ignore()

    def close_application(self):

        choice = QMessageBox.question(self, 'Message',
                                      "Are you sure to quit?", QMessageBox.Yes |
                                      QMessageBox.No, QMessageBox.No)

        if choice == QMessageBox.Yes:
            plt.close('all')
            #stop the timers
            #self.updateTimer.stop()
            QApplication.closeAllWindows()

            print('quit application')
            sys.exit()
        else:
            pass


    def pumping_start_thread(self, turbo_start = 300, target_pressure = 1.2):
        
        QtTest.QTest.qWait(2000)
        self.lb_target_pressure.setText(f"  Target Pressure = {target_pressure}  ")
        QtTest.QTest.qWait(2000)
        self.lb_sample_change_action.setText("  Pumping  ")
        QtTest.QTest.qWait(2000)
        
        self.pump_thread = StartPumpThread(turbo_start,target_pressure)
        self.pump_thread.start()
        self.pbar_thread = PressureProgressBar(
            self.prb_sample_exchange,
            "XF:03IDC-VA{VT:Chm-CM:1}P-I",
            760,
            target_pressure
        )
        self.pbar_thread.start()

    def pumping_stop(self):
        
        HXNSampleExchanger.stop_pumping()
        self.pump_thread.terminate()
        self.pbar_thread.terminate()
        self.prb_sample_exchange.reset()

#from FXI--modified
class liveStatus(QThread):
    current_sts = pyqtSignal(int)
    def __init__(self, PV):
        super().__init__()
        self.PV = PV

    def run(self):

        while True:
            self.current_sts.emit(caget(self.PV))
            #print("New positions")
            QtTest.QTest.qWait(500)

class liveUpdate(QThread):
    
    current_positions = pyqtSignal(list)

    def __init__(self, pv_dict, update_interval_ms = 500):
        super().__init__()
        self.pv_dict = pv_dict
        self.update_interval_ms = update_interval_ms

    def return_values(self):
        readings = []
        for i in self.pv_dict.values():
            try:
                readings.append(i.position)
            except:
                readings.append(caget(i))

        return readings


    #use moveToThread method later
    def run(self):

        while True:
            positions = self.return_values()
            #self.pv_list = list(self.pv_dict.values())
            self.current_positions.emit(positions)
            #print(list(self.pv_dict.values())[0])
            #print(positions[0])
            QtTest.QTest.qWait(self.update_interval_ms)

class StartPumpThread(QThread):

    #TODO change to a move to thread method

    def __init__(self, turbo_pressure, target_pressure):
        super().__init__()
        self.turbo_pressure = turbo_pressure
        self.target_pressure = target_pressure


    def run(self):

        HXNSampleExchanger.start_pumping(
            turbo_start_pressure = self.turbo_pressure, 
            target_pressure = self.target_pressure
            )


class PressureProgressBar(QThread):
    
    def __init__(self, pbar, pv, min, max):
        super().__init__()
        self.min = min*-1
        self.max = max*-1
        self.pbar = pbar
        self.pv = pv

    def run(self):
        self.pbar.reset()
        self.pbar.setRange(int(self.min), int(self.max))
        
        while True:
            self.pbar.setValue(int(caget(self.pv))*-1)
            QtTest.QTest.qWait(200)




class WorkerSignals(QObject):
    started = QtCore.pyqtSignal(object)
    finished = QtCore.pyqtSignal(object) # create a signal
    result = QtCore.pyqtSignal(object) # create a signal that gets an object as argument

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn # Get the function passed in
        self.args = args # Get the arguments passed in
        self.kwargs = kwargs # Get the keyward arguments passed in
        self.signals = WorkerSignals()

    def run(self): # our thread's worker function
        result = self.fn(*self.args, **self.kwargs) # execute the passed in function with its arguments
        #self.signals.result.emit(result)  # return result
        self.signals.finished.emit(result)  # emit when thread ended






if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())


