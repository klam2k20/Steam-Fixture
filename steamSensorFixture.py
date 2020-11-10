import matplotlib.pyplot as plt
import xlsxwriter
import os
import sys
import time
import glob
import smtplib
import ADS1256
import RPi.GPIO as GPIO
import math
import numpy as np
import pandas as pd
import constants

#-------------------------------------------------------------- SENSOR READING FUNCTIONS -------------------------------------------------------------------
def update_temp_id():
    try:
        mypath = '/sys/bus/w1/devices/'
        onlylinks = [f for f in os.listdir(mypath) if os.path.islink(os.path.join(mypath, f))]
        onlylinks.remove('w1_bus_master1')
        constants.TEMP_PROBE_SURR = str(onlylinks[0])
        constants.TEMP_PROBE_STEAM = str(onlylinks[1])
    except IndexError:
        print('Temperature probes are not correctly connected')

def read_temp_raw(id):
    base_dir = '/sys/bus/w1/devices/'
    thermo_file = glob.glob(base_dir + id)[0] + '/w1_slave'
    f = open(thermo_file, 'r')
    lines = f.readlines()
    f.close()
    return lines
 
def read_temp(id):
    lines = read_temp_raw(id)
    while lines[0].strip()[-3:] != 'YES':
        lines = read_temp_raw(id)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

#--------------------------------------------------------------------- DIRECTORY FUNCTION -----------------------------------------------------------------------
def new_Dir():
    DATE = time.ctime().split(' ')
    path1 = os.getcwd() + '/' + 'RAW DATA'
    path2 = path1 + "/" + DATE[1] + DATE[2]
    
    if not os.path.exists(path1):
        os.mkdir(path1)
        os.mkdir(path2)
    elif not os.path.exists(path2):
        os.mkdir(path2)
    
    onlylinks = [f for f in os.listdir(path2) if os.path.isdir(os.path.join(path2, f))]
    counter = len(onlylinks)
    file_path = path2 + "/" + str(counter)
    os.mkdir(file_path)
    os.chdir(file_path)
    
def reset_Dir():
    os.chdir(constants.START_PATH)
        
#--------------------------------------------------------------------- EXCEL FUNCTION -----------------------------------------------------------------------
def excel_FileName():
    return 'Steam_Fixture_RAW_DATA.xlsx'

def dataframe_to_Excel(derivative_df):
    input_df = input_to_df()
    writer = pd.ExcelWriter(excel_FileName(), engine='xlsxwriter')
    constants.df.to_excel(writer, sheet_name= 'Raw_Data')
    input_df.to_excel(writer, sheet_name= 'Procedure_Results_Data')
    derivative_df.to_excel(writer, sheet_name= 'Top Derivative - Time')
    workbook = writer.book
    worksheet = workbook.add_worksheet('Graphs')
    worksheet.insert_image(0,0,'Steam_Fixture_Graphs.png')
    writer.save()
#--------------------------------------------------------------------- HELPER FUNCTIONS --------------------------------------------------------------------
def to_Humidity(raw):
    return (raw/0x7fffff) * 100.00

def input_to_df():
    input_dict = {'Steam Appliance':['Function', 'Food Load', 'Time Interval (min)', 'Cook Time (min)', 'Monitor Time (min)', 'Sensor Height (in)', 'Initial Water Mass (g)', 'Initial Food Mass (g)',
                    'Final Water Mass (g)', 'Final Food Mass (g)', 'Water Loss (g)','Average Steam Sensor Humidity (%)', 'Steam Accumulation (Count * min)', 'Average Steam Temperature (C)'],
                    constants.STEAM_APPLIANCE: [constants.FUNCTION, constants.FOOD_LOAD, constants.TIME_INTERVAL, constants.COOK_TIME, (constants.df.iloc[-1]['Time (min)'] - constants.df.iloc[0]['Time (min)']), constants.SENSOR_HEIGHT, constants.INITIAL_WATER_MASS, 
                    constants.INITIAL_FOOD_MASS, constants.FINAL_WATER_MASS, constants.FINAL_FOOD_MASS, constants.WATER_LOSS, constants.STEAM_SENSOR_HUMIDITY, constants.STEAM_ACCUMULATION, 
                    average_steam_temperature()] }
    input_df = pd.DataFrame(input_dict)
    return input_df

def check_Sensors():

    try:
        ADC = ADS1256.ADS1256()
        ADC.ADS1256_init()

        for i in range(10):
            ADC_Value = ADC.ADS1256_GetAll()
            analog_Steam_Sensor_1 = ADC_Value[constants.STEAM_SENSOR1]
            analog_Steam_Sensor_2 = ADC_Value[constants.STEAM_SENSOR2]
            analog_Steam_Sensor_3 = ADC_Value[constants.STEAM_SENSOR3]
            humidity_Steam_Sensor_1 = to_Humidity(analog_Steam_Sensor_1)
            humidity_Steam_Sensor_2 = to_Humidity(analog_Steam_Sensor_2)
            humidity_Steam_Sensor_3 = to_Humidity(analog_Steam_Sensor_3)
            
            if ((humidity_Steam_Sensor_1 > constants.THRESHOLD) | (humidity_Steam_Sensor_2 > constants.THRESHOLD) | (humidity_Steam_Sensor_3 > constants.THRESHOLD)):
                return False
        return True
    
    except :
        GPIO.cleanup()
        exit()

#----------------------------------------------------------------- DATAFRAME FUNCTION -------------------------------------------------------------------
def dataframe_Structure():
    columns = {'Time (min)':[], 'Steam Sensor 1 (Count)':[], 'Humidity 1 (%)':[],'Steam Sensor 2 (Count)':[], 'Humidity 2 (%)':[], 
            'Steam Sensor 3 (Count)':[], 'Humidity 3 (%)':[], 'Steam Temp. (C)':[], 'Surrounding Temp. (C)':[]}
    df = pd.DataFrame(columns)
    return df

def update_Dataframe(updated_time, ADC_Value):
    analog_Steam_Sensor_1 = ADC_Value[constants.STEAM_SENSOR1]
    analog_Steam_Sensor_2 = ADC_Value[constants.STEAM_SENSOR2]
    analog_Steam_Sensor_3 = ADC_Value[constants.STEAM_SENSOR3]
    humidity_Steam_Sensor_1 = to_Humidity(analog_Steam_Sensor_1)
    humidity_Steam_Sensor_2 = to_Humidity(analog_Steam_Sensor_2)
    humidity_Steam_Sensor_3 = to_Humidity(analog_Steam_Sensor_3)
    if ((humidity_Steam_Sensor_1 >= constants.THRESHOLD) | (humidity_Steam_Sensor_2 >= constants.THRESHOLD) | (humidity_Steam_Sensor_3 >= constants.THRESHOLD)) & (constants.START_TIME == 0):
        constants.START_TIME = updated_time
    if constants.START_TIME != 0:
        new_row = {'Time (min)':updated_time, 
                'Steam Sensor 1 (Count)':analog_Steam_Sensor_1, 'Humidity 1 (%)':humidity_Steam_Sensor_1,
                'Steam Sensor 2 (Count)':analog_Steam_Sensor_2, 'Humidity 2 (%)':humidity_Steam_Sensor_2, 
                'Steam Sensor 3 (Count)':analog_Steam_Sensor_3, 'Humidity 3 (%)':humidity_Steam_Sensor_3, 
                'Steam Temp. (C)':read_temp(constants.TEMP_PROBE_STEAM), 'Surrounding Temp. (C)':read_temp(constants.TEMP_PROBE_SURR)}
        constants.df = constants.df.append(new_row, ignore_index = True)
        
def average_Steam_Sensor_Humidity():
    total = constants.df['Humidity 1 (%)'].sum() + constants.df['Humidity 2 (%)'].sum() + constants.df['Humidity 3 (%)'].sum()
    rows = len(constants.df.index)
    return total/(3*rows)

def average_steam_temperature():
    return constants.df['Steam Temp. (C)'].mean()

def average_surrounding_humidity():
    return constants.df['Surrounding Humidity (%)'].mean()

def average_surrounding_temperature():
    return constants.df['Surrounding Temp. (C)'].mean()
    
def steam_Accumulation():
    constants.df['Delta T (min)'] = abs(constants.df['Time (min)'].diff(periods=-1))
    constants.df['Steam Accumulation (Count * min)'] = (constants.df['Steam Sensor 1 (Count)'] * constants.df['Delta T (min)']) + (constants.df['Steam Sensor 2 (Count)'] * constants.df['Delta T (min)']) + (constants.df['Steam Sensor 3 (Count)'] * constants.df['Delta T (min)'])
    return constants.df['Steam Accumulation (Count * min)'].sum()

def record_data():
    constants.STATE = True
    update_temp_id()
    try:
        constants.df = dataframe_Structure()
        ADC = ADS1256.ADS1256()
        ADC.ADS1256_init()
        while constants.STATE:
            ADC_Value = ADC.ADS1256_GetAll()
            updated_time = constants.MONITOR_TIME/60
            update_Dataframe(updated_time, ADC_Value)
            time.sleep(2)
    except :
        GPIO.cleanup()
        print ("\r\nProgram end     ")
        exit()

#----------------------------------------------------------------- GRAPH FUNCTION -------------------------------------------------------------------
def humidity_Graph():
    plt.plot('Time (min)', 'Humidity 1 (%)', data = constants.df, color = 'red')
    plt.plot('Time (min)', 'Humidity 2 (%)', data = constants.df, color = 'black')
    plt.plot('Time (min)', 'Humidity 3 (%)', data = constants.df, color = 'blue')
    plt.xlabel('Time (min)')
    plt.ylabel('Humidity (%)')
    plt.title('Time vs. Steam Sensor\'s Humidity')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

def steam_Accumulation_Graph():
    start_Interval = constants.df.iloc[0]['Time (min)']
    end_Interval = start_Interval + constants.TIME_INTERVAL
    derivative_time = dict()
    while start_Interval < constants.MONITOR_TIME:
        df2 = constants.df.loc[(constants.df['Time (min)'] >= start_Interval) & (constants.df['Time (min)'] <= end_Interval)]
        x = df2['Time (min)']
        y = df2['Steam Accumulation (Count * min)']
        if not x.empty and not y.empty:
            m,b = np.polyfit(x,y,1)
            plt.plot(x,y,'ro')
            best_fit, = plt.plot(x, m*x+b)
            derivative_time[m] = start_Interval
        start_Interval = end_Interval
        end_Interval = start_Interval + constants.TIME_INTERVAL
    plt.plot('Time (min)', 'Steam Accumulation (Count * min)', 'o', data = constants.df, color = 'red')
    plt.xlabel('Time (min)')
    plt.ylabel('Steam Accum. (Count * min)')
    plt.title('Time vs. Steam Accumulation')
    return derivative_time

def temperature_Graph():
    plt.plot('Time (min)', 'Steam Temp. (C)', data = constants.df, color = 'red')
    plt.plot('Time (min)', 'Surrounding Temp. (C)', data = constants.df, color = 'blue')
    plt.xlabel('Time (min)')
    plt.ylabel('Temperature (C)')
    plt.title('Time vs. Steam Temperature vs Surrounding Temperature')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

def steam_Fixture_Graphs():
    plt.figure(num=None, figsize=(10, 10), dpi=80, facecolor='w', edgecolor='k')
    plt.subplot(311)
    derivative_time = steam_Accumulation_Graph()

    plt.subplot(312)
    humidity_Graph()

    plt.subplot(313)
    temperature_Graph()

    plt.tight_layout()
    return derivative_time
