import threading
import matplotlib.pyplot as plt
import pandas as pd
import math
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QApplication
import constants
import steamSensorFixture
import  os

#----------------------------------------------------------------- THREAD FUNCTION -------------------------------------------------------------------
class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.fn(*self.args, **self.kwargs)

#----------------------------------------------------------------- GUI FUNCTION -------------------------------------------------------------------
class myLineEdit(QtWidgets.QLineEdit):
    def check_state(self, *args, **kwargs):
        validator = self.validator()
        state = validator.validate(self.text(), 0)[0]
        if state == QtGui.QValidator.Acceptable:
            color = '#c4df9b' # green
        elif state == QtGui.QValidator.Intermediate:
            color = '#fff79a' # yellow
        else:
            color = '#f6989d' # red
        self.setStyleSheet('QLineEdit { background-color: %s }' % color)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.threadpool = QtCore.QThreadPool()
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(1000, 550)
        qr = MainWindow.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        MainWindow.move(qr.topLeft())
        
        #STATUS BAR
        self.status_bar = QtWidgets.QStatusBar(MainWindow)
        self.status_bar.setObjectName('status_bar')
        self.status_bar.setVisible(True)
        MainWindow.setStatusBar(self.status_bar)
        
        self.steam_Fixture_GUI = QtWidgets.QWidget(MainWindow)
        self.steam_Fixture_GUI.setObjectName("steam_Fixture_GUI")

        #LAYOUTS
        self.layoutWidget = QtWidgets.QWidget(self.steam_Fixture_GUI)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 310, 340))
        self.layoutWidget.setObjectName("layoutWidget")

        self.input_layout = QtWidgets.QGridLayout(self.layoutWidget)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setObjectName("input_layout")

        self.layoutWidget1 = QtWidgets.QWidget(self.steam_Fixture_GUI)
        self.layoutWidget1.setGeometry(QtCore.QRect(350, 488, 300, 32))
        self.layoutWidget1.setObjectName("layoutWidget1")

        self.button_layout = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setObjectName("button_layout")

        self.layoutWidget2 = QtWidgets.QWidget(self.steam_Fixture_GUI)
        self.layoutWidget2.setGeometry(QtCore.QRect(350, 20, 300, 160))
        self.layoutWidget2.setObjectName("layoutWidget2")

        self.output_layout = QtWidgets.QGridLayout(self.layoutWidget2)
        self.output_layout.setContentsMargins(0, 0, 0, 0)
        self.output_layout.setObjectName("output_layout")
        
        #VALIDATORS
        regexp = QtCore.QRegExp(r"[\w]+")
        self.alphanumeric_validator = QtGui.QRegExpValidator(regexp)
        regexp = QtCore.QRegExp(r"([1-9][0-9]*(\.[0-9]*[1-9])?|0\.[0-9]*[1-9])")
        self.double_validator = QtGui.QRegExpValidator(regexp)
        regexp = QtCore.QRegExp(r"[a-zA-Z]+")
        self.string_validator = QtGui.QRegExpValidator(regexp)

        #CREATE QLINEEDIT INPUTS
        self.create_input_labels()
        self.create_input_line_edits()

        #CREATE QLINEEDIT OUTPUTS
        self.create_output_labels()
        self.create_output_line_edits()
        
        #Timer
        self.setup_timer_label()
        self.setup_timer()

        #CREATE QLISTWIDGE SLOPE
        self.create_slope_list()
        self.format_initial_slope_list()

        #CREATE BUTTONS
        self.create_buttons()

        #CREATE GRAPH
        self.create_graph_pixmap()

        #VALIDATE QLINEEDIT INPUTS
        self.validate_input_line_edits()

        MainWindow.setCentralWidget(self.steam_Fixture_GUI)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        constants.START_PATH = os.getcwd()
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Steam Fixture GUI"))
        self.timer_label.setText(_translate("MainWindow", "TextLabel"))
        self.graph_label.setText(_translate("MainWindow", "TextLabel"))
        self.food_load_label.setText(_translate("MainWindow", "Food Load"))
        self.function_label.setText(_translate("MainWindow", "Function"))
        self.steam_appliance_label.setText(_translate("MainWindow", "Steam Appliance"))
        self.sensor_height_label.setText(_translate("MainWindow", "Sensor Height"))
        self.initial_water_mass_label.setText(_translate("MainWindow", "Initial Water Mass"))
        self.initial_food_mass_label.setText(_translate("MainWindow", "Initial Food Mass"))
        self.final_water_mass_label.setText(_translate("MainWindow", "Final Water Mass"))
        self.cook_time_label.setText(_translate("MainWindow", "Cook Time"))
        self.final_food_mass_label.setText(_translate("MainWindow", "Final Food Mass"))
        self.resume_button.setText(_translate("MainWindow", "Resume"))
        self.start_button.setText(_translate("MainWindow", "Start"))
        self.reset_button.setText(_translate("MainWindow", "Reset"))
        self.exit_button.setText(_translate("MainWindow", "Exit"))
        self.steam_accumulation_label.setText(_translate("MainWindow", "Steam Accumulation"))
        self.water_loss_label.setText(_translate("MainWindow", "Water Loss"))
        self.sensor_humidity_label.setText(_translate("MainWindow", "Sensors\' Humidity"))
        self.steam_temp_label.setText(_translate("MainWindow", "Steam Temperature"))
        self.graph_label.setText(_translate("MainWindow", ""))
        
#----------------------------------------------------------------- TIMER FUNCTIONS -------------------------------------------------------------------
    def setup_timer_label(self):
        self.count = 0
        self.flag = False
        self.timer_label = QtWidgets.QLabel(self.steam_Fixture_GUI)
        self.timer_label.setGeometry(QtCore.QRect(350, 408, 300, 60))
        self.timer_label.setObjectName("timer_label")
        self.timer_label.setText('00:00:00') 
        self.timer_label.setAlignment(QtCore.Qt.AlignCenter)
        self.timer_label.setStatusTip('Timer')
        
            
    def setup_timer(self):
        timer = QtCore.QTimer(self.steam_Fixture_GUI) 
        timer.timeout.connect(self.showTime) 
        timer.start(1000)
    
    def showTime(self):
        if self.flag: 
            self.count+= 1
        constants.MONITOR_TIME = self.count
        h = math.floor(self.count / 3600)
        m = math.floor((self.count % 3600) / 60)
        s = self.count % 3600 % 60
        text = '{0:02d}:{1:02d}:{2:02d}'.format(h,m,s)
        self.timer_label.setText(text)
        if constants.START_TIME !=0:
            self.timer_label.setStyleSheet("background-color: #c4df9b; border: 1px solid black;")
            self.status_bar.setStatusTip('Steam detected.Recording sensors\' data')
        else:
            self.timer_label.setStyleSheet("background-color: #fff79a; border: 1px solid black;")

#----------------------------------------------------------------- BUTTON FUNCTIONS -------------------------------------------------------------------
    def create_buttons(self):
        self.start_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.start_button.setObjectName("start_button")
        self.button_layout.addWidget(self.start_button)
        self.start_button.clicked.connect(self.start_function)
        self.start_button.setEnabled(False)
        self.start_button.setStatusTip('All fields must be green before sensors\' data can be recorded')

        self.exit_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.exit_button.setObjectName("exit_button")
        self.button_layout.addWidget(self.exit_button)
        self.exit_button.clicked.connect(self.quit_function)
        self.exit_button.setStatusTip('Exit')
        
        self.reset_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.reset_button.setObjectName("reset_button")
        self.button_layout.addWidget(self.reset_button)
        self.reset_button.clicked.connect(self.reset)
        self.reset_button.setStatusTip('Reset')

        self.resume_button = QtWidgets.QPushButton(self.layoutWidget)
        self.resume_button.setObjectName("resume_button")
        self.input_layout.addWidget(self.resume_button, 9, 1, 1, 1)
        self.resume_button.clicked.connect(self.resume_function)
        self.resume_button.setEnabled(False)
        self.resume_button.setStatusTip('Start recording sensors\' data first')

    def start_function(self):
        self.status_bar.setStatusTip('Steam has not been detected')
        self.start_button.setStatusTip('Stop recording sensors\' data')
        _translate = QtCore.QCoreApplication.translate
        self.start_button.clicked.disconnect(self.start_function)
        self.start_button.setText(_translate("MainWindow", "Stop"))
        self.start_button.clicked.connect(self.stop_function)
        
        self.steam_appliance_line.setEnabled(False)
        self.function_line.setEnabled(False)
        self.food_load_line.setEnabled(False)
        self.cook_time_line.setEnabled(False)
        self.sensor_height_line.setEnabled(False)
        self.initial_water_mass_line.setEnabled(False)
        self.initial_food_mass_line.setEnabled(False)

        constants.STEAM_APPLIANCE = self.steam_appliance_line.text().strip()
        constants.FUNCTION = self.function_line.text().strip()
        constants.FOOD_LOAD = self.food_load_line.text().strip()
        constants.COOK_TIME = float(self.cook_time_line.text().strip())
        constants.SENSOR_HEIGHT = float(self.sensor_height_line.text().strip())
        constants.INITIAL_WATER_MASS = float(self.initial_water_mass_line.text().strip())
        constants.INITIAL_FOOD_MASS = float(self.initial_food_mass_line.text().strip())
        
        self.flag = True

        record_worker = Worker(steamSensorFixture.record_data)
        self.threadpool.start(record_worker)
        
    def stop_function(self):
        _translate = QtCore.QCoreApplication.translate
        self.flag = False
        constants.STATE = False

        if self.dataframe_Empty_Check():
            self.dataframe_Empty_Popup()
        elif self.dataframe_Time_Interval_Check():
            self.dataframe_Time_Interval_Popup()
        elif not self.dataframe_Empty_Check() and not self.dataframe_Time_Interval_Check():
            self.final_Mass_Popup()
            self.resume_button.setEnabled(False)
            self.resume_button.setStatusTip('Calculate results')
            self.start_button.setEnabled(False)
                
            self.final_water_mass_line.setEnabled(True)
            self.final_water_mass_line.setValidator(self.double_validator)
            self.final_water_mass_line.textChanged.connect(self.final_water_mass_line.check_state)
            self.final_water_mass_line.textChanged.emit(self.final_water_mass_line.text())
            self.final_water_mass_line.textChanged.connect(self.enable_resume)
            self.final_water_mass_line.setStatusTip('Input final water mass')

            self.final_food_mass_line.setEnabled(True)
            self.final_food_mass_line.setValidator(self.double_validator)
            self.final_food_mass_line.textChanged.connect(self.final_food_mass_line.check_state)
            self.final_food_mass_line.textChanged.emit(self.final_food_mass_line.text())
            self.final_food_mass_line.textChanged.connect(self.enable_resume)
            self.final_food_mass_line.setStatusTip('Input final water mass')
    
    def resume_function(self):
        self.status_bar.setStatusTip('Calculating results')
        self.final_food_mass_line.setEnabled(False)
        self.final_water_mass_line.setEnabled(False)
        self.resume_button.setEnabled(False)
        
        steamSensorFixture.new_Dir()
        
        constants.FINAL_WATER_MASS = float(self.final_water_mass_line.text().strip())
        constants.FINAL_FOOD_MASS = float(self.final_food_mass_line.text().strip())
        constants.WATER_LOSS = (constants.INITIAL_FOOD_MASS + constants.INITIAL_WATER_MASS) - (constants.FINAL_FOOD_MASS + constants.FINAL_WATER_MASS)
        constants.STEAM_SENSOR_HUMIDITY = steamSensorFixture.average_Steam_Sensor_Humidity()
        constants.STEAM_TEMP = steamSensorFixture.average_steam_temperature()
        constants.STEAM_ACCUMULATION = steamSensorFixture.steam_Accumulation()
        
        output_worker = Worker(self.resume_function_helper)
        self.threadpool.start(output_worker)
        
    def resume_function_helper(self):
        derivative_time = steamSensorFixture.steam_Fixture_Graphs() 
        self.water_loss_line.setText('{0:,.2f}'.format(constants.WATER_LOSS))
        self.steam_accumulation_line.setText('{0:,.2f}'.format(constants.STEAM_ACCUMULATION))
        self.sensor_humidity_line.setText('{0:,.2f}'.format(constants.STEAM_SENSOR_HUMIDITY))
        self.steam_temp_line.setText('{0:,.2f}'.format(constants.STEAM_TEMP))
        derivative_df = self.format_final_slope_list(derivative_time)
        plt.savefig('Steam_Fixture_Graphs.png')
        steamSensorFixture.dataframe_to_Excel(derivative_df)
        self.graph_label.setPixmap(QtGui.QPixmap('Steam_Fixture_Graphs.png'))
        self.graph_label.setScaledContents(True)
        self.status_bar.setStatusTip('Done calculating results. Excel file has been exported')
        
    
    def quit_function(self):
        self.status_bar.setStatusTip('Quitting')
        sys.exit()

#----------------------------------------------------------------- INPUT LABEL FUNCTIONS -------------------------------------------------------------------
    def create_input_labels(self):
        self.steam_appliance_label = QtWidgets.QLabel(self.layoutWidget)
        self.steam_appliance_label.setObjectName("steam_appliance_label")
        self.input_layout.addWidget(self.steam_appliance_label, 0, 0, 1, 1)

        self.food_load_label = QtWidgets.QLabel(self.layoutWidget)
        self.food_load_label.setObjectName("food_load_label")
        self.input_layout.addWidget(self.food_load_label, 2, 0, 1, 1)

        self.function_label = QtWidgets.QLabel(self.layoutWidget)
        self.function_label.setObjectName("function_label")
        self.input_layout.addWidget(self.function_label, 1, 0, 1, 1)

        self.sensor_height_label = QtWidgets.QLabel(self.layoutWidget)
        self.sensor_height_label.setObjectName("sensor_height_label")
        self.input_layout.addWidget(self.sensor_height_label, 4, 0, 1, 1)

        self.initial_water_mass_label = QtWidgets.QLabel(self.layoutWidget)
        self.initial_water_mass_label.setObjectName("initial_water_mass_label")
        self.input_layout.addWidget(self.initial_water_mass_label, 5, 0, 1, 1)

        self.initial_food_mass_label = QtWidgets.QLabel(self.layoutWidget)
        self.initial_food_mass_label.setObjectName("initial_food_mass_label")
        self.input_layout.addWidget(self.initial_food_mass_label, 6, 0, 1, 1)

        self.final_water_mass_label = QtWidgets.QLabel(self.layoutWidget)
        self.final_water_mass_label.setObjectName("final_water_mass_label")
        self.input_layout.addWidget(self.final_water_mass_label, 7, 0, 1, 1)

        self.cook_time_label = QtWidgets.QLabel(self.layoutWidget)
        self.cook_time_label.setObjectName("cook_time_label")
        self.input_layout.addWidget(self.cook_time_label, 3, 0, 1, 1)

        self.final_food_mass_label = QtWidgets.QLabel(self.layoutWidget)
        self.final_food_mass_label.setObjectName("final_food_mass_label")
        self.input_layout.addWidget(self.final_food_mass_label, 8, 0, 1, 1)

#----------------------------------------------------------------- INPUT FUNCTIONS -------------------------------------------------------------------
    def create_input_line_edits(self):
        self.steam_appliance_line = myLineEdit(self.layoutWidget)
        self.steam_appliance_line.setObjectName("steam_appliance_line")
        self.input_layout.addWidget(self.steam_appliance_line, 0, 1, 1, 1)
        self.steam_appliance_line.setStatusTip('Input steam appliance')

        self.function_line = myLineEdit(self.layoutWidget)
        self.function_line.setObjectName("function_line")
        self.input_layout.addWidget(self.function_line, 1, 1, 1, 1)
        self.function_line.setStatusTip('Input function')
        
        self.sensor_height_line = myLineEdit(self.layoutWidget)
        self.sensor_height_line.setObjectName("sensor_height_line")
        self.input_layout.addWidget(self.sensor_height_line, 4, 1, 1, 1)
        self.sensor_height_line.setStatusTip('Input sensor height')

        self.final_water_mass_line = myLineEdit(self.layoutWidget)
        self.final_water_mass_line.setObjectName("final_water_mass_line")
        self.input_layout.addWidget(self.final_water_mass_line, 7, 1, 1, 1)
        self.final_water_mass_line.setStatusTip('Final water mass can not be inputted until the end of the run')
        self.final_water_mass_line.setEnabled(False)

        self.initial_food_mass_line = myLineEdit(self.layoutWidget)
        self.initial_food_mass_line.setObjectName("initial_food_mass_line")
        self.input_layout.addWidget(self.initial_food_mass_line, 6, 1, 1, 1)
        self.initial_food_mass_line.setStatusTip('Input initial food mass')

        self.cook_time_line = myLineEdit(self.layoutWidget)
        self.cook_time_line.setObjectName("cook_time_line")
        self.input_layout.addWidget(self.cook_time_line, 3, 1, 1, 1)
        self.cook_time_line.setStatusTip('Input cook time')

        self.food_load_line = myLineEdit(self.layoutWidget)
        self.food_load_line.setObjectName("food_load_line")
        self.input_layout.addWidget(self.food_load_line, 2, 1, 1, 1)
        self.food_load_line.setStatusTip('Input food load')

        self.initial_water_mass_line = myLineEdit(self.layoutWidget)
        self.initial_water_mass_line.setObjectName("initial_water_mass_line")
        self.input_layout.addWidget(self.initial_water_mass_line, 5, 1, 1, 1)
        self.initial_water_mass_line.setStatusTip('Input initial water mass')

        self.final_food_mass_line = myLineEdit(self.layoutWidget)
        self.final_food_mass_line.setObjectName("final_food_mass_line")
        self.input_layout.addWidget(self.final_food_mass_line, 8, 1, 1, 1)
        self.final_food_mass_line.setStatusTip('Final food mass can not be inputted until the end of the run')
        self.final_food_mass_line.setEnabled(False)

    def validate_input_line_edits(self):
        input_list = [self.steam_appliance_line, self.function_line, self.food_load_line, self.cook_time_line, self.sensor_height_line, self.initial_water_mass_line, self.initial_food_mass_line]

        #Connect validator to line edits
        self.steam_appliance_line.setValidator(self.alphanumeric_validator)
        self.function_line.setValidator(self.string_validator)
        self.food_load_line.setValidator(self.string_validator)
        self.cook_time_line.setValidator(self.double_validator)
        self.sensor_height_line.setValidator(self.double_validator)
        self.initial_water_mass_line.setValidator(self.double_validator)
        self.initial_food_mass_line.setValidator(self.double_validator)

        #Connect line edits to function
        for i in input_list:
            i.textChanged.connect(i.check_state)
            i.textChanged.emit(i.text())
            i.textChanged.connect(self.enable_start)
    
    def enable_start(self):
        qLineEdit_list = [self.steam_appliance_line, self.function_line, self.food_load_line, self.cook_time_line, self.sensor_height_line, self.initial_water_mass_line,self.initial_food_mass_line]
        inputs_valid = True
        for q in qLineEdit_list:
            if q.validator().validate(q.text(), 0)[0] == QtGui.QValidator.Intermediate:
                inputs_valid = False
        if inputs_valid:
            if steamSensorFixture.check_Sensors():
                self.start_button.setEnabled(True)
            else:
                self.sensor_Wet_Popup()
        else:
            self.start_button.setEnabled(False)
    
    def enable_resume(self):
        if (self.final_water_mass_line.validator().validate(self.final_water_mass_line.text(), 0)[0] == QtGui.QValidator.Intermediate) | (self.final_food_mass_line.validator().validate(self.final_food_mass_line.text(), 0)[0] == QtGui.QValidator.Intermediate):
            self.resume_button.setEnabled(False)
        else:
            self.resume_button.setEnabled(True)

#----------------------------------------------------------------- OUTPUT LABEL FUNCTIONS -------------------------------------------------------------------
    def create_output_labels(self):
        self.steam_accumulation_label = QtWidgets.QLabel(self.layoutWidget2)
        self.steam_accumulation_label.setObjectName("steam_accumulation_label")
        self.output_layout.addWidget(self.steam_accumulation_label, 0, 0, 1, 1)

        self.water_loss_label = QtWidgets.QLabel(self.layoutWidget2)
        self.water_loss_label.setObjectName("water_loss_label")
        self.output_layout.addWidget(self.water_loss_label, 3, 0, 1, 1)

        self.sensor_humidity_label = QtWidgets.QLabel(self.layoutWidget2)
        self.sensor_humidity_label.setObjectName("sensor_humidity_label")
        self.output_layout.addWidget(self.sensor_humidity_label, 1, 0, 1, 1)

        self.steam_temp_label = QtWidgets.QLabel(self.layoutWidget2)
        self.steam_temp_label.setObjectName("steam_temp_label")
        self.output_layout.addWidget(self.steam_temp_label, 2, 0, 1, 1)
        

#----------------------------------------------------------------- OUTPUT FUNCTIONS -------------------------------------------------------------------
    def create_output_line_edits(self):
        self.steam_accumulation_line = myLineEdit(self.layoutWidget2)
        self.steam_accumulation_line.setObjectName("steam_accumulation_line")
        self.output_layout.addWidget(self.steam_accumulation_line, 0, 1, 1, 1)
        self.steam_accumulation_line.setStatusTip('Steam Accumation')
        self.steam_accumulation_line.setEnabled(False)

        self.sensor_humidity_line = myLineEdit(self.layoutWidget2)
        self.sensor_humidity_line.setObjectName("sensor_humidity_line")
        self.output_layout.addWidget(self.sensor_humidity_line, 1, 1, 1, 1)
        self.sensor_humidity_line.setStatusTip('Average steam sensors\' humidity')
        self.sensor_humidity_line.setEnabled(False)

        self.steam_temp_line = myLineEdit(self.layoutWidget2)
        self.steam_temp_line.setObjectName("steam_temp_line")
        self.output_layout.addWidget(self.steam_temp_line, 2, 1, 1, 1)
        self.steam_temp_line.setStatusTip('Average steam temperature')
        self.steam_temp_line.setEnabled(False)

        self.water_loss_line = myLineEdit(self.layoutWidget2)
        self.water_loss_line.setObjectName("water_loss_line")
        self.output_layout.addWidget(self.water_loss_line, 3, 1, 1, 1)
        self.water_loss_line.setStatusTip('Water Loss')
        self.water_loss_line.setEnabled(False)
    
    def create_slope_list(self):
        self.slope_list = QtWidgets.QListWidget(self.steam_Fixture_GUI)
        self.slope_list.setGeometry(QtCore.QRect(350, 200, 300, 160))
        self.slope_list.setObjectName("slope_list")

        item = QtWidgets.QListWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        counter = 0
        while counter < 11:
            self.slope_list.addItem(item)
            item = QtWidgets.QListWidgetItem()
            counter +=1
    
    def format_initial_slope_list(self):
        _translate = QtCore.QCoreApplication.translate
        __sortingEnabled = self.slope_list.isSortingEnabled()
        self.slope_list.setStatusTip('Slope - Time')
        self.slope_list.setSortingEnabled(False)
        item = self.slope_list.item(0)
        item.setText(_translate("MainWindow", "Slope (Count) - Time (min):"))
        counter = 1
        while counter < 11:
            item = self.slope_list.item(counter)
            row = str(counter) + '. '
            item.setText(_translate("MainWindow", row))
            counter += 1
        self.slope_list.setSortingEnabled(__sortingEnabled)
    
    def format_final_slope_list(self,d):
        _translate = QtCore.QCoreApplication.translate
        sorted_derivative = sorted(d, reverse=True)
        dict_len = len(sorted_derivative)
        derivative_df_structure = {'Derivative (Count * min)':[], 'Time (min)':[]}
        derivative_df = pd.DataFrame(derivative_df_structure)
        counter = 1

        if  dict_len > 10:
            dict_len = 10
        for derivative in sorted_derivative[:dict_len]:
            if not math.isnan(derivative):
                derivative_df_new_row = {'Derivative (Count * min)':derivative, 'Time (min)':d[derivative]}
                derivative_df = derivative_df.append(derivative_df_new_row, ignore_index = True)
                item = self.slope_list.item(counter)
                item.setText(_translate("MainWindow", ' {0}. {1:.2f} @ {2:.2f}'.format(counter, derivative, d[derivative])))
                counter +=1
        return derivative_df

    def create_graph_pixmap(self):
        
        self.graph_label = QtWidgets.QLabel(self.steam_Fixture_GUI)
        self.graph_label.setGeometry(QtCore.QRect(670, 20, 310, 340))
        self.graph_label.setObjectName("graph_label")
        self.graph_label.setStyleSheet("border : 1px solid black;")
        self.graph_label.setStatusTip('Graphs')
        

#----------------------------------------------------------------- POPUP FUNCTIONS -------------------------------------------------------------------
    def dataframe_Empty_Check(self):
        return constants.df.empty
    
    def calculate_monitor_time(self):
        return (constants.df.iloc[-1]['Time (min)'] - constants.df.iloc[0]['Time (min)'])
    
    def dataframe_Time_Interval_Check(self):
        return self.calculate_monitor_time() < .5

    def final_Mass_Popup(self):
        self.status_bar.setStatusTip('Input final masses')
        msg = QMessageBox()
        msg.setText("Enter Food and Water Final Masses (g)")
        msg.setIcon(QMessageBox.Information)
        msg.exec()
    
    def sensor_Wet_Popup(self):
        self.status_bar.setStatusTip('Error!')
        msg = QMessageBox()
        msg.setText('Error! Steam sensors are not dry')
        msg.setIcon(QMessageBox.Critical)
        msg.exec()
        
    def dataframe_Empty_Popup(self):
        self.status_bar.setStatusTip('Error!')
        msg = QMessageBox()
        msg.setText("Error! No data recorded! Theshold maybe too high.")
        msg.setIcon(QMessageBox.Critical)            
        msg.exec()
        self.disable_all()
                
    def dataframe_Time_Interval_Popup(self):
        self.status_bar.setStatusTip('Error!')
        msg = QMessageBox()
        msg.setText("Error! Please increase monitor time on next run.")
        msg.setIcon(QMessageBox.Critical)
        msg.exec()
        self.disable_all()
        print(constants.df)
            
#----------------------------------------------------------------- RESET FUNCTIONS -------------------------------------------------------------------
    def reset_Line_Edits(self):
        self.food_load_line.setText('')
        self.function_line.setText('')
        self.steam_appliance_line.setText('')
        self.cook_time_line.setText('')
        self.sensor_height_line.setText('')
        self.initial_food_mass_line.setText('')
        self.initial_water_mass_line.setText('')
        self.final_food_mass_line.setText('')
        self.final_water_mass_line.setText('')

        self.water_loss_line.setText('')
        self.steam_accumulation_line.setText('')
        self.sensor_humidity_line.setText('')
        self.steam_temp_line.setText('')
        
        color = '#fdfefe'
        self.final_food_mass_line.setStyleSheet('QLineEdit { background-color: %s }' % color)
        self.final_water_mass_line.setStyleSheet('QLineEdit { background-color: %s }' % color)
        
        self.steam_appliance_line.setEnabled(True)
        self.function_line.setEnabled(True)
        self.food_load_line.setEnabled(True)
        self.cook_time_line.setEnabled(True)
        self.sensor_height_line.setEnabled(True)
        self.initial_water_mass_line.setEnabled(True)
        self.initial_food_mass_line.setEnabled(True)
        

        self.water_loss_line.setEnabled(False)
        self.steam_accumulation_line.setEnabled(False)
        self.sensor_humidity_line.setEnabled(False)
        self.steam_temp_line.setEnabled(False)
        
        self.final_water_mass_line.setStatusTip('Final water mass can not be inputted until the end of the run')
        self.final_food_mass_line.setStatusTip('Final food mass can not be inputted until the end of the run')
        
    def reset_buttons(self):
        _translate = QtCore.QCoreApplication.translate
        self.resume_button.setEnabled(False)
        self.start_button.setEnabled(False)
        
        self.start_button.setStatusTip('All fields must be green before sensors\' data can be recorded')
        self.resume_button.setStatusTip('Start recording sensors\' data first')
        
        if self.start_button.text() == 'Stop':
            self.start_button.clicked.disconnect(self.stop_function)
            self.start_button.setText(_translate("MainWindow", "Start"))
            self.start_button.clicked.connect(self.start_function)
        
    def reset(self):
        self.status_bar.setStatusTip('Inputs and outputs have been reset')
        constants.STATE = False
        constants.START_TIME = 0
        constants.MONITOR_TIME = 0
        self.flag = False
        steamSensorFixture.reset_Dir()
        self.reset_Line_Edits()
        self.reset_buttons()
        self.count = 0
        self.format_initial_slope_list()
        self.graph_label.clear()
        

#----------------------------------------------------------------- DISABLE FUNCTIONS -------------------------------------------------------------------
    def disable_all(self):
        self.disable_buttons()
        self.disable_line_edits()
        
    def disable_line_edits(self):
        self.steam_appliance_line.setEnabled(False)
        self.function_line.setEnabled(False)
        self.food_load_line.setEnabled(False)
        self.cook_time_line.setEnabled(False)
        self.sensor_humidity_line.setEnabled(False)
        self.sensor_height_line.setEnabled(False)
        self.initial_food_mass_line.setEnabled(False)
        self.initial_water_mass_line.setEnabled(False)
    
    def disable_buttons(self):
        self.start_button.setEnabled(False)

#----------------------------------------------------------------- MAIN FUNCTIONS -------------------------------------------------------------------
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())