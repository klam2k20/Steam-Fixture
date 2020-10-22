import matplotlib.pyplot as plt
import os
import time
import glob
import smtplib
import ADS1256
import Adafruit_DHT
import RPi.GPIO as GPIO
import csv
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

#------------------------------------------------------------------ CONSTANTS & VARIABLES ------------------------------------------------------------------
DISTANCE_FROM_SENSOR = 0
NUMBER_OF_STEAM_SENSORS = 3
INITIAL_MASS = 0
FINAL_MASS = 0
FOOD_INPUTTED = ''
COOKING_TIME = 0

STEAM_SENSOR1 = 6
STEAM_SENSOR2 = 5
STEAM_SENSOR3 = 4
TEMP_PROBE_STEAM = '28-03049779ac6a'
TEMP_PROBE_SURR = '28-03049779d2c1'
HUMIDITY = Adafruit_DHT.DHT11
HUMIDITY_SENSOR = 16

EMAIL_SEND = "rtesting708@gmail.com"
EMAIL_RECEIVE = "etesting604@gmail.com"
EMAIL_PASSWORD = "Poohbear1!"
 
DATE = time.ctime().split(' ')
PREVIOUS_SURR_HUM = 0

#-------------------------------------------------------------- SENSOR READING FUNCTIONS -------------------------------------------------------------------
def read_humidity(DHT_object, DHT_pin):
    global PREVIOUS_SURR_HUM
    surr_humidity, surr_temp = Adafruit_DHT.read(DHT_object, DHT_pin)
    if surr_humidity is not None:
        PREVIOUS_SURR_HUM = surr_humidity
        return surr_humidity
    else:
        return PREVIOUS_SURR_HUM

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
def email_send(fileName):
    global EMAIL_SEND, EMAIL_RECEIVE, EMAIL_PASSWORD
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

#--------------------------------------------------------------------- CSV FUNCTIONS -----------------------------------------------------------------------
def new_Dir():
    global DATE
    path = os.getcwd() + '/' + 'RAW DATA' 
    file_path = path + "/" + DATE[1] + DATE[2] + DATE[4]
    if not os.path.exists(path):
        os.mkdir(path)
        os.mkdir(file_path)
    elif not os.path.exists(file_path):
        os.mkdir(file_path)
    os.chdir(file_path)
        

def new_CSV(counter):
    global FOOD_INPUTTED, DISTANCE_FROM_SENSOR
    return 'STEAM_SENSOR_FIXTURE_' + FOOD_INPUTTED + '_' +  str(DISTANCE_FROM_SENSOR) + 'in_' + str(counter) + '.csv'

def setup_CSV(fileName):
    global DISTANCE_FROM_SENSOR
    f = open(fileName, "w+")
    fWriter = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    fWriter.writerow([
        'Time (s)', 'Steam Sensor 1 (Count)', 'Humidity 1 (%)','Steam Sensor 2 (Count)', 'Humidity 2 (%)', 'Steam Sensor 3 (Count)', 'Humidity 3 (%)', 
        'Steam Temp. (C)', 'Surrounding Humidity (%)', 'Surrounding Temp. (C)'])
    return f,fWriter

def write_CSV(fWriter, deltaTime, ADC_Value):
    global TEMP_PROBE_STEAM, TEMP_PROBE_SURR, STEAM_SENSOR1, STEAM_SENSOR2, STEAM_SENSOR3, HUMIDITY_SENSOR, HUMIDITY
    surr_humidity = read_humidity(HUMIDITY, HUMIDITY_SENSOR)
    fWriter.writerow([
                    "{:.2f}".format(deltaTime),ADC_Value[STEAM_SENSOR1],to_Humidity(ADC_Value[STEAM_SENSOR1]),
                     ADC_Value[STEAM_SENSOR2],to_Humidity(ADC_Value[STEAM_SENSOR2]),
                     ADC_Value[STEAM_SENSOR3],to_Humidity(ADC_Value[STEAM_SENSOR3]),
                    read_temp(TEMP_PROBE_STEAM), surr_humidity, read_temp(TEMP_PROBE_SURR)])

#--------------------------------------------------------------------- HELPER FUNCTIONS --------------------------------------------------------------------
def update_Delta_Time(start):
    currentTime = time.time()
    deltaTime = currentTime - start
    return deltaTime

def to_Humidity(raw):
    return raw/0x7fffff

#----------------------------------------------------------------- DATAFRAME FUNCTION -------------------------------------------------------------------
def average_Steam_Sensor_Humidity(df):
    total = df['Humidity 1 (%)'].sum() + df['Humidity 2 (%)'].sum() + df['Humidity 3 (%)'].sum()
    rows = len(df.index)
    return total/(3*rows) * 100

def average_steam_temperature(df):
    return df['Steam Temp. (C)'].mean()

def average_surrounding_humidity(df):
    return df['Surrounding Humidity (%)'].mean()

def average_surrounding_temperature(df):
    return df['Surrounding Temp. (C)'].mean()
    
def steam_Accumulation(df):
     df['Delta T (s)'] = abs(df['Time (s)'].diff(periods=-1))
     df['Steam Accumulation (Count * s)'] = (df['Steam Sensor 1 (Count)'] * df['Delta T (s)']) + (df['Steam Sensor 2 (Count)'] * df['Delta T (s)']) + (df['Steam Sensor 3 (Count)'] * df['Delta T (s)'])
     return df['Steam Accumulation (Count * s)'].sum()

#----------------------------------------------------------------- GRAPH FUNCTION -------------------------------------------------------------------
def humidity_Graph(df):
    plt.plot('Time (s)', 'Humidity 1 (%)', data = df, color = 'red')
    plt.plot('Time (s)', 'Humidity 2 (%)', data = df, color = 'black')
    plt.plot('Time (s)', 'Humidity 3 (%)', data = df, color = 'blue')
    plt.plot('Time (s)', 'Surrounding Humidity (%)', data = df, color = 'orange')
    plt.xlabel('Time (s)')
    plt.ylabel('Humidity (%)')
    plt.title('Time vs. Steam Sensor\'s Humidity vs Surrounding Humidity')
    plt.legend()

def steam_Accumulation_Graph(df):
    plt.plot('Time (s)', 'Steam Accumulation (Count * s)', data = df, color = 'red')
    plt.xlabel('Time (s)')
    plt.ylabel('Steam Accumulation (Count * s)')
    plt.title('Time vs. Steam Accumulation')

def temperature_Graph(df):
    plt.plot('Time (s)', 'Steam Temp. (C)', data = df, color = 'red')
    plt.plot('Time (s)', 'Surrounding Temp. (C)', data = df, color = 'blue')
    plt.xlabel('Time (s)')
    plt.ylabel('Temperature (C)')
    plt.title('Time vs. Steam Temperature vs Surrounding Temperature')
    plt.legend()

def steam_Fixture_Graphs(df):
    plt.figure()
    plt.subplot(311)
    steam_Accumulation_Graph(df)

    plt.subplot(312)
    humidity_Graph(df)

    plt.subplot(313)
    temperature_Graph(df)

    plt.tight_layout()
    
#----------------------------------------------------------------- INPUT FUNCTIONS -------------------------------------------------------------------
def check_str(string):
    while 1:
        if type(string) == str:
            return string
        print('\n Input must be a string')

def check_non_negative(number):
    while 1:
        if (type(number) == float or type(number) == int) and (number >= 0):
            return number
        print('\n Input must be a non-negative value')

#----------------------------------------------------------------- MAIN FUNCTION -------------------------------------------------------------------
def main():
    global DISTANCE_FROM_SENSOR, FOOD_INPUTTED, COOKING_TIME, FINAL_MASS, INITIAL_MASS
    counter = 0
    new_Dir()
    while 1:
        FOOD_INPUTTED = check_str(input('Food: '))
        COOKING_TIME = check_non_negative(input('Cooking Time (s): '))
        DISTANCE_FROM_SENSOR = check_non_negative(input('Sensor Height (in): '))
        INITIAL_MASS = check_non_negative(input('Initial Mass (g):'))
        fileName = new_CSV(counter)
        print('Start Cooking')
        f, fWriter = setup_CSV(fileName)
        startTime = time.time()
        deltaTime = 0
        try:
            ADC = ADS1256.ADS1256()
            ADC.ADS1256_init()
            while (deltaTime < COOKING_TIME):
                ADC_Value = ADC.ADS1256_GetAll()
                deltaTime = update_Delta_Time(startTime)
                write_CSV(fWriter, deltaTime, ADC_Value)
                time.sleep(2)
            f.close()
            email_send(fileName)
            FINAL_MASS = check_non_negative(input('Final Mass (g):'))
            path = os.getcwd() + '/' + fileName
            df = pd.read_csv(path)
            average_Sensor_Humidity = average_Steam_Sensor_Humidity(df)
            steam_Accum = steam_Accumulation(df)
            print('Steam Accumulation - Steam Sensor Average Humidity: {0:.2f} - {1:.2f} %'.format(steam_Accum, average_Sensor_Humidity))
            print('Water Loss (g): {0:.2f}'.format(FINAL_MASS - INITIAL_MASS))
            steam_Fixture_Graphs(df)
            plt.show()
            counter = counter + 1
        except :
            GPIO.cleanup()
            print ("\r\nProgram end     ")
            exit()

if __name__ == "__main__":
    main()


