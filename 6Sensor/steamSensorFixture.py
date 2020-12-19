import xlsxwriter
import os
import sys
import time
import glob
import numpy as np
import pandas as pd
from datetime import date

# AD/DA Board
import ADS1256
import RPi.GPIO as GPIO

# External graphs
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

# Canvas for external grpahs
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QWidget

# Supporting Script
import constants

# A class to represent a steam sensor fixture with all its sensor components
class steamSensorFixture():

    # Updates constants.TEMP_PROBE_SURR and constants.TEMP_PROBE_STEAM variables to
    # hold the current 1Wire Temp Probe
    def update_temp_id(self):
        try:
            mypath = '/sys/bus/w1/devices/'
            onlylinks = [f for f in os.listdir(mypath) if os.path.islink(os.path.join(mypath, f))]
            onlylinks.remove('w1_bus_master1')
            constants.TEMP_PROBE_SURR = str(onlylinks[0])
            constants.TEMP_PROBE_STEAM = str(onlylinks[1])
        except IndexError:
            constants.TEMP_PROBE_STATE = False

    # Reads in the data from the 1Wire Temp Probe
    def read_temp_raw(self, id):
        try:
            base_dir = '/sys/bus/w1/devices/'
            thermo_file = glob.glob(base_dir + id)[0] + '/w1_slave'
            f = open(thermo_file, 'r')
            lines = f.readlines()
            f.close()
            return lines
        except FileNotFoundError:
            constants.TEMP_PROBE_STATE = False
    
    # Returns the temperature read in from the 1Wire Temp Probe
    def read_temp(self, id):
        try:
            lines = self.read_temp_raw(id)
            while lines[0].strip()[-3:] != 'YES':
                lines = self.read_temp_raw(id)
            equals_pos = lines[1].find('t=')
            if equals_pos != -1:
                temp_string = lines[1][equals_pos+2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c
        except IndexError:
            constants.TEMP_PROBE_STATE = False
        except TypeError:
            constants.TEMP_PROBE_STATE = False

    # Creates a RAW DATA folder & Date folder # Unit folder to hold the logged sensor data.
    # Changes the directory to the Date folder
    def new_Dir(self):
        DATE = date.today().strftime("%m-%d-%y")
        path1 = os.getcwd() + '/' + 'RAW DATA'
        path2 = path1 + "/" + DATE
        path3 = path2 + "/" + constants.STEAM_APPLIANCE
        
        if not os.path.exists(path1):
            os.mkdir(path1)
            os.mkdir(path2)
            os.mkdir(path3)
        elif not os.path.exists(path2):
            os.mkdir(path2)
            os.mkdir(path3)
        elif not os.path.exists(path3):
            os.mkdir(path3)

        onlylinks = [f for f in os.listdir(path3) if os.path.isdir(os.path.join(path3, f))]
        counter = len(onlylinks)
        file_path = path3 + "/" + str(counter)
        os.mkdir(file_path)
        os.chdir(file_path)
    
    # Changes the directory to the initial start path
    def reset_Dir(self):
        os.chdir(constants.START_PATH)

    # Returns a file name for the Excel file           
    def excel_FileName(self):
        return 'Steam_Fixture_RAW_DATA.xlsx'

    # Converts the dataframe to an excel file and inserts the graphs
    # within the excel file
    def dataframe_to_Excel(self, derivative_df):
        input_df = self.input_to_df()
        writer = pd.ExcelWriter(self.excel_FileName(), engine='xlsxwriter')
        constants.df.to_excel(writer, sheet_name= 'Raw_Data')
        input_df.to_excel(writer, sheet_name= 'Procedure_Results_Data')
        derivative_df.to_excel(writer, sheet_name= 'Top Derivative - Time')
        workbook = writer.book
        worksheet = workbook.add_worksheet('Graphs')
        finalRow = len(constants.df.index)
        chart1, chart2, chart3 = self.excelGraph(workbook, finalRow)
        worksheet.insert_chart('B2', chart1)
        worksheet.insert_chart('B22', chart2)
        worksheet.insert_chart('O2', chart3)
        workbook.close()
    
    # Create excel graphs 
    def excelGraph(self, workbook, finalRow):
        chart1 = workbook.add_chart({'type': 'line'})
        chart2 = workbook.add_chart({'type': 'line'})
        chart3 = workbook.add_chart({'type': 'line'})
            
        try:
            chart1.add_series({
                'name': 'Steam Accumulation',
                'categories': ['Raw_Data', 1, 0, finalRow, 0],
                'values': ['Raw_Data', 1, 17, finalRow, 17],
            })
                
            chart2.add_series({
                'name': 'Humidity 1',
                'categories': ['Raw_Data', 1, 0, finalRow, 0],
                'values': ['Raw_Data', 1, 3, finalRow, 3],
            })
            chart2.add_series({
                'name': 'Humidity 2',
                'categories': ['Raw_Data', 1, 0, finalRow, 0],
                'values': ['Raw_Data', 1, 5, finalRow, 5],
            })
            chart2.add_series({
                'name': 'Humidity 3',
                'categories': ['Raw_Data', 1, 0, finalRow, 0],
                'values': ['Raw_Data', 1, 7, finalRow, 7],
            })
            chart2.add_series({
                'name': 'Humidity 3',
                'categories': ['Raw_Data', 1, 0, finalRow, 0],
                'values': ['Raw_Data', 1, 9, finalRow, 9],
            })
            chart2.add_series({
                'name': 'Humidity 3',
                'categories': ['Raw_Data', 1, 0, finalRow, 0],
                'values': ['Raw_Data', 1, 11, finalRow, 11],
            })
            chart2.add_series({
                'name': 'Humidity 3',
                'categories': ['Raw_Data', 1, 0, finalRow, 0],
                'values': ['Raw_Data', 1, 13, finalRow, 13],
            })

            chart3.add_series({
                'name': 'Steam Temp',
                'categories': ['Raw_Data', 1, 0, finalRow, 0],
                'values': ['Raw_Data', 1, 8, finalRow, 8],
            })
            chart3.add_series({
                'name': 'Surrounding Temp',
                'categories': ['Raw_Data', 1, 0, finalRow, 0],
                'values': ['Raw_Data', 1, 9, finalRow, 9],
            })
                
        except:
            pass

        # Configure the chart axes.
        chart1.set_y_axis({'name': 'Steam Accumulation (Count * min)'})
        chart1.set_x_axis({'name': 'Time (min)'})
        chart1.set_size({'width': 750, 'height': 400})

        chart2.set_y_axis({'name': 'Humidity (%)'})
        chart2.set_x_axis({'name': 'Time (min)'})
        chart2.set_size({'width': 750, 'height': 400})

        chart3.set_y_axis({'name': 'Temperature (C)'})
        chart3.set_x_axis({'name': 'Time (min)'})
        chart3.set_size({'width': 750, 'height': 400})

        return chart1, chart2, chart3

    # Creates a dataframe with the following headers:
    # Time (min), Steam Sensor 1 (Count), Humidity 1 (%) ... Steam Sensor 3 (Count), Humidity 3 (%), 
    # Steam Temp. (C), Surrounding Temp. (C)
    def dataframe_Structure(self):
        columns = {'Time (min)':[], 'Steam Sensor 1 (Count)':[], 'Humidity 1 (%)':[],'Steam Sensor 2 (Count)':[], 'Humidity 2 (%)':[], 
                'Steam Sensor 3 (Count)':[], 'Humidity 3 (%)':[], 'Steam Sensor 4 (Count)':[], 'Humidity 4 (%)':[], 
                'Steam Sensor 5 (Count)':[], 'Humidity 5 (%)':[], 'Steam Sensor 6 (Count)':[], 'Humidity 6 (%)':[],
                'Steam Temp. (C)':[], 'Surrounding Temp. (C)':[]}
        df = pd.DataFrame(columns)
        return df

    # Updates the dataframe with a new row holding the new sensor data
    def update_Dataframe(self, updated_time, ADC_Value):
        analog_Steam_Sensor_1 = ADC_Value[constants.STEAM_SENSOR1]
        analog_Steam_Sensor_2 = ADC_Value[constants.STEAM_SENSOR2]
        analog_Steam_Sensor_3 = ADC_Value[constants.STEAM_SENSOR3]
        analog_Steam_Sensor_4 = ADC_Value[constants.STEAM_SENSOR4]
        analog_Steam_Sensor_5 = ADC_Value[constants.STEAM_SENSOR5]
        analog_Steam_Sensor_6 = ADC_Value[constants.STEAM_SENSOR6]
        humidity_Steam_Sensor_1, humidity_Steam_Sensor_2, humidity_Steam_Sensor_3, humidity_Steam_Sensor_4, humidity_Steam_Sensor_5, humidity_Steam_Sensor_6 = self.all_Sensors_to_humidity(ADC_Value)
        if ((humidity_Steam_Sensor_1 >= constants.THRESHOLD) | (humidity_Steam_Sensor_2 >= constants.THRESHOLD) | (humidity_Steam_Sensor_3 >= constants.THRESHOLD) | (humidity_Steam_Sensor_4 >= constants.THRESHOLD) | (humidity_Steam_Sensor_5 >= constants.THRESHOLD) | (humidity_Steam_Sensor_6 >= constants.THRESHOLD)) & (constants.START_TIME == 0):
            constants.START_TIME = updated_time
        if constants.START_TIME != 0:
            new_row = {'Time (min)':updated_time, 
                    'Steam Sensor 1 (Count)':analog_Steam_Sensor_1, 'Humidity 1 (%)':humidity_Steam_Sensor_1,
                    'Steam Sensor 2 (Count)':analog_Steam_Sensor_2, 'Humidity 2 (%)':humidity_Steam_Sensor_2, 
                    'Steam Sensor 3 (Count)':analog_Steam_Sensor_3, 'Humidity 3 (%)':humidity_Steam_Sensor_3, 
                    'Steam Sensor 4 (Count)':analog_Steam_Sensor_4, 'Humidity 4 (%)':humidity_Steam_Sensor_4,
                    'Steam Sensor 5 (Count)':analog_Steam_Sensor_5, 'Humidity 5 (%)':humidity_Steam_Sensor_5, 
                    'Steam Sensor 6 (Count)':analog_Steam_Sensor_6, 'Humidity 6 (%)':humidity_Steam_Sensor_6, 
                    'Steam Temp. (C)':self.read_temp(constants.TEMP_PROBE_SURR), 'Surrounding Temp. (C)':self.read_temp(constants.TEMP_PROBE_STEAM)}
            constants.df = constants.df.append(new_row, ignore_index = True)
    
    # Calculates the average steam sensor humidity
    def average_Steam_Sensor_Humidity(self):
        total = constants.df['Humidity 1 (%)'].sum() + constants.df['Humidity 2 (%)'].sum() + constants.df['Humidity 3 (%)'].sum() + constants.df['Humidity 4 (%)'].sum() + constants.df['Humidity 5 (%)'].sum() + constants.df['Humidity 6 (%)'].sum()
        rows = len(constants.df.index)
        return total/(6*rows)

    # Calculates the average steam temperature
    def average_steam_temperature(self):
        return constants.df['Steam Temp. (C)'].mean()

    # Calculates the total steam accumulation number
    def steam_Accumulation(self):
        constants.df['Delta T (min)'] = abs(constants.df['Time (min)'].diff(periods=-1))
        constants.df['Steam Accumulation (Count * min)'] = (constants.df['Steam Sensor 1 (Count)'] * constants.df['Delta T (min)']) + (constants.df['Steam Sensor 2 (Count)'] * constants.df['Delta T (min)']) + (constants.df['Steam Sensor 3 (Count)'] * constants.df['Delta T (min)']) + (constants.df['Steam Sensor 4 (Count)'] * constants.df['Delta T (min)']) + (constants.df['Steam Sensor 5 (Count)'] * constants.df['Delta T (min)']) + (constants.df['Steam Sensor 6 (Count)'] * constants.df['Delta T (min)'])
        return constants.df['Steam Accumulation (Count * min)'].sum()

    # Reads in sensor data every 4 s and updates the dataframe with the 
    # additional data
    def record_data(self):
        try:
            constants.df = self.dataframe_Structure()
            ADC = ADS1256.ADS1256()
            ADC.ADS1256_init()
            while constants.UPDATED_TIME > 0:
                ADC_Value = ADC.ADS1256_GetAll()
                updated_time = constants.MONITOR_TIME/60 - constants.UPDATED_TIME/60
                self.update_Dataframe(updated_time, ADC_Value)
                time.sleep(2)

        except :
            GPIO.cleanup()
            exit()

    # Converts the steam sensor analog value to a percentage
    def to_Humidity(self, raw):
        return (raw/0x7fffff) * 100.00

    # Creates a dataframe for the user inputs 
    def input_to_df(self):
        input_dict = {'Steam Appliance':['Function', 'Food Load', 'Time Interval (min)', 'Cook Time (min)', 'Sensor Height (in)', 'Initial Water Mass (g)', 'Initial Food Mass (g)',
                        'Final Water Mass (g)', 'Final Food Mass (g)', 'Water Loss (g)','Average Steam Sensor Humidity (%)', 'Steam Accumulation (Count * min)', 'Average Steam Temperature (C)'],
                        constants.STEAM_APPLIANCE: [constants.FUNCTION, constants.FOOD_LOAD, constants.TIME_INTERVAL, constants.MONITOR_TIME/60, constants.SENSOR_HEIGHT, constants.INITIAL_WATER_MASS, 
                        constants.INITIAL_FOOD_MASS, constants.FINAL_WATER_MASS, constants.FINAL_FOOD_MASS, constants.WATER_LOSS, constants.STEAM_SENSOR_HUMIDITY, constants.STEAM_ACCUMULATION, 
                        self.average_steam_temperature()] }
        input_df = pd.DataFrame(input_dict)
        return input_df

    # Converts all steam sensor analog values to percentages
    def all_Sensors_to_humidity(self, ADC_Value):
        analog_Steam_Sensor_1 = ADC_Value[constants.STEAM_SENSOR1]
        analog_Steam_Sensor_2 = ADC_Value[constants.STEAM_SENSOR2]
        analog_Steam_Sensor_3 = ADC_Value[constants.STEAM_SENSOR3]
        analog_Steam_Sensor_4 = ADC_Value[constants.STEAM_SENSOR4]
        analog_Steam_Sensor_5 = ADC_Value[constants.STEAM_SENSOR5]
        analog_Steam_Sensor_6 = ADC_Value[constants.STEAM_SENSOR6]
        humidity_Steam_Sensor_1 = self.to_Humidity(analog_Steam_Sensor_1)
        humidity_Steam_Sensor_2 = self.to_Humidity(analog_Steam_Sensor_2)
        humidity_Steam_Sensor_3 = self.to_Humidity(analog_Steam_Sensor_3)
        humidity_Steam_Sensor_4 = self.to_Humidity(analog_Steam_Sensor_4)
        humidity_Steam_Sensor_5 = self.to_Humidity(analog_Steam_Sensor_5)
        humidity_Steam_Sensor_6 = self.to_Humidity(analog_Steam_Sensor_6)
        return humidity_Steam_Sensor_1, humidity_Steam_Sensor_2, humidity_Steam_Sensor_3, humidity_Steam_Sensor_4, humidity_Steam_Sensor_5, humidity_Steam_Sensor_6

    # Checks that the steam sensors readings are below the sensor threshold inputted
    def check_Sensors(self):
        try:
            ADC = ADS1256.ADS1256()
            ADC.ADS1256_init()
            ADC_Value = ADC.ADS1256_GetAll()
            time.sleep(.5)
            ADC_Value = ADC.ADS1256_GetAll() 
            humidity_Steam_Sensor_1, humidity_Steam_Sensor_2, humidity_Steam_Sensor_3, humidity_Steam_Sensor_4, humidity_Steam_Sensor_5, humidity_Steam_Sensor_6 = self.all_Sensors_to_humidity(ADC_Value)

            if ((humidity_Steam_Sensor_1 > constants.THRESHOLD) | (humidity_Steam_Sensor_2 > constants.THRESHOLD) | (humidity_Steam_Sensor_3 > constants.THRESHOLD) | (humidity_Steam_Sensor_4 > constants.THRESHOLD) | (humidity_Steam_Sensor_5 > constants.THRESHOLD) | (humidity_Steam_Sensor_6 > constants.THRESHOLD)):
                return False

            return True

        except :
            GPIO.cleanup()
            exit()

# A class to hold the external graph window
class MplCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(MplCanvas, self).__init__(self.fig)

# A class to graph the dataframe data to an external window
class GraphWindow(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.resize(750, 500)
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
        self.setObjectName("GraphWindow")

        sc, derivative_time  = self.graph()
        self.derivative_time = derivative_time
        layout = QtWidgets.QVBoxLayout()
        toolbar = NavigationToolbar2QT(sc, self)
        layout.addWidget(toolbar)
        layout.addWidget(sc)

        self.setLayout(layout)
        self.retranslateUi()
        
    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("GraphWindow", "Graphs"))

    # Plots the time vs humidity graph on the figure
    def humidity_Graph(self, sc, time, humidity1, humidity2, humidity3, humidity4, humidity5, humidity6):
        plot2 = sc.fig.add_subplot(312, ylabel = 'Humidity (%)', title = 'Time vs. Steam Sensor Humidity')
        plot2.plot(time, humidity1, label='Humidity 1')
        plot2.plot(time, humidity2, label='Humidity 2')
        plot2.plot(time, humidity3, label='Humidity 3')
        plot2.plot(time, humidity4, label='Humidity 4')
        plot2.plot(time, humidity5, label='Humidity 5')
        plot2.plot(time, humidity6, label='Humidity 6')
        box = plot2.get_position()
        plot2.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        plot2.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    # Plots the time vs steam accumulation graph on the figure
    def steam_Accumulation_Graph(self, sc, time, steamAccumulation):
        plot1 = sc.fig.add_subplot(311, ylabel ='Steam Accum. (Count * min)', title = 'Time vs. Steam Accumulation')
        start_Interval = time[0]
        end_Interval = start_Interval + constants.TIME_INTERVAL
        derivative_time = dict()
        while start_Interval < constants.MONITOR_TIME:
            df2 = constants.df.loc[(time >= start_Interval) & (time <= end_Interval)]
            x = df2['Time (min)']
            y = df2['Steam Accumulation (Count * min)']
            if not x.empty and not y.empty:
                m,b = np.polyfit(x,y,1)
                plot1.plot(x,y,'ro')
                plot1.plot(x, m*x+b)
                derivative_time[m] = start_Interval
            start_Interval = end_Interval
            end_Interval = start_Interval + constants.TIME_INTERVAL
        plot1.plot(time, steamAccumulation)
        box = plot1.get_position()
        plot1.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        return derivative_time

    # Plots the time vs surrounding temp vs steam temp graph on the figure
    def temperature_Graph(self, sc, time, surrTemp, steamTemp):
        plot3 = sc.fig.add_subplot(313, xlabel = 'Time (min)', ylabel='Temperature (C)', title = 'Time vs. Steam Temperature vs Surrounding Temperature')
        plot3.plot(time, surrTemp, label='Surrounding Temp')
        plot3.plot(time, steamTemp, label='Steam Temp')
        box = plot3.get_position()
        plot3.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        plot3.legend(loc='center left', bbox_to_anchor=(1, 0.5))
  
    # Plots all three graphs on the figure
    def graph(self):
        sc = MplCanvas(self, width=5, height=4, dpi=100)

        time = constants.df['Time (min)']
        humidity1 = constants.df['Humidity 1 (%)']
        humidity2 = constants.df['Humidity 2 (%)']
        humidity3 = constants.df['Humidity 3 (%)']
        humidity4 = constants.df['Humidity 4 (%)']
        humidity5 = constants.df['Humidity 5 (%)']
        humidity6 = constants.df['Humidity 6 (%)']
        steamAccumulation = constants.df['Steam Accumulation (Count * min)']
        surrTemp = constants.df['Surrounding Temp. (C)']
        steamTemp = constants.df['Steam Temp. (C)']
          
        derivative_time = self.steam_Accumulation_Graph(sc, time, steamAccumulation)
        self.humidity_Graph(sc, time, humidity1, humidity2, humidity3, humidity4, humidity5, humidity6)
        self.temperature_Graph(sc, time, surrTemp, steamTemp)

        return sc, derivative_time
    
    