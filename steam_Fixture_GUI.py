import threading
import matplotlib.pyplot as plt
import pandas as pd
import math
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QApplication
import constants
import steamSensorFixture

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
        MainWindow.setFixedSize(900,550)
        qr = MainWindow.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        MainWindow.move(qr.topLeft())
        
        self.status_bar = QtWidgets.QStatusBar(MainWindow)
        self.status_bar.setObjectName('status_bar')
        self.status_bar.setVisible(True)
        MainWindow.setStatusBar(self.status_bar)
        
        self.steam_Fixture_GUI = QtWidgets.QWidget(MainWindow)
        self.steam_Fixture_GUI.setObjectName("steam_Fixture_GUI")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.steam_Fixture_GUI)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 20, 201, 401))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.inputs = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.inputs.setContentsMargins(0, 0, 0, 0)
        self.inputs.setObjectName("inputs")
        
        #VALIDATORS
        regexp = QtCore.QRegExp(r"[\w]+")
        self.alphanumeric_validator = QtGui.QRegExpValidator(regexp)
        regexp = QtCore.QRegExp(r"([1-9][0-9]*(\.[0-9]*[1-9])?|0\.[0-9]*[1-9])")
        self.double_validator = QtGui.QRegExpValidator(regexp)
        regexp = QtCore.QRegExp(r"[a-zA-Z]+")
        self.string_validator = QtGui.QRegExpValidator(regexp)

        #CREATE QLINEEDIT INPUTS
        self.create_input_line_edits()

        #CREATE QLINEEDIT OUTPUTS
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

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Steam Fixture GUI"))
        self.steam_appliance.setPlaceholderText(_translate("MainWindow", "Steam Appliance:"))
        self.function.setPlaceholderText(_translate("MainWindow", "Function:"))
        self.food_load.setPlaceholderText(_translate("MainWindow", "Food Load:"))
        self.cook_time.setPlaceholderText(_translate("MainWindow", "Cook Time (min):"))
        self.sensor_height.setPlaceholderText(_translate("MainWindow", "Sensor Height (in):"))
        self.initial_water_mass.setPlaceholderText(_translate("MainWindow", "Initial Water Mass (g):"))
        self.initial_food_mass.setPlaceholderText(_translate("MainWindow", "Initial Food Mass (g):"))
        self.final_water_mass.setPlaceholderText(_translate("MainWindow", "Final Water Mass (g):"))
        self.final_food_mass.setPlaceholderText(_translate("MainWindow", "Final Food Mass (g):"))

        self.steam_accumulation.setPlaceholderText(_translate("MainWindow", "Steam Accumulation (Count * min): "))
        self.steam_sensor_humidity.setPlaceholderText(_translate("MainWindow", "Steam Sensors\' Average Humidity (%): "))
        self.steam_temp.setPlaceholderText(_translate("MainWindow", "Average Steam Temperature (C): "))
        self.water_loss.setPlaceholderText(_translate("MainWindow", "Water Loss (g):"))

        self.start_button.setText(_translate("MainWindow", "Start"))
        self.quit_button.setText(_translate("MainWindow", "Quit"))
        self.resume_button.setText(_translate("MainWindow", "Resume"))
        self.new_run_button.setText(_translate("MainWindow", "New Run"))

        self.graphs.setText(_translate("MainWindow", "Graphs"))
        
#----------------------------------------------------------------- TIMER FUNCTIONS -------------------------------------------------------------------
    def setup_timer_label(self):
        self.count = 0
        self.flag = False
        self.timer_label = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        self.timer_label.setStyleSheet("border : 1px solid black;")
        self.timer_label.setText('00:00:00') 
        self.timer_label.setAlignment(QtCore.Qt.AlignCenter)
        self.timer_label.setStatusTip('Stopwatch')
        self.outputs.addWidget(self.timer_label)
            
    def setup_timer(self):
        timer = QtCore.QTimer(self.steam_Fixture_GUI) 
        timer.timeout.connect(self.showTime) 
        timer.start(1000)
    
    def showTime(self):
        if self.flag: 
            self.count+= 1
        constants.TIME = self.count
        h = math.floor(self.count / 3600)
        m = math.floor((self.count % 3600) / 60)
        s = self.count % 3600 % 60
        text = '{0:02d}:{1:02d}:{2:02d}'.format(h,m,s)
        self.timer_label.setText(text)

#----------------------------------------------------------------- BUTTON FUNCTIONS -------------------------------------------------------------------
    def create_buttons(self):
        self.start_button = QtWidgets.QPushButton(self.steam_Fixture_GUI)
        self.start_button.setGeometry(QtCore.QRect(160, 460, 231, 20))
        self.start_button.setObjectName("start_button")
        self.start_button.clicked.connect(self.start_function)
        self.start_button.setEnabled(False)
        self.start_button.setStatusTip('All fields must be green before sensors\' data can be recorded')

        self.quit_button = QtWidgets.QPushButton(self.steam_Fixture_GUI)
        self.quit_button.setGeometry(QtCore.QRect(410, 460, 231, 20))
        self.quit_button.setObjectName("quit_button")
        self.quit_button.clicked.connect(self.quit_function)
        self.quit_button.setStatusTip('Quit')
        
        self.new_run_button = QtWidgets.QPushButton(self.steam_Fixture_GUI)
        self.new_run_button.setGeometry(QtCore.QRect(660, 460, 231, 20))
        self.new_run_button.setObjectName("new_run_button")
        self.new_run_button.clicked.connect(self.new_run)
        self.new_run_button.setStatusTip('Begin new run')

        self.resume_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.resume_button.setObjectName("resume_button")
        self.inputs.addWidget(self.resume_button)
        self.resume_button.clicked.connect(self.resume_function)
        self.resume_button.setEnabled(False)

    
    def start_function(self):
        self.status_bar.setStatusTip('Recording sensors\' data')
        self.start_button.setStatusTip('Stop recording sensors\' data')
        _translate = QtCore.QCoreApplication.translate
        self.start_button.clicked.disconnect(self.start_function)
        self.start_button.setText(_translate("MainWindow", "Stop"))
        self.start_button.clicked.connect(self.stop_function)
        
        self.steam_appliance.setEnabled(False)
        self.function.setEnabled(False)
        self.food_load.setEnabled(False)
        self.cook_time.setEnabled(False)
        self.sensor_height.setEnabled(False)
        self.initial_water_mass.setEnabled(False)
        self.initial_food_mass.setEnabled(False)

        constants.STEAM_APPLIANCE = self.steam_appliance.text().strip()
        constants.FUNCTION = self.function.text().strip()
        constants.FOOD_LOAD = self.food_load.text().strip()
        constants.COOK_TIME = float(self.cook_time.text().strip())
        constants.SENSOR_HEIGHT = float(self.sensor_height.text().strip())
        constants.INITIAL_WATER_MASS = float(self.initial_water_mass.text().strip())
        constants.INITIAL_FOOD_MASS = float(self.initial_food_mass.text().strip())
        
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
                
            self.final_water_mass.setEnabled(True)
            self.final_water_mass.setValidator(self.double_validator)
            self.final_water_mass.textChanged.connect(self.final_water_mass.check_state)
            self.final_water_mass.textChanged.emit(self.final_water_mass.text())
            self.final_water_mass.textChanged.connect(self.enable_resume)
            self.final_water_mass.setStatusTip('Input final water mass')

            self.final_food_mass.setEnabled(True)
            self.final_food_mass.setValidator(self.double_validator)
            self.final_food_mass.textChanged.connect(self.final_food_mass.check_state)
            self.final_food_mass.textChanged.emit(self.final_food_mass.text())
            self.final_food_mass.textChanged.connect(self.enable_resume)
            self.final_food_mass.setStatusTip('Input final water mass')
    
    def resume_function(self):
        self.status_bar.setStatusTip('Calculating results')
        self.final_food_mass.setEnabled(False)
        self.final_water_mass.setEnabled(False)
        self.resume_button.setEnabled(False)
        
        constants.FINAL_WATER_MASS = float(self.final_water_mass.text().strip())
        constants.FINAL_FOOD_MASS = float(self.final_food_mass.text().strip())
        constants.WATER_LOSS = (constants.INITIAL_FOOD_MASS + constants.INITIAL_WATER_MASS) - (constants.FINAL_FOOD_MASS + constants.FINAL_WATER_MASS)
        constants.STEAM_SENSOR_HUMIDITY = steamSensorFixture.average_Steam_Sensor_Humidity()
        constants.STEAM_TEMP = steamSensorFixture.average_steam_temperature()
        constants.STEAM_ACCUMULATION = steamSensorFixture.steam_Accumulation()
        
        output_worker = Worker(self.resume_function_helper)
        self.threadpool.start(output_worker)
        
    def resume_function_helper(self):
        derivative_time = steamSensorFixture.steam_Fixture_Graphs() 
        self.water_loss.setText('{0:,.2f}'.format(constants.WATER_LOSS))
        self.steam_accumulation.setText('{0:,.2f}'.format(constants.STEAM_ACCUMULATION))
        self.steam_sensor_humidity.setText('{0:,.2f}'.format(constants.STEAM_SENSOR_HUMIDITY))
        self.steam_temp.setText('{0:,.2f}'.format(constants.STEAM_TEMP))
        derivative_df = self.format_final_slope_list(derivative_time)
        plt.savefig('Steam_Fixture_Graphs.png')
        steamSensorFixture.dataframe_to_Excel(derivative_df)
        self.graphs.setPixmap(QtGui.QPixmap('Steam_Fixture_Graphs.png'))
        self.graphs.setScaledContents(True)
        self.status_bar.setStatusTip('Done calculating results. Excel file has been exported')
        
    
    def quit_function(self):
        self.status_bar.setStatusTip('Quitting')
        sys.exit()

#----------------------------------------------------------------- INPUT FUNCTIONS -------------------------------------------------------------------
    def create_input_line_edits(self):
        self.steam_appliance = myLineEdit(self.verticalLayoutWidget)
        self.steam_appliance.setObjectName("steam_appliance")
        self.steam_appliance.setStatusTip('Input steam appliance')
        self.inputs.addWidget(self.steam_appliance)

        self.function = myLineEdit(self.verticalLayoutWidget)
        self.function.setObjectName("function")
        self.function.setStatusTip('Input function')
        self.inputs.addWidget(self.function)
        
        self.food_load = myLineEdit(self.verticalLayoutWidget)
        self.food_load.setObjectName("food_load")
        self.food_load.setStatusTip('Input food load')
        self.inputs.addWidget(self.food_load)

        self.cook_time = myLineEdit(self.verticalLayoutWidget)
        self.cook_time.setObjectName("cook_time")
        self.cook_time.setStatusTip('Input cook time')
        self.inputs.addWidget(self.cook_time)

        self.sensor_height = myLineEdit(self.verticalLayoutWidget)
        self.sensor_height.setObjectName("sensor_height")
        self.sensor_height.setStatusTip('Input sensor height')
        self.inputs.addWidget(self.sensor_height)

        self.initial_water_mass = myLineEdit(self.verticalLayoutWidget)
        self.initial_water_mass.setObjectName("initial_water_mass")
        self.initial_water_mass.setStatusTip('Input initial water mass')
        self.inputs.addWidget(self.initial_water_mass)

        self.initial_food_mass = myLineEdit(self.verticalLayoutWidget)
        self.initial_food_mass.setObjectName("initial_food_mass")
        self.initial_food_mass.setStatusTip('Input initial food mass')
        self.inputs.addWidget(self.initial_food_mass)

        self.final_water_mass = myLineEdit(self.verticalLayoutWidget)
        self.final_water_mass.setObjectName("final_water_mass")
        self.final_water_mass.setStatusTip('Final water mass can not be inputted until the end of the run')
        self.inputs.addWidget(self.final_water_mass)
        self.final_water_mass.setEnabled(False)

        self.final_food_mass = myLineEdit(self.verticalLayoutWidget)
        self.final_food_mass.setObjectName("final_food_mass")
        self.final_food_mass.setStatusTip('Final food mass can not be inputted until the end of the run')
        self.inputs.addWidget(self.final_food_mass)
        self.final_food_mass.setEnabled(False)
    
    def validate_input_line_edits(self):
        input_list = [self.steam_appliance, self.function, self.food_load, self.cook_time, self.sensor_height, self.initial_water_mass, self.initial_food_mass]

        #Connect validator to line edits
        self.steam_appliance.setValidator(self.alphanumeric_validator)
        self.function.setValidator(self.string_validator)
        self.food_load.setValidator(self.string_validator)
        self.cook_time.setValidator(self.double_validator)
        self.sensor_height.setValidator(self.double_validator)
        self.initial_water_mass.setValidator(self.double_validator)
        self.initial_food_mass.setValidator(self.double_validator)

        #Connect line edits to function
        for i in input_list:
            i.textChanged.connect(i.check_state)
            i.textChanged.emit(i.text())
            i.textChanged.connect(self.enable_start)
    
    def enable_start(self):
        qLineEdit_list = [self.steam_appliance, self.function, self.food_load, self.cook_time, self.sensor_height, self.initial_water_mass,self.initial_food_mass]
        inputs_valid = True
        for q in qLineEdit_list:
            if q.validator().validate(q.text(), 0)[0] == QtGui.QValidator.Intermediate:
                inputs_valid = False
        if inputs_valid:
            self.start_button.setEnabled(True)
        else:
            self.start_button.setEnabled(False)
    
    def enable_resume(self):
        if (self.final_water_mass.validator().validate(self.final_water_mass.text(), 0)[0] == QtGui.QValidator.Intermediate) | (self.final_food_mass.validator().validate(self.final_food_mass.text(), 0)[0] == QtGui.QValidator.Intermediate):
            self.resume_button.setEnabled(False)
        else:
            self.resume_button.setEnabled(True)

#----------------------------------------------------------------- OUTPUT FUNCTIONS -------------------------------------------------------------------
    def create_output_line_edits(self):
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.steam_Fixture_GUI)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(220, 20, 241, 401))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.outputs = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.outputs.setContentsMargins(0, 0, 0, 0)
        self.outputs.setObjectName("outputs")

        self.steam_accumulation = myLineEdit(self.verticalLayoutWidget_2)
        self.steam_accumulation.setObjectName("steam_accumulation")
        self.steam_accumulation.setStatusTip('Steam Accumation')
        self.outputs.addWidget(self.steam_accumulation)
        self.steam_accumulation.setEnabled(False)

        self.steam_sensor_humidity = myLineEdit(self.verticalLayoutWidget_2)
        self.steam_sensor_humidity.setObjectName("steam_sensor_humidity")
        self.steam_sensor_humidity.setStatusTip('Average steam sensors\' humidity')
        self.outputs.addWidget(self.steam_sensor_humidity)
        self.steam_sensor_humidity.setEnabled(False)

        self.steam_temp = myLineEdit(self.verticalLayoutWidget_2)
        self.steam_temp.setObjectName("steam_temp")
        self.steam_temp.setStatusTip('Average steam temperature')
        self.outputs.addWidget(self.steam_temp)
        self.steam_temp.setEnabled(False)

        self.water_loss = myLineEdit(self.verticalLayoutWidget_2)
        self.water_loss.setObjectName("water_loss")
        self.water_loss.setStatusTip('Water Loss')
        self.outputs.addWidget(self.water_loss)
        self.water_loss.setEnabled(False)
    
    def create_slope_list(self):
        self.slope = QtWidgets.QListWidget(self.verticalLayoutWidget_2)
        self.slope.setObjectName("slope")
        item = QtWidgets.QListWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        counter = 0
        while counter < 11:
            self.slope.addItem(item)
            item = QtWidgets.QListWidgetItem()
            counter +=1
        self.outputs.addWidget(self.slope)
    
    def format_initial_slope_list(self):
        _translate = QtCore.QCoreApplication.translate
        __sortingEnabled = self.slope.isSortingEnabled()
        self.slope.setSortingEnabled(False)
        item = self.slope.item(0)
        item.setText(_translate("MainWindow", "Slope (Count) - Time (min):"))
        counter = 1
        while counter < 11:
            item = self.slope.item(counter)
            row = str(counter) + '. '
            item.setText(_translate("MainWindow", row))
            counter += 1
        self.slope.setSortingEnabled(__sortingEnabled)
    
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
                item = self.slope.item(counter)
                item.setText(_translate("MainWindow", ' {0}. {1:.2f} @ {2:.2f}'.format(counter, derivative, d[derivative])))
                counter +=1
        return derivative_df

    def create_graph_pixmap(self):
        self.graphs = QtWidgets.QLabel(self.steam_Fixture_GUI)
        self.graphs.setGeometry(QtCore.QRect(470, 20, 321, 401))
        font = QtGui.QFont()
        font.setPointSize(22)
        font.setBold(True)
        font.setWeight(75)
        self.graphs.setFont(font)
        self.graphs.setAlignment(QtCore.Qt.AlignHCenter|QtCore.Qt.AlignTop)
        self.graphs.setObjectName("graphs")
        MainWindow.setCentralWidget(self.steam_Fixture_GUI)

#----------------------------------------------------------------- POPUP FUNCTIONS -------------------------------------------------------------------
    def dataframe_Empty_Check(self):
        return constants.df.empty
    
    def dataframe_Time_Interval_Check(self):
        return constants.df.iloc[-1]['Time (min)'] < .5

    def final_Mass_Popup(self):
        self.status_bar.setStatusTip('Input final masses')
        msg = QMessageBox()
        msg.setText("Enter Food and Water Final Masses (g)")
        msg.setIcon(QMessageBox.Information)
        msg.exec()

    def dataframe_Empty_Popup(self):
        self.status_bar.setStatusTip('Error!')
        msg = QMessageBox()
        msg.setText("Error! Theshold maybe too high or steam sensors maybe wet.")
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
            
#----------------------------------------------------------------- RESET FUNCTIONS -------------------------------------------------------------------
    def reset_Line_Edits(self):
        self.food_load.setText('')
        self.function.setText('')
        self.steam_appliance.setText('')
        self.food_load.setText('')
        self.cook_time.setText('')
        self.sensor_height.setText('')
        self.initial_food_mass.setText('')
        self.initial_water_mass.setText('')
        self.final_food_mass.setText('')
        self.final_water_mass.setText('')
        self.water_loss.setText('')
        self.steam_accumulation.setText('')
        self.steam_sensor_humidity.setText('')
        self.steam_temp.setText('')
        
        self.steam_appliance.setEnabled(True)
        self.function.setEnabled(True)
        self.food_load.setEnabled(True)
        self.cook_time.setEnabled(True)
        self.sensor_height.setEnabled(True)
        self.initial_water_mass.setEnabled(True)
        self.initial_food_mass.setEnabled(True)
        self.water_loss.setEnabled(False)
        self.steam_accumulation.setEnabled(False)
        self.steam_sensor_humidity.setEnabled(False)
        self.steam_temp.setEnabled(False)
        
    def reset_buttons(self):
        _translate = QtCore.QCoreApplication.translate
        self.resume_button.setEnabled(False)
        self.start_button.setEnabled(False)
        if self.start_button.text() == 'Stop':
            self.start_button.clicked.disconnect(self.stop_function)
            self.start_button.setText(_translate("MainWindow", "Start"))
            self.start_button.clicked.connect(self.start_function)
        
    def new_run(self):
        self.status_bar.setStatusTip('Inputs and outputs have been reset')
        constants.STATE = False
        self.flag = False
        self.reset_Line_Edits()
        self.reset_buttons()
        self.count = 0
        self.format_initial_slope_list()

#----------------------------------------------------------------- DISABLE FUNCTIONS -------------------------------------------------------------------
    def disable_all(self):
        self.disable_buttons()
        self.disable_line_edits()
        
    def disable_line_edits(self):
        self.steam_appliance.setEnabled(False)
        self.function.setEnabled(False)
        self.food_load.setEnabled(False)
        self.cook_time.setEnabled(False)
        self.initial_food_mass.setEnabled(False)
        self.initial_water_mass.setEnabled(False)
    
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