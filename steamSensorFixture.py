import matplotlib.pyplot as plt
import xlsxwriter
import os
import time
import glob
import smtplib
import ADS1256
import RPi.GPIO as GPIO
import csv
import numpy as np
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

#------------------------------------------------------------------ CONSTANTS & VARIABLES ------------------------------------------------------------------
STEAM_SENSOR1 = 6
STEAM_SENSOR2 = 5
STEAM_SENSOR3 = 4
TEMP_PROBE_STEAM = ''
TEMP_PROBE_SURR = ''

#-------------------------------------------------------------- SENSOR READING FUNCTIONS -------------------------------------------------------------------
def update_temp_id():
    global TEMP_PROBE_STEAM, TEMP_PROBE_SURR
    mypath = '/sys/bus/w1/devices/'
    onlylinks = [f for f in os.listdir(mypath) if os.path.islink(os.path.join(mypath, f))]
    onlylinks.remove('w1_bus_master1')
    TEMP_PROBE_SURR = str(onlylinks[0])
    TEMP_PROBE_STEAM = str(onlylinks[1])

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


#-------------------------------------------------------------------- EMAIL FUNCTIONS ----------------------------------------------------------------------
def email_Send(fileName, EMAIL_RECEIVE):
    EMAIL_SEND = "rtesting708@gmail.com"
    EMAIL_PASSWORD = "Poohbear1!"
    print("Sending email")
    subject =  fileName
    msg = MIMEMultipart()
    msg['From'] =  EMAIL_SEND
    msg['To'] =  EMAIL_RECEIVE
    msg['Subject'] = subject

    body = "Raw data from steam sensor test."
    msg.attach(MIMEText(body, 'plain'))

    attachment = open(fileName, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        "attachment; filename= " + fileName,
    )
    msg.attach(part)
    text = msg.as_string()

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.ehlo()
    server.login(EMAIL_SEND, EMAIL_PASSWORD)
    server.sendmail(EMAIL_SEND, EMAIL_RECEIVE, text)
    server.close()
    print("Email sent")

#--------------------------------------------------------------------- DIRECTORY FUNCTION -----------------------------------------------------------------------
def new_Dir():
    DATE = time.ctime().split(' ')
    path1 = os.getcwd() + '/' + 'RAW DATA'
    path2 = path1 + "/" + DATE[1] + DATE[2] + DATE[4]
    onlylinks = [f for f in os.listdir(path2) if os.path.isdir(os.path.join(path2, f))]
    counter = len(onlylinks)
    file_path = path2 + "/" + str(counter)
    
    if not os.path.exists(path1):
        os.mkdir(path1)
        os.mkdir(path2)
    elif not os.path.exists(path2):
        os.mkdir(path2)

    os.mkdir(file_path)
    os.chdir(file_path)
    return counter
        
#--------------------------------------------------------------------- EXCEL FUNCTION -----------------------------------------------------------------------
def excel_FileName(counter, SENSOR_HEIGHT):
    return 'Steam_Fixture_' + str(counter) + '.xlsx'

def dataframe_to_Excel(counter, df, average_Sensor_Humidity, steam_Accum, FOOD_LOAD, MONITOR_TIME, TIME_INTERVAL, SENSOR_HEIGHT, INITIAL_MASS, FINAL_MASS, STEAM_APPLIANCE, FUNCTION):
    input_df = input_to_df(df,FOOD_LOAD, MONITOR_TIME, TIME_INTERVAL, SENSOR_HEIGHT, INITIAL_MASS, FINAL_MASS, average_Sensor_Humidity, steam_Accum, STEAM_APPLIANCE, FUNCTION)
    writer = pd.ExcelWriter(excel_FileName(counter, SENSOR_HEIGHT), engine='xlsxwriter')
    df.to_excel(writer, sheet_name= 'Raw_Steam_Fixture_Data')
    input_df.to_excel(writer, sheet_name= 'Procedure_Results_Data')
    workbook = writer.book
    worksheet = workbook.add_worksheet('Graphs')
    worksheet.insert_image(0,0,'Steam_Fixture_Graphs.png')
    writer.save()
#--------------------------------------------------------------------- HELPER FUNCTIONS --------------------------------------------------------------------
def update_Delta_Time(start):
    currentTime = time.time()
    deltaTime = currentTime - start
    return deltaTime/60.0

def to_Humidity(raw):
    return (raw/0x7fffff) * 100.00

def format_best_fit_eq(m,b):
    return 'y = ' + '{0:.2f}'.format(m) + 'x +' + '{0:.2f}'.format(b)

def input_to_df(df, FOOD_LOAD, MONITOR_TIME, TIME_INTERVAL, SENSOR_HEIGHT, INITIAL_MASS, FINAL_MASS, average_Sensor_Humidity, steam_Accum, STEAM_APPLIANCE, FUNCTION):
    input_dict = {'Steam Appliance':['Function', 'Food Load', 'Cook Time (min)', 'Time Interval (min)', 'Sensor Height (in)', 'Initial Mass (g)', 'Final Mass (g)', 'Water Loss (g)',
                               'Average Steam Sensor Humidity (%)', 'Steam Accumulation (Count * min)', 'Average Steam Temperature (C)'],
                    STEAM_APPLIANCE: [FUNCTION, FOOD_LOAD, MONITOR_TIME, TIME_INTERVAL, SENSOR_HEIGHT, INITIAL_MASS, FINAL_MASS, INITIAL_MASS - FINAL_MASS,
                                         average_Sensor_Humidity, steam_Accum, average_steam_temperature(df)] }
    input_df = pd.DataFrame(input_dict)
    return input_df

def print_top10_derative(d):
    sorted_derative = sorted(d, reverse=True)
    dict_len = len(sorted_derative)
    counter = 1
    if  dict_len < 10:
        print('\n Top ' + str(dict_len) + ' steam slope spikes: ')
        for derative in sorted_derative:
            print('\n {0}. {1:.2f} (Count * min) @ {2:.2f} min'.format(counter, derative, d[derative]))
            counter += 1
    else:
        print('\n Top 10 steam slope spikes: ')
        for derative in sorted_derative[:10]:
            print('\n {0}. {1:.2f} @ {2:.2f} min'.format(counter, derative, d[derative]))
            counter += 1
#----------------------------------------------------------------- DATAFRAME FUNCTION -------------------------------------------------------------------
def dataframe_Structure():
    columns = {'Time (min)':[], 'Steam Sensor 1 (Count)':[], 'Humidity 1 (%)':[],'Steam Sensor 2 (Count)':[], 'Humidity 2 (%)':[], 
            'Steam Sensor 3 (Count)':[], 'Humidity 3 (%)':[], 'Steam Temp. (C)':[], 'Surrounding Temp. (C)':[]}
    df = pd.DataFrame(columns)
    return df

def update_Dataframe(deltaTime, ADC_Value, df):
    global TEMP_PROBE_STEAM, TEMP_PROBE_SURR, STEAM_SENSOR1, STEAM_SENSOR2, STEAM_SENSOR3
    new_row = {'Time (min)':deltaTime, 
                'Steam Sensor 1 (Count)':ADC_Value[STEAM_SENSOR1], 'Humidity 1 (%)':to_Humidity(ADC_Value[STEAM_SENSOR1]),
                'Steam Sensor 2 (Count)':ADC_Value[STEAM_SENSOR2], 'Humidity 2 (%)':to_Humidity(ADC_Value[STEAM_SENSOR2]), 
                'Steam Sensor 3 (Count)':ADC_Value[STEAM_SENSOR3], 'Humidity 3 (%)':to_Humidity(ADC_Value[STEAM_SENSOR3]), 
                'Steam Temp. (C)':read_temp(TEMP_PROBE_STEAM), 'Surrounding Temp. (C)':read_temp(TEMP_PROBE_SURR)}
    df = df.append(new_row, ignore_index = True)
    return df
                    
def average_Steam_Sensor_Humidity(df):
    total = df['Humidity 1 (%)'].sum() + df['Humidity 2 (%)'].sum() + df['Humidity 3 (%)'].sum()
    rows = len(df.index)
    return total/(3*rows)

def average_steam_temperature(df):
    return df['Steam Temp. (C)'].mean()

def average_surrounding_humidity(df):
    return df['Surrounding Humidity (%)'].mean()

def average_surrounding_temperature(df):
    return df['Surrounding Temp. (C)'].mean()
    
def steam_Accumulation(df):
    df['Delta T (min)'] = abs(df['Time (min)'].diff(periods=-1))
    df['Steam Accumulation (Count * min)'] = (df['Steam Sensor 1 (Count)'] * df['Delta T (min)']) + (df['Steam Sensor 2 (Count)'] * df['Delta T (min)']) + (df['Steam Sensor 3 (Count)'] * df['Delta T (min)'])
    return df['Steam Accumulation (Count * min)'].sum()

#----------------------------------------------------------------- GRAPH FUNCTION -------------------------------------------------------------------
def humidity_Graph(df):
    plt.plot('Time (min)', 'Humidity 1 (%)', data = df, color = 'red')
    plt.plot('Time (min)', 'Humidity 2 (%)', data = df, color = 'black')
    plt.plot('Time (min)', 'Humidity 3 (%)', data = df, color = 'blue')
    plt.xlabel('Time (min)')
    plt.ylabel('Humidity (%)')
    plt.title('Time vs. Steam Sensor\'s Humidity')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

def steam_Accumulation_Graph(df, time_interval, MONITOR_TIME):
    start_Interval = df.iloc[0]['Time (min)']
    end_Interval = start_Interval + time_interval
    legend = []
    label = []
    derative_time = dict()
    while start_Interval < MONITOR_TIME:
        df2 = df.loc[(df['Time (min)'] >= start_Interval) & (df['Time (min)'] <= end_Interval)]
        x = df2['Time (min)']
        y = df2['Steam Accumulation (Count * min)']
        m,b = np.polyfit(x,y,1)
        plt.plot(x,y,'ro')
        best_fit, = plt.plot(x, m*x+b)
        legend.append(best_fit,)
        label.append(format_best_fit_eq(m,b))
        derative_time[m] = start_Interval
        start_Interval = end_Interval
        end_Interval = start_Interval + time_interval
    plt.plot('Time (min)', 'Steam Accumulation (Count * min)', 'o', data = df, color = 'red')
    plt.xlabel('Time (min)')
    plt.ylabel('Steam Accum. (Count * min)')
    plt.title('Time vs. Steam Accumulation')
    #plt.legend(legend, label,loc='center left', bbox_to_anchor=(1, 0.5))
    return derative_time

def temperature_Graph(df):
    plt.plot('Time (min)', 'Steam Temp. (C)', data = df, color = 'red')
    plt.plot('Time (min)', 'Surrounding Temp. (C)', data = df, color = 'blue')
    plt.xlabel('Time (min)')
    plt.ylabel('Temperature (C)')
    plt.title('Time vs. Steam Temperature vs Surrounding Temperature')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

def steam_Fixture_Graphs(df,time_interval, MONITOR_TIME):
    plt.figure(num=None, figsize=(10, 10), dpi=80, facecolor='w', edgecolor='k')
    plt.subplot(311)
    derative_time = steam_Accumulation_Graph(df,time_interval,MONITOR_TIME)

    plt.subplot(312)
    humidity_Graph(df)

    plt.subplot(313)
    temperature_Graph(df)

    plt.tight_layout()
    return derative_time
    
#----------------------------------------------------------------- CHECK INPUT FUNCTIONS -------------------------------------------------------------------
def check_non_negative(num):
    return num > 0
    
def check_float(num):
    try:
        float(num)
        return True
    except ValueError:
        return False

def check_string_input(phrase):
    while 1:
        string = input(phrase).strip()
        if not check_float(string):
            return string
        else:
            print('Input must be a string value.')

def check_float_input(phrase):
    while 1:
        num = input(phrase).strip()
        if check_float(num) and check_non_negative(float(num)):
            return float(num)
        elif check_float(num) and not check_non_negative(float(num)):
            print('Input must be a positive value.')
        else:
            print('Input must be a float or integer.')

#----------------------------------------------------------------- MAIN FUNCTION -------------------------------------------------------------------
def main():
    counter = new_Dir()
    update_temp_id()
    TIME_INTERVAL = .5
    STEAM_APPLIANCE = input('Steam Appliance: ').strip()
    #EMAIL_RECEIVE = input('Email:').strip()
    
    FUNCTION = input('Function: ').strip()
    FOOD_LOAD = check_string_input('Food Load: ')
    MONITOR_TIME = check_float_input('Monitor Time (min): ')
    SENSOR_HEIGHT = check_float_input('Sensor Height (in): ')
    INITIAL_MASS = check_float_input('Initial Mass (g): ')
    
    try:
        df = dataframe_Structure()
        startTime = time.time()
        deltaTime = 0
        ADC = ADS1256.ADS1256()
        ADC.ADS1256_init()
        while (deltaTime < MONITOR_TIME):
            ADC_Value = ADC.ADS1256_GetAll()
            deltaTime = update_Delta_Time(startTime)
            df = update_Dataframe(deltaTime, ADC_Value, df)
            time.sleep(2)
        FINAL_MASS = check_float_input('Final Mass (g): ')
        average_Sensor_Humidity = average_Steam_Sensor_Humidity(df)
        steam_Accum = steam_Accumulation(df)
        derative_time = steam_Fixture_Graphs(df,TIME_INTERVAL, MONITOR_TIME)
        print('Water Loss (g): {0:.2f}'.format(INITIAL_MASS - FINAL_MASS))
        print('Steam Accumulation - Steam Sensor Average Humidity: {0:,.2f} - {1:.2f} %'.format(steam_Accum, average_Sensor_Humidity))
        print_top10_derative(derative_time)
        plt.savefig('Steam_Fixture_Graphs.png')
        dataframe_to_Excel(counter, df, average_Sensor_Humidity, steam_Accum, FOOD_LOAD, MONITOR_TIME, TIME_INTERVAL, SENSOR_HEIGHT, INITIAL_MASS, FINAL_MASS, STEAM_APPLIANCE, FUNCTION)
        #email_Send(excel_FileName(counter, SENSOR_HEIGHT), EMAIL_RECEIVE)
        plt.show()
    except :
        GPIO.cleanup()
        print ("\r\nProgram end     ")
        exit()

if __name__ == "__main__":
    main()


