# -*- coding: utf-8 -*-

#Author: Ajith Pattammattel
#Data:06-23-2020

import sys, os, signal, subprocess
import numpy as np

from pdf_log import *
from xanes2d import*
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QMessageBox, QFileDialog


 

class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('hxn_gui_admin.ui', self)
                
        self.pb_exit.clicked.connect(self.close_application)
        self.dwell.valueChanged.connect(self.calc_res) # updating resolution/tot time
        self.x_step.valueChanged.connect(self.calc_res)#
        self.y_step.valueChanged.connect(self.calc_res)#
        self.x_start.valueChanged.connect(self.calc_res)#
        self.y_start.valueChanged.connect(self.calc_res)#
        self.x_end.valueChanged.connect(self.calc_res)#
        self.y_end.valueChanged.connect(self.calc_res)#
        
        self.pb_save_cmd.clicked.connect(self.save_file)
        self.pb_clear_cmd.clicked.connect(self.clear_cmd)
        self.pb_new_macro_gedit.clicked.connect(self.open_gedit)
        self.pb_new_macro_vi.clicked.connect(self.open_vi)
        self.pb_new_macro_emacs.clicked.connect(self.open_emacs)
        self.pb_browse_a_macro.clicked.connect(self.get_a_file)
        self.pb_ex_macro_open.clicked.connect(self.open_a_macro)
        self.pb_close_all_plot.clicked.connect(self.close_all_plots)
        self.pb_close_plot.clicked.connect(self.close_plot)
        self.start.clicked.connect(self.start_flyscan)
        self.pb_plot.clicked.connect(self.plot_me)
        #self.pushButton_2.clicked.connect(self.abort_scan)
        self.pb_gen_elist.clicked.connect(self.generate_elist)
        self.pb_start_xanes.clicked.connect(self.zp_xanes)

        self.pb_move_smarx.clicked.connect(self.move_smarx())
        self.pb_move_smary.clicked.connect(self.move_smary())
        self.pb_move_smarz.clicked.connect(self.move_smarz())
        self.pb_move_dth.clicked.connect(self.move_dsth())

        '''
        self.pb_folder_log.clicked.connect(self.select_pdf_wd)
        self.pb_pdf_image.clicked.connect(self.select_pdf_image)
        self.pb_date_ok.clicked.connect(self.generate_pdf)
        self.pb_save_pdf.clicked.connect(self.force_save_pdf)
        self.pb_createpdf.clicked.connect(self.insert_pdf)
        '''
        self.show()

    def start_flyscan(self):
    
        motor1 = self.cb_motor1.currentText()
        motor2 = self.cb_motor2.currentText()
        det = self.pb_dets.currentText()
        
        mot1_s = self.x_start.value()
        mot1_e = self.x_end.value()
        mot1_steps = self.x_step.value() 
        mot2_s = self.y_start.value()
        mot2_e = self.y_end.value()
        mot2_steps = self.y_step.value()
        dwell_t = self.dwell.value()

        cal_res_x = (abs(mot1_s)+abs(mot1_e))/mot1_steps
        cal_res_y = (abs(mot2_s)+abs(mot2_e))/mot2_steps
        
        motor_list = {'zpssx':zpssx,'zpssy':zpssy,'zpssz':zpssz}
        det_list = {'dets1': dets1, 'dets2': dets2, 'dets3': dets3,
                    'dets4': dets4, 'dets5': dets5, 'dets6': dets6,
                    'dets7': dets7, 'dets8': dets8,'dets_fs': dets_fs}
 

        if self.rb_1d.isChecked(): #TODO disable the other motor when 1d is checked 
            
            RE(fly1d(det_list[det], motor_list[motor1], mot1_s,mot1_e ,mot1_steps, dwell_t))
        
        elif self.rb_2d.isChecked():
           
            RE(fly2d(det_list[det], motor_list[motor1], mot1_s,mot1_e ,mot1_steps, motor_list[motor2], mot2_s,mot2_e, mot2_steps, dwell_t))

    def move_smarx(self):
        move_by = self.db_move_smarx.value()
        RE(bps.movr(smarx, move_by * 0.001))

    def move_smary(self):
        move_by = self.db_move_smary.value()
        RE(bps.movr(smary, move_by * 0.001))

    def move_smarz(self):
        move_by = self.db_move_smarz.value()
        RE(bps.movr(smarz, move_by * 0.001))

    def move_dsth(self):
        move_by = self.db_move_dth.value()
        RE(bps.movr(zpsth, move_by))
        
    def merlinIN(self):
        RE(go_det('merlin')      
        
    def merlinOUT(self):
        RE(bps.mov(diff.x,-400)
                
    def vortexIN(self):
        RE(bps.mov(fdet1.x,-8)
        
    def vortexOUT(self):
        RE(bps.mov(fdet1.x,-107)
        
    def cam11IN(self):
        RE(go_det('cam11')
        
        
    def fill_common_scan_params(self):
        common_scans = {

                        self.scan1: [-15, 15, -15,15, 30,30, 0.03],

                        self.scan2: [-1, 1, -1,1, 100,100, 0.03],

                        self.scan3: [-3, 3, -3,3, 100,100, 0.05],

                        self.scan4: [-10, 10, -10,10, 100,100, 0.03]

                        }
        param_to_fill = [self.x_start, self.x_end, self.y_start, self.y_end, self.x_step, self.y_step, self.dwell]

        for val, mot in zip(common_scans[self.fill_rb_checked()], param_to_fill):
            print(mot, val)

        pass

    def fill_rb_checked(self):
        "return the name of the rb checked by the user"
        pass

    def calc_res(self):
        mot1_s = self.x_start.value()
        mot1_e = self.x_end.value()
        mot1_steps = self.x_step.value()

        mot2_s = self.y_start.value()
        mot2_e = self.y_end.value()
        mot2_steps = self.y_step.value()

        dwell_t = self.dwell.value()

        cal_res_x = (abs(mot1_s) + abs(mot1_e)) / mot1_steps
        cal_res_y = (abs(mot2_s) + abs(mot2_e)) / mot2_steps
        tot_t = str(np.around(mot1_steps * mot2_steps * dwell_t / 60, 2))
        self.label_scan_info_calc.setText(f'X: {(cal_res_x * 1000):.2f}, Y: {(cal_res_y * 1000).:2f} \n'
                                          f'{tot_t} + overhead')

        self.label_scanMacro.setText(f'fly2d(dets1, {mot1_s}, {mot1_e}, {mot1_steps}, '
                                     f'{mot2_s},{mot2_e},{mot2_steps},{dwell_t})')

    def plot_me(self):

        sd = self.lineEdit_5.text()
        elem = self.lineEdit_6.text()
        if self.ch_b_norm.isChecked():
            plot_data(int(sd), elem, 'sclr1_ch4')
        else:
            plot_data(sd, elem)


        
    def close_application(self):

        choice = QMessageBox.question(self, 'Message',
                                     "Are you sure to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)

        if choice == QMessageBox.Yes:
            print('quit application')
            sys.exit()
        else:
            pass
            
    def save_file(self):
      S__File = QFileDialog.getSaveFileName(None,'SaveFile','/', "Python Files (*.py)")
    
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
        
    def close_all_plots(self):
        return plt.close('all')
        
    def close_plot(self):
        return plt.close()
        
    def abort_scan(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        RE.abort()
        
        
        
    def select_pdf_wd(self):
        folder_path = QFileDialog().getExistingDirectory(self, "Select Folder")
        self.le_folder_log.setText(str(folder_path))
        
    def select_pdf_image(self):
        file_name = QFileDialog().getOpenFileName(self, "Select an Image")
        self.le_elog_image.setText(str(file_name[0]))
        
    
    def generate_pdf(self):
        dt = self.dateEdit_elog.date()
        tmp_date = dt.toString(self.dateEdit_elog.displayFormat())
        tmp_file = os.path.join(self.le_folder_log.text(),self.le_elog_name.text())
        tmp_sample = self.le_elog_sample.text()
        tmp_experimenter = self.le_elog_experimenters.text()
        tmp_pic = self.le_elog_image.text()
        
        return setup_pdf_for_gui(tmp_file, tmp_date, tmp_sample, tmp_experimenter, tmp_pic)
        
    def insert_pdf(self):
        return insertTitle_for_gui()
        
    def force_save_pdf(self):
        return save_page_for_gui()
        
        



    def generate_elist(self):

        pre = np.linspace(self.dsb_pre_s.value(), self.dsb_pre_e.value(), self.sb_pre_p.value())
        XANES1 = np.linspace(self.dsb_ed1_s.value(), self.dsb_ed1_e.value(), self.sb_ed1_p.value())
        XANES2 = np.linspace(self.dsb_ed2_s.value(), self.dsb_ed2_e.value(), self.sb_ed2_p.value())
        post = np.linspace(self.dsb_post_s.value(), self.dsb_post_e.value(), self.sb_post_p.value())

        energies = np.concatenate([pre, XANES1, XANES2, post])
        
        #print(energies)
        dE = (self.dsb_monoe_h.value() - self.dsb_monoe_l.value())

        ugap_slope = (self.dsb_ugap_h.value() - self.dsb_ugap_l.value()) / dE
        ugap_list = self.dsb_ugap_h.value() + (energies - self.dsb_monoe_h.value()) * ugap_slope

        crl_slope = (self.dsb_crl_h.value() - self.dsb_crl_l.value()) / dE
        crl_list = self.dsb_crl_h.value() + (energies - self.dsb_monoe_h.value()) * crl_slope

        zpz_slope = (self.dsb_zpz_h.value() - self.dsb_zpz_l.value()) / dE
        zpz_list = self.dsb_zpz_h.value() + (energies - self.dsb_monoe_h.value()) * zpz_slope

        e_list = np.column_stack((energies, ugap_list, zpz_list, crl_list))

        return e_list

    def zp_xanes(self):
    
        e_list = self.generate_elist()
        
        motor1 = self.cb_motor1.currentText()
        motor2 = self.cb_motor2.currentText()
        det = self.Dets_3.currentText()
        
        mot1_s = self.x_start.value()
        mot1_e = self.x_end.value()
        mot1_steps = self.x_step.value() 
        mot2_s = self.y_start.value()
        mot2_e = self.y_end.value()
        mot2_steps = self.y_step.value()
        dwell_t = self.dwell.value()
        
        RE(zp_list_xanes2d(e_list,det_list[det], motor_list[motor1], mot1_s,mot1_e ,mot1_steps, 
                        motor_list[motor2], mot2_s,mot2_e, mot2_steps, dwell_t))
        

if __name__ == "__main__":
    
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())


