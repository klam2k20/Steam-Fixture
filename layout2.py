# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'layout2.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1005, 546)
        self.steam_fixture_GUI = QtWidgets.QWidget(MainWindow)
        self.steam_fixture_GUI.setObjectName("steam_fixture_GUI")
        self.slope_list = QtWidgets.QListWidget(self.steam_fixture_GUI)
        self.slope_list.setGeometry(QtCore.QRect(370, 170, 341, 181))
        self.slope_list.setObjectName("slope_list")
        self.timer_label = QtWidgets.QLabel(self.steam_fixture_GUI)
        self.timer_label.setGeometry(QtCore.QRect(310, 380, 341, 61))
        self.timer_label.setObjectName("timer_label")
        self.graph_label = QtWidgets.QLabel(self.steam_fixture_GUI)
        self.graph_label.setGeometry(QtCore.QRect(730, 20, 241, 331))
        self.graph_label.setObjectName("graph_label")
        self.layoutWidget = QtWidgets.QWidget(self.steam_fixture_GUI)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 331, 337))
        self.layoutWidget.setObjectName("layoutWidget")
        self.input_layout = QtWidgets.QGridLayout(self.layoutWidget)
        self.input_layout.setContentsMargins(0, 0, 0, 0)
        self.input_layout.setObjectName("input_layout")
        self.food_load_label = QtWidgets.QLabel(self.layoutWidget)
        self.food_load_label.setObjectName("food_load_label")
        self.input_layout.addWidget(self.food_load_label, 2, 0, 1, 1)
        self.function_label = QtWidgets.QLabel(self.layoutWidget)
        self.function_label.setObjectName("function_label")
        self.input_layout.addWidget(self.function_label, 1, 0, 1, 1)
        self.steam_appliance_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.steam_appliance_line.setObjectName("steam_appliance_line")
        self.input_layout.addWidget(self.steam_appliance_line, 0, 1, 1, 1)
        self.function_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.function_line.setObjectName("function_line")
        self.input_layout.addWidget(self.function_line, 1, 1, 1, 1)
        self.steam_appliance_label = QtWidgets.QLabel(self.layoutWidget)
        self.steam_appliance_label.setObjectName("steam_appliance_label")
        self.input_layout.addWidget(self.steam_appliance_label, 0, 0, 1, 1)
        self.sensor_height_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.sensor_height_line.setObjectName("sensor_height_line")
        self.input_layout.addWidget(self.sensor_height_line, 4, 1, 1, 1)
        self.sensor_height_label = QtWidgets.QLabel(self.layoutWidget)
        self.sensor_height_label.setObjectName("sensor_height_label")
        self.input_layout.addWidget(self.sensor_height_label, 4, 0, 1, 1)
        self.initial_water_mass_label = QtWidgets.QLabel(self.layoutWidget)
        self.initial_water_mass_label.setObjectName("initial_water_mass_label")
        self.input_layout.addWidget(self.initial_water_mass_label, 5, 0, 1, 1)
        self.final_water_mass_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.final_water_mass_line.setObjectName("final_water_mass_line")
        self.input_layout.addWidget(self.final_water_mass_line, 7, 1, 1, 1)
        self.initial_food_mass_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.initial_food_mass_line.setObjectName("initial_food_mass_line")
        self.input_layout.addWidget(self.initial_food_mass_line, 6, 1, 1, 1)
        self.initial_food_mass_label = QtWidgets.QLabel(self.layoutWidget)
        self.initial_food_mass_label.setObjectName("initial_food_mass_label")
        self.input_layout.addWidget(self.initial_food_mass_label, 6, 0, 1, 1)
        self.final_water_mass_label = QtWidgets.QLabel(self.layoutWidget)
        self.final_water_mass_label.setObjectName("final_water_mass_label")
        self.input_layout.addWidget(self.final_water_mass_label, 7, 0, 1, 1)
        self.cook_time_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.cook_time_line.setObjectName("cook_time_line")
        self.input_layout.addWidget(self.cook_time_line, 3, 1, 1, 1)
        self.cook_time_label = QtWidgets.QLabel(self.layoutWidget)
        self.cook_time_label.setObjectName("cook_time_label")
        self.input_layout.addWidget(self.cook_time_label, 3, 0, 1, 1)
        self.food_load_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.food_load_line.setObjectName("food_load_line")
        self.input_layout.addWidget(self.food_load_line, 2, 1, 1, 1)
        self.initial_water_mass_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.initial_water_mass_line.setObjectName("initial_water_mass_line")
        self.input_layout.addWidget(self.initial_water_mass_line, 5, 1, 1, 1)
        self.final_food_mass_line = QtWidgets.QLineEdit(self.layoutWidget)
        self.final_food_mass_line.setObjectName("final_food_mass_line")
        self.input_layout.addWidget(self.final_food_mass_line, 8, 1, 1, 1)
        self.final_food_mass_label = QtWidgets.QLabel(self.layoutWidget)
        self.final_food_mass_label.setObjectName("final_food_mass_label")
        self.input_layout.addWidget(self.final_food_mass_label, 8, 0, 1, 1)
        self.resume_button = QtWidgets.QPushButton(self.layoutWidget)
        self.resume_button.setObjectName("resume_button")
        self.input_layout.addWidget(self.resume_button, 9, 1, 1, 1)
        self.layoutWidget1 = QtWidgets.QWidget(self.steam_fixture_GUI)
        self.layoutWidget1.setGeometry(QtCore.QRect(310, 450, 343, 32))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.button_layout = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.button_layout.setContentsMargins(0, 0, 0, 0)
        self.button_layout.setObjectName("button_layout")
        self.start_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.start_button.setObjectName("start_button")
        self.button_layout.addWidget(self.start_button)
        self.reset_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.reset_button.setObjectName("reset_button")
        self.button_layout.addWidget(self.reset_button)
        self.exit_button = QtWidgets.QPushButton(self.layoutWidget1)
        self.exit_button.setObjectName("exit_button")
        self.button_layout.addWidget(self.exit_button)
        self.layoutWidget2 = QtWidgets.QWidget(self.steam_fixture_GUI)
        self.layoutWidget2.setGeometry(QtCore.QRect(370, 20, 341, 151))
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.output_layout = QtWidgets.QGridLayout(self.layoutWidget2)
        self.output_layout.setContentsMargins(0, 0, 0, 0)
        self.output_layout.setObjectName("output_layout")
        self.steam_accumulation_line = QtWidgets.QLineEdit(self.layoutWidget2)
        self.steam_accumulation_line.setObjectName("steam_accumulation_line")
        self.output_layout.addWidget(self.steam_accumulation_line, 0, 1, 1, 1)
        self.water_loss_line = QtWidgets.QLineEdit(self.layoutWidget2)
        self.water_loss_line.setObjectName("water_loss_line")
        self.output_layout.addWidget(self.water_loss_line, 3, 1, 1, 1)
        self.sensor_humidity_line = QtWidgets.QLineEdit(self.layoutWidget2)
        self.sensor_humidity_line.setObjectName("sensor_humidity_line")
        self.output_layout.addWidget(self.sensor_humidity_line, 1, 1, 1, 1)
        self.steam_accumulation_label = QtWidgets.QLabel(self.layoutWidget2)
        self.steam_accumulation_label.setObjectName("steam_accumulation_label")
        self.output_layout.addWidget(self.steam_accumulation_label, 0, 0, 1, 1)
        self.water_loss_label = QtWidgets.QLabel(self.layoutWidget2)
        self.water_loss_label.setObjectName("water_loss_label")
        self.output_layout.addWidget(self.water_loss_label, 3, 0, 1, 1)
        self.steam_temp_line = QtWidgets.QLineEdit(self.layoutWidget2)
        self.steam_temp_line.setObjectName("steam_temp_line")
        self.output_layout.addWidget(self.steam_temp_line, 2, 1, 1, 1)
        self.sensor_humidity_label = QtWidgets.QLabel(self.layoutWidget2)
        self.sensor_humidity_label.setObjectName("sensor_humidity_label")
        self.output_layout.addWidget(self.sensor_humidity_label, 1, 0, 1, 1)
        self.steam_temp_label = QtWidgets.QLabel(self.layoutWidget2)
        self.steam_temp_label.setObjectName("steam_temp_label")
        self.output_layout.addWidget(self.steam_temp_label, 2, 0, 1, 1)
        MainWindow.setCentralWidget(self.steam_fixture_GUI)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
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