import  os
import warnings
warnings.filterwarnings("ignore")

# PyQT5
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMessageBox, QApplication, QInputDialog, QWidget

# Supporting Files
import constants

# Class to represent a threadpool
class Worker(QtCore.QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def run(self):
        self.fn(*self.args, **self.kwargs)

# A class to represent a line edit whose background reflects whether 
# a valid input has been entered
class myLineEdit(QtWidgets.QLineEdit):

    # Changes the line edit's background to reflect
    # whether a valid input has been entered
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

# A class to represent a 10 second count down window
class countdown_Window(QWidget):
    def __init__(self, count):
        super().__init__()
        self.setFixedSize(150, 100)
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setObjectName("CountDownWindow")
        
        self.count = int(count - 1)
        self.setup_countdown_label()
        self.setup_countdown()
        
        self.retranslateUi()

    # Creates a QLabel to hold the count down 
    def setup_countdown_label(self):
        self.countdown_label = QtWidgets.QLabel(self)
        self.countdown_label.setGeometry(QtCore.QRect(0, 0, 150, 100))
        self.countdown_label.setAlignment(QtCore.Qt.AlignCenter)
        self.countdown_label.setText('00:00:10')
        font = self.font()
        font.setPointSize(20)
        font.setBold(True)
        self.countdown_label.setFont(font)

    # Creates a timer 
    def setup_countdown(self):
        countdown = QtCore.QTimer(self)
        countdown.timeout.connect(self.showTime)
        countdown.start(1000)
    
    # Decreases the timer time each second
    def showTime(self):
        if self.count > 0:
            text = '00:00:{0:02d}'.format(self.count)
            self.countdown_label.setText(text)
            self.count -=1
        else:
            self.close()
    
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("CountDownWindow", "Count Down"))

# A class to represent the GUI
class Ui_MainWindow(object):

    # Sets up the GUI with all its widgets
    def setupUi(self, MainWindow):
        constants.START_PATH = os.getcwd()
        self.threadpool = QtCore.QThreadPool()
        MainWindow.setObjectName("MainWindow")
        MainWindow.setFixedSize(800, 550)
        qr = MainWindow.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        MainWindow.move(qr.topLeft())
        
        self.steam_Fixture_GUI = QtWidgets.QWidget(MainWindow)
        self.steam_Fixture_GUI.setObjectName("steam_Fixture_GUI")

        #COUNT DOWN WINDOW VARIABLE
        self.countdown_window = None

        #GRAPH WINDOW VARIABLE
        self.graph_window = None

        #STATUS BAR
        self.status_bar = QtWidgets.QStatusBar(MainWindow)
        self.status_bar.setObjectName('status_bar')
        self.status_bar.setVisible(True)
        MainWindow.setStatusBar(self.status_bar)
        
        #LAYOUTS
        self.layoutWidget = QtWidgets.QWidget(self.steam_Fixture_GUI)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 370, 340))
        self.layoutWidget.setObjectName("layoutWidget")

        self.input_layout = QtWidgets.QGridLayout(self.layoutWidget)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setObjectName("input_layout")

        self.layoutWidget1 = QtWidgets.QWidget(self.steam_Fixture_GUI)
        self.layoutWidget1.setGeometry(QtCore.QRect(250, 488, 300, 32))
        self.layoutWidget1.setObjectName("layoutWidget1")

        self.button_layout = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setObjectName("button_layout")

        self.layoutWidget2 = QtWidgets.QWidget(self.steam_Fixture_GUI)
        self.layoutWidget2.setGeometry(QtCore.QRect(410, 20, 370, 160))
        self.layoutWidget2.setObjectName("layoutWidget2")

        self.output_layout = QtWidgets.QGridLayout(self.layoutWidget2)
        self.output_layout.setContentsMargins(0, 0, 0, 0)
        self.output_layout.setObjectName("output_layout")
        
        #VALIDATORS
        regexp = QtCore.QRegExp(r"[\w]+")
        self.alphanumeric_validator = QtGui.QRegExpValidator(regexp)
        regexp = QtCore.QRegExp(r"([0-9][0-9]*(\.[0-9]*[1-9])?|0\.[0-9]*[1-9])")
        self.double_validator = QtGui.QRegExpValidator(regexp)
        regexp = QtCore.QRegExp(r"([1-9][0-9]*(\.[0-9]*[1-9])?|0\.[0-9]*[1-9])")
        self.positive_double_validator = QtGui.QRegExpValidator(regexp)
        regexp = QtCore.QRegExp(r"[a-zA-Z]+")
        self.string_validator = QtGui.QRegExpValidator(regexp)

        #CREATE QLINEEDIT INPUTS
        self.create_input_labels()
        self.create_input_line_edits()

        #CREATE QLINEEDIT OUTPUTS
        self.create_output_labels()
        self.create_output_line_edits()

        #CREATE QLISTWIDGE SLOPE
        self.create_slope_list()
        self.format_initial_slope_list()

        #CREATE BUTTONS
        self.create_buttons()

        MainWindow.setCentralWidget(self.steam_Fixture_GUI)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        return self

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Steam Fixture GUI"))
        self.food_load_label.setText(_translate("MainWindow", "Food Load"))
        self.function_label.setText(_translate("MainWindow", "Function"))
        self.steam_appliance_label.setText(_translate("MainWindow", "Steam Appliance"))
        self.threshold_label.setText(_translate("MainWindow", "Sensor Threshold"))
        self.sensor_height_label.setText(_translate("MainWindow", "Sensor Height (in)"))
        self.initial_water_mass_label.setText(_translate("MainWindow", "Initial Water Mass (g)"))
        self.initial_food_mass_label.setText(_translate("MainWindow", "Initial Food Mass (g)"))
        self.final_water_mass_label.setText(_translate("MainWindow", "Final Water Mass (g)"))
        self.monitor_time_label.setText(_translate("MainWindow", "Monitor Time (min)"))
        self.final_food_mass_label.setText(_translate("MainWindow", "Final Food Mass (g)"))
        self.resume_button.setText(_translate("MainWindow", "Resume"))
        self.start_button.setText(_translate("MainWindow", "Start"))
        self.reset_button.setText(_translate("MainWindow", "Reset"))
        self.exit_button.setText(_translate("MainWindow", "Exit"))
        self.steam_accumulation_label.setText(_translate("MainWindow", "Steam Accumulation \n (Count * min)"))
        self.water_loss_label.setText(_translate("MainWindow", "Water Loss (g)"))
        self.sensor_humidity_label.setText(_translate("MainWindow", "Sensors\' Humidity (%)"))
        self.steam_temp_label.setText(_translate("MainWindow", "Steam Temperature (C)"))
        
    # Create the QPushButtons
    def create_buttons(self):
        self.start_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.start_button.setObjectName("start_button")
        self.button_layout.addWidget(self.start_button)
        self.start_button.setEnabled(False)
        self.start_button.setStatusTip('All fields must be green before sensors\' data can be recorded')

        self.exit_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.exit_button.setObjectName("exit_button")
        self.button_layout.addWidget(self.exit_button)
        self.exit_button.setStatusTip('Exit')
        
        self.reset_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.reset_button.setObjectName("reset_button")
        self.button_layout.addWidget(self.reset_button)
        self.reset_button.setStatusTip('Reset')

        self.resume_button = QtWidgets.QPushButton(self.layoutWidget)
        self.resume_button.setObjectName("resume_button")
        self.input_layout.addWidget(self.resume_button, 10, 1, 1, 1)
        self.resume_button.setEnabled(False)
        self.resume_button.setStatusTip('Resume')

    # Creates the QLabels for the inputs
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
        self.input_layout.addWidget(self.initial_water_mass_label, 6, 0, 1, 1)

        self.initial_food_mass_label = QtWidgets.QLabel(self.layoutWidget)
        self.initial_food_mass_label.setObjectName("initial_food_mass_label")
        self.input_layout.addWidget(self.initial_food_mass_label, 7, 0, 1, 1)

        self.final_water_mass_label = QtWidgets.QLabel(self.layoutWidget)
        self.final_water_mass_label.setObjectName("final_water_mass_label")
        self.input_layout.addWidget(self.final_water_mass_label, 8, 0, 1, 1)

        self.monitor_time_label = QtWidgets.QLabel(self.layoutWidget)
        self.monitor_time_label.setObjectName("monitor_time_label")
        self.input_layout.addWidget(self.monitor_time_label, 3, 0, 1, 1)

        self.final_food_mass_label = QtWidgets.QLabel(self.layoutWidget)
        self.final_food_mass_label.setObjectName("final_food_mass_label")
        self.input_layout.addWidget(self.final_food_mass_label, 9, 0, 1, 1)
        
        self.threshold_label = QtWidgets.QLabel(self.layoutWidget)
        self.threshold_label.setObjectName("threshold_label")
        self.input_layout.addWidget(self.threshold_label, 5, 0, 1, 1)

    # Creates the QLineEdits for the inputs
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
        self.input_layout.addWidget(self.final_water_mass_line, 8, 1, 1, 1)
        self.final_water_mass_line.setStatusTip('Final water mass can not be inputted until the end of the run')
        self.final_water_mass_line.setEnabled(False)

        self.initial_food_mass_line = myLineEdit(self.layoutWidget)
        self.initial_food_mass_line.setObjectName("initial_food_mass_line")
        self.input_layout.addWidget(self.initial_food_mass_line, 7, 1, 1, 1)
        self.initial_food_mass_line.setStatusTip('Input initial food mass')

        self.monitor_time_line = myLineEdit(self.layoutWidget)
        self.monitor_time_line.setObjectName("monitor_time_line")
        self.input_layout.addWidget(self.monitor_time_line, 3, 1, 1, 1)
        self.monitor_time_line.setStatusTip('Input cook time')

        self.food_load_line = myLineEdit(self.layoutWidget)
        self.food_load_line.setObjectName("food_load_line")
        self.input_layout.addWidget(self.food_load_line, 2, 1, 1, 1)
        self.food_load_line.setStatusTip('Input food load')

        self.threshold_line = myLineEdit(self.layoutWidget)
        self.threshold_line.setObjectName("threshold_line")
        self.threshold_line.setText('10')
        self.input_layout.addWidget(self.threshold_line, 5, 1, 1, 1)
        self.threshold_line.setStatusTip('Input steam sensor threshold')
        
        self.initial_water_mass_line = myLineEdit(self.layoutWidget)
        self.initial_water_mass_line.setObjectName("initial_water_mass_line")
        self.input_layout.addWidget(self.initial_water_mass_line, 6, 1, 1, 1)
        self.initial_water_mass_line.setStatusTip('Input initial water mass')

        self.final_food_mass_line = myLineEdit(self.layoutWidget)
        self.final_food_mass_line.setObjectName("final_food_mass_line")
        self.input_layout.addWidget(self.final_food_mass_line, 9, 1, 1, 1)
        self.final_food_mass_line.setStatusTip('Final food mass can not be inputted until the end of the run')
        self.final_food_mass_line.setEnabled(False)

    # Creates the QLabels for the outputs
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

    # Creates the QLineEdit for the outputs    
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
    
    # Creates the QListWidget for the steam slopes
    def create_slope_list(self):
        self.slope_list = QtWidgets.QListWidget(self.steam_Fixture_GUI)
        self.slope_list.setGeometry(QtCore.QRect(410, 200, 370, 160))
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
    
    # Formats the QListWidget with a title
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

