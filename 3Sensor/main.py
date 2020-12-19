import math
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

# PyQT5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QApplication, QInputDialog, QWidget

# Supporting Files
import GUI
import steamSensorFixture
import constants

# A class to represent the main window the user will interact with
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        self.do_init = QtCore.QEvent.registerEventType()
        QtWidgets.QMainWindow.__init__(self)
        super(MainWindow, self).__init__()
        self.ui = GUI.Ui_MainWindow().setupUi(self)
        self.steamSensorFixture = steamSensorFixture.steamSensorFixture()

        # Timer
        self.setup_timer_label()
        self.setup_timer()

        # Connect line inputs to validators
        self.validate_input_line_edits()
        
        # Check if temp probes are connected correctly
        self.temp_probe_popup()
        
        # Quit button and shortcut
        quit_action = QtWidgets.QAction('Quit', self)
        quit_action.setShortcuts(['Ctrl+Q', 'Ctrl+W'])
        quit_action.triggered.connect(QtWidgets.qApp.closeAllWindows)
        self.addAction(quit_action)
        self.ui.exit_button.clicked.connect(QtWidgets.qApp.closeAllWindows)

        # Connecting buttons to functions
        self.ui.start_button.clicked.connect(self.start_function)
        self.ui.resume_button.clicked.connect(self.resume_function)
        self.ui.reset_button.clicked.connect(self.reset)

    # Creates a QLabel that will contain the timer
    def setup_timer_label(self):
        _translate = QtCore.QCoreApplication.translate
        self.ui.flag = False
        self.ui.timer_label = QtWidgets.QLabel(self.ui.steam_Fixture_GUI)
        self.ui.timer_label.setGeometry(QtCore.QRect(250, 407, 300, 60))
        self.ui.timer_label.setObjectName("timer_label")
        self.ui.timer_label.setAlignment(QtCore.Qt.AlignCenter)
        self.ui.timer_label.setStatusTip('Timer')
        self.ui.timer_label.setText(_translate("MainWindow", "00:00:00"))
        self.timer_background()
    
    # Creates a timer
    def setup_timer(self):
        timer = QtCore.QTimer(self.ui.steam_Fixture_GUI)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
    
    # Updates the timer every second. 
    # @ 10 s starts the count down window
    # @ 1 s prompts the user for additional monitor time if wanted
    def showTime(self):   
        if self.ui.flag:
            self.timer_background()
            constants.UPDATED_TIME-= 1
            text = self.format_timer()
            self.ui.timer_label.setText(text)
            if constants.UPDATED_TIME <= 10:
                self.countDown()
                
            if constants.UPDATED_TIME == 1:
                self.additional_time_input_dialog()
    
    # Creates the count down window @ 10 s
    def countDown(self):
        if self.ui.countdown_window is None:
            self.ui.countdown_window = GUI.countdown_Window(constants.UPDATED_TIME)
        self.ui.countdown_window.show()

    # Creates the prompt asking the user if he/she would like additional monitoring time
    def additional_time_input_dialog(self):
        additional_mins,ok = QInputDialog.getInt(self.ui.steam_Fixture_GUI,"ADD TIME","Additional Monitor Time (min): ")
        if ok and additional_mins != 0:
            self.ui.countdown_window = None
            constants.MONITOR_TIME += (additional_mins * 60)
            constants.UPDATED_TIME += (additional_mins * 60)
            self.ui.flag = True
        elif not ok or additional_mins == 0:
            self.ui.flag = False
            constants.UPDATED_TIME -=1
            self.ui.timer_label.setText('00:00:00')
            self.stop_function()
    
    # Format timer: hour: min: sec
    def format_timer(self):
        h = int(math.floor(constants.UPDATED_TIME / 3600))
        m = int(math.floor((constants.UPDATED_TIME % 3600) / 60))
        s = int(constants.UPDATED_TIME % 3600 % 60)
        text = '{0:02d}:{1:02d}:{2:02d}'.format(h,m,s)
        return text

    # Updates the timer's background to reflect whether sensor logging has begun. 
    def timer_background(self):
        if constants.START_TIME !=0:
            self.temp_probe_popup()
            self.ui.timer_label.setStyleSheet("background-color: #c4df9b; border: 1px solid black;")

            self.ui.status_bar.setStatusTip('Steam detected.Recording sensors\' data')
        else:
            self.ui.timer_label.setStyleSheet("background-color: #fff79a; border: 1px solid black;")

    # Stores all user inputs in variables
    # Disables all input line edits
    # Begins count down and sensor logging once at least one steam sensor value is 
    # above the sensor threshold inputted
    def start_function(self):
        self.ui.status_bar.setStatusTip('Steam has not been detected')
        self.ui.start_button.setStatusTip('Monitoring...')
        self.ui.start_button.setEnabled(False)
    
        self.ui.steam_appliance_line.setEnabled(False)
        self.ui.function_line.setEnabled(False)
        self.ui.food_load_line.setEnabled(False)
        self.ui.monitor_time_line.setEnabled(False)
        self.ui.sensor_height_line.setEnabled(False)
        self.ui.threshold_line.setEnabled(False)
        self.ui.initial_water_mass_line.setEnabled(False)
        self.ui.initial_food_mass_line.setEnabled(False)

        constants.STEAM_APPLIANCE = self.ui.steam_appliance_line.text().strip()
        constants.FUNCTION = self.ui.function_line.text().strip()
        constants.FOOD_LOAD = self.ui.food_load_line.text().strip()
        constants.MONITOR_TIME = float(self.ui.monitor_time_line.text().strip()) * 60
        constants.UPDATED_TIME = constants.MONITOR_TIME
        constants.SENSOR_HEIGHT = float(self.ui.sensor_height_line.text().strip())
        constants.INITIAL_WATER_MASS = float(self.ui.initial_water_mass_line.text().strip())
        constants.INITIAL_FOOD_MASS = float(self.ui.initial_food_mass_line.text().strip())
        
        self.ui.flag = True
        record_worker = GUI.Worker(self.steamSensorFixture.record_data)
        self.ui.threadpool.start(record_worker)
    
    # Outputs any popup windows with errors
    def stop_function(self):
        _translate = QtCore.QCoreApplication.translate

        if self.dataframe_Empty_Check():
            self.dataframe_Empty_Popup()
        elif self.dataframe_Time_Interval_Check():
            self.dataframe_Time_Interval_Popup()
        elif not self.dataframe_Empty_Check() and not self.dataframe_Time_Interval_Check():
            self.final_Mass_Popup()
            self.ui.resume_button.setEnabled(False)
            self.ui.resume_button.setStatusTip('Calculate results')
            self.ui.start_button.setEnabled(False)
                
            self.ui.final_water_mass_line.setEnabled(True)
            self.ui.final_water_mass_line.setValidator(self.ui.double_validator)
            self.ui.final_water_mass_line.textChanged.connect(self.ui.final_water_mass_line.check_state)
            self.ui.final_water_mass_line.textChanged.emit(self.ui.final_water_mass_line.text())
            self.ui.final_water_mass_line.textChanged.connect(self.enable_resume)
            self.ui.final_water_mass_line.setStatusTip('Input final water mass')

            self.ui.final_food_mass_line.setEnabled(True)
            self.ui.final_food_mass_line.setValidator(self.ui.double_validator)
            self.ui.final_food_mass_line.textChanged.connect(self.ui.final_food_mass_line.check_state)
            self.ui.final_food_mass_line.textChanged.emit(self.ui.final_food_mass_line.text())
            self.ui.final_food_mass_line.textChanged.connect(self.enable_resume)
            self.ui.final_food_mass_line.setStatusTip('Input final mass mass')
    
    # Calculates all outputs: steam accumulation, average steam temp, average steam sensor humidity, 
    # water loss, and steam sensor slopes
    def resume_function(self):
        self.ui.status_bar.setStatusTip('Calculating results')
        self.ui.final_food_mass_line.setEnabled(False)
        self.ui.final_water_mass_line.setEnabled(False)
        self.ui.resume_button.setEnabled(False)
        
        self.steamSensorFixture.new_Dir()
        
        constants.FINAL_WATER_MASS = float(self.ui.final_water_mass_line.text().strip())
        constants.FINAL_FOOD_MASS = float(self.ui.final_food_mass_line.text().strip())
        constants.WATER_LOSS = (constants.INITIAL_FOOD_MASS + constants.INITIAL_WATER_MASS) - (constants.FINAL_FOOD_MASS + constants.FINAL_WATER_MASS)
        constants.STEAM_SENSOR_HUMIDITY = self.steamSensorFixture.average_Steam_Sensor_Humidity()
        constants.STEAM_TEMP = self.steamSensorFixture.average_steam_temperature()
        constants.STEAM_ACCUMULATION = self.steamSensorFixture.steam_Accumulation()
        
        output_worker = GUI.Worker(self.resume_function_helper)
        self.ui.threadpool.start(output_worker)
        
    def resume_function_helper(self):
        if self.ui.graph_window is None:
            self.ui.graph_window = steamSensorFixture.GraphWindow()
        self.ui.graph_window.show()

        derivative_time = self.ui.graph_window.derivative_time
        self.ui.water_loss_line.setText('{0:,.2f}'.format(constants.WATER_LOSS))
        self.ui.steam_accumulation_line.setText('{0:,.2f}'.format(constants.STEAM_ACCUMULATION))
        self.ui.sensor_humidity_line.setText('{0:,.2f}'.format(constants.STEAM_SENSOR_HUMIDITY))
        self.ui.steam_temp_line.setText('{0:,.2f}'.format(constants.STEAM_TEMP))
        derivative_df = self.format_final_slope_list(derivative_time)

        self.steamSensorFixture.dataframe_to_Excel(derivative_df)
        self.ui.status_bar.setStatusTip('Done calculating results. Excel file has been exported')
    
    # Formats the QListWidget with the top 10 steam sensor slopes
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
                item = self.ui.slope_list.item(counter)
                item.setText(_translate("MainWindow", ' {0}. {1:.2f} @ {2:.2f}'.format(counter, derivative, d[derivative])))
                counter +=1
        return derivative_df

    # Checks to see if the user inputs are valid
    def validate_input_line_edits(self):
        input_list = [self.ui.steam_appliance_line, self.ui.function_line, self.ui.food_load_line, self.ui.monitor_time_line, self.ui.sensor_height_line, self.ui.threshold_line, self.ui.initial_water_mass_line, self.ui.initial_food_mass_line]

        #Connect validator to line edits
        self.ui.steam_appliance_line.setValidator(self.ui.alphanumeric_validator)
        self.ui.function_line.setValidator(self.ui.string_validator)
        self.ui.food_load_line.setValidator(self.ui.string_validator)
        self.ui.monitor_time_line.setValidator(self.ui.positive_double_validator)
        self.ui.sensor_height_line.setValidator(self.ui.double_validator)
        self.ui.threshold_line.setValidator(self.ui.double_validator)
        self.ui.initial_water_mass_line.setValidator(self.ui.double_validator)
        self.ui.initial_food_mass_line.setValidator(self.ui.double_validator)

        #Connect line edits to function
        for i in input_list:
            i.textChanged.connect(i.check_state)
            i.textChanged.emit(i.text())
            i.textChanged.connect(self.enable_start)
    
    # Enables the start button if all user inputs are valid
    def enable_start(self):
        qLineEdit_list = [self.ui.steam_appliance_line, self.ui.function_line, self.ui.food_load_line, self.ui.monitor_time_line, self.ui.sensor_height_line, self.ui.threshold_line, self.ui.initial_water_mass_line, self.ui.initial_food_mass_line]
        inputs_valid = True
        for q in qLineEdit_list:
            if q.validator().validate(q.text(), 0)[0] == QtGui.QValidator.Intermediate:
                inputs_valid = False
        if inputs_valid:
            constants.THRESHOLD = float(self.ui.threshold_line.text().strip())
            
            if self.steamSensorFixture.check_Sensors():
                self.ui.start_button.setEnabled(True)
            else:
                self.sensor_Wet_Popup()
        else:
            self.ui.start_button.setEnabled(False)
    
    # Enables the resume button if all user inputs are valid
    def enable_resume(self):
        if (self.ui.final_water_mass_line.validator().validate(self.ui.final_water_mass_line.text(), 0)[0] == QtGui.QValidator.Intermediate) | (self.ui.final_food_mass_line.validator().validate(self.ui.final_food_mass_line.text(), 0)[0] == QtGui.QValidator.Intermediate):
            self.ui.resume_button.setEnabled(False)
        else:
            self.ui.resume_button.setEnabled(True)
    
    # Create a popup alerting the user that the temp probe can not be correctly read
    def temp_probe_popup(self):
        self.steamSensorFixture.update_temp_id()
        if not constants.TEMP_PROBE_STATE:
            self.ui.status_bar.setStatusTip('Error!')
            msg = QMessageBox()
            msg.setText('Error! Temperature probes are not connected correctly')
            msg.setIcon(QMessageBox.Critical)
            msg.exec()
            self.disable_all()

    # Create a popup alerting the user that the final masses must be inputted
    def final_Mass_Popup(self):
        self.ui.status_bar.setStatusTip('Input final masses')
        msg = QMessageBox()
        msg.setText("Enter Food and Water Final Masses (g)")
        msg.setIcon(QMessageBox.Information)
        msg.exec()
    
    # Create a popup alerting the user that the steam sensors' values are above the
    # inputted sensor threshold
    def sensor_Wet_Popup(self):
        self.ui.status_bar.setStatusTip('Error!')
        msg = QMessageBox()
        msg.setText('Error! Steam sensors are not dry')
        msg.setIcon(QMessageBox.Critical)
        msg.exec()
    
    # Create a popup alerting the user that no steam sensor data was logged. 
    # Sensor threshold was too high
    def dataframe_Empty_Popup(self):
        self.ui.status_bar.setStatusTip('Error!')
        msg = QMessageBox()
        msg.setText("Error! No data recorded! Theshold maybe too high.")
        msg.setIcon(QMessageBox.Critical)            
        msg.exec()
        self.disable_all()

    # Create a popup alerting the user that the sensor logging time
    # was below 30 s    
    def dataframe_Time_Interval_Popup(self):
        self.ui.status_bar.setStatusTip('Error!')
        msg = QMessageBox()
        msg.setText("Error! Please increase monitor time on next run.")
        msg.setIcon(QMessageBox.Critical)
        msg.exec()
        self.isable_all()
            
    # Resets all line edits
    def reset_Line_Edits(self):
        self.ui.food_load_line.setText('')
        self.ui.function_line.setText('')
        self.ui.steam_appliance_line.setText('')
        self.ui.monitor_time_line.setText('')
        self.ui.sensor_height_line.setText('')
        self.ui.threshold_line.setText('10')
        self.ui.initial_food_mass_line.setText('')
        self.ui.initial_water_mass_line.setText('')
        self.ui.final_food_mass_line.setText('')
        self.ui.final_water_mass_line.setText('')

        self.ui.water_loss_line.setText('')
        self.ui.steam_accumulation_line.setText('')
        self.ui.sensor_humidity_line.setText('')
        self.ui.steam_temp_line.setText('')
        
        color = '#fdfefe'
        self.ui.final_food_mass_line.setStyleSheet('QLineEdit { background-color: %s }' % color)
        self.ui.final_water_mass_line.setStyleSheet('QLineEdit { background-color: %s }' % color)
        
        self.ui.steam_appliance_line.setEnabled(True)
        self.ui.function_line.setEnabled(True)
        self.ui.food_load_line.setEnabled(True)
        self.ui.monitor_time_line.setEnabled(True)
        self.ui.sensor_height_line.setEnabled(True)
        self.ui.threshold_line.setEnabled(True)
        self.ui.initial_water_mass_line.setEnabled(True)
        self.ui.initial_food_mass_line.setEnabled(True)

        self.ui.water_loss_line.setEnabled(False)
        self.ui.steam_accumulation_line.setEnabled(False)
        self.ui.sensor_humidity_line.setEnabled(False)
        self.ui.steam_temp_line.setEnabled(False)
        
        self.ui.final_water_mass_line.setStatusTip('Final water mass can not be inputted until the end of the run')
        self.ui.final_food_mass_line.setStatusTip('Final food mass can not be inputted until the end of the run')
    
    # Resets all line buttons
    def reset_buttons(self):
        _translate = QtCore.QCoreApplication.translate
        self.ui.resume_button.setEnabled(False)
        self.ui.start_button.setEnabled(False)
        
        self.ui.start_button.setStatusTip('All fields must be green before sensors\' data can be recorded')
        self.ui.resume_button.setStatusTip('Start recording sensors\' data first')
    
    # Resets timer
    def reset_timer(self):
        self.ui.timer_label.setText('00:00:00')
        self.ui.flag = False
        self.ui.timer_label.setStyleSheet("background-color: #fff79a; border: 1px solid black;")
    
    # Resets variables
    def reset_variables(self):
        constants.START_TIME = 0
        constants.MONITOR_TIME = -1
        constants.UPDATED_TIME = -1
        constants.ADDITIONAL_MINS = -1
        constants.TEMP_PROBE_STATE = True
        constants.THRESHOLD = 10
    
    # Checks to see if the temp probe is connected correctly
    def reset_temp_probe(self):
        self.temp_probe_popup()
    
    # Resets countdown window
    def reset_countdown(self):
        if self.ui.countdown_window != None:
            self.ui.countdown_window.close()
            self.ui.countdown_window = None
    
    # Resets graph window
    def reset_graph(self):
        if self.ui.graph_window != None:
            self.ui.graph_window.close()
            self.ui.graph_window = None
    
    # Resets everything within the GUI
    def reset(self):
        self.ui.status_bar.setStatusTip('Inputs and outputs have been reset')
        self.steamSensorFixture.reset_Dir()
        self.reset_Line_Edits()
        self.reset_buttons()
        self.reset_timer()
        self.reset_variables()
        self.reset_countdown()
        self.reset_graph()
        self.ui.format_initial_slope_list()
        self.reset_temp_probe()
        
    # Disables everything within the GUI
    def disable_all(self):
        self.disable_buttons()
        self.disable_line_edits()
        self.ui.flag = False
    
    # Disables the input QLineEdits
    def disable_line_edits(self):
        self.ui.steam_appliance_line.setEnabled(False)
        self.ui.function_line.setEnabled(False)
        self.ui.food_load_line.setEnabled(False)
        self.ui.monitor_time_line.setEnabled(False)
        self.ui.sensor_humidity_line.setEnabled(False)
        self.ui.sensor_height_line.setEnabled(False)
        self.ui.threshold_line.setEnabled(False)
        self.ui.initial_food_mass_line.setEnabled(False)
        self.ui.initial_water_mass_line.setEnabled(False)
    
    # Disables the QPushButtons
    def disable_buttons(self):
        self.ui.start_button.setEnabled(False)

    # Calculates sensor logging time
    def calculate_monitor_time(self):
        return (constants.df.iloc[-1]['Time (min)'] - constants.df.iloc[0]['Time (min)'])
    
    # Checks if the dataframe is empty
    def dataframe_Empty_Check(self):
        return constants.df.empty
    
    # Checks that the sensor logging time is at least 30 s
    def dataframe_Time_Interval_Check(self):
        return self.calculate_monitor_time() < .5

#----------------------------------------------------------------- MAIN FUNCTIONS -------------------------------------------------------------------
if __name__ == "__main__":
    import sys

    if sys.flags.interactive != 1:
        app = QtWidgets.QApplication(sys.argv)
        app.processEvents()
        program = MainWindow()
        program.show()
        app.exec_()
    
