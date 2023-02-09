import os
import sys
import collections
import json
import datetime


from PyQt5 import QtWidgets, uic, QtCore, QtGui, QtTest
from PyQt5.QtWidgets import QMessageBox, QFileDialog


class ListWidget(QtWidgets.QMainWindow):
    def __init__(self):
        super(ListWidget, self).__init__()
        uic.loadUi('listWidgetTest.ui', self)
        self.roiDict = {}
        self.pb_save_pos.clicked.connect(self.generatePositionDict)
        self.pb_roiList_import.clicked.connect(self.importROIDict)
        self.pb_roiList_export.clicked.connect(self.exportROIDict)
        self.pb_roiList_clear.clicked.connect(self.clearROIList)
        self.sampleROI_List.itemClicked.connect(self.showROIPos)
        #self.sampleROI_List.itemClicked.connect(lambda: print(
            #(self.roiDict[self.sampleROI_List.currentItem().text()])))
        self.show()

    def getTime(self):
        return datetime.datetime.now()

    def generatePositionDict(self):
        #roi = {'now': self.getTime()}
        roi = str(self.sampleROI_List.count())
        roi_name = 'ROI' + str(self.sampleROI_List.count())
        self.roiDict[roi_name] = roi
        self.sampleROI_List.addItem(roi_name)
        item = self.sampleROI_List.item(self.sampleROI_List.count()-1)
        item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)


    def applyDictWithLabel(self):
        label_ = {}
        for idx in range(self.sampleROI_List.count()):
            label = self.sampleROI_List.item(idx).text()
            label_[label] = idx
        self.roiDict['user_labels'] = label_
        print(self.roiDict)

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
        print(self.roiDict[f'ROI{item_num}'])


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = ListWidget()
    window.show()
    sys.exit(app.exec_())
