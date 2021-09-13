import time
import Adafruit_DHT
import urllib.request
import codecs
import csv
from RPLCD.i2c import CharLCD

DHT_SENSOR=Adafruit_DHT.DHT11
DHT_PIN=4

lcd=CharLCD('PCF8574',0x27)

temp_sum=0;
humid_sum=0;
counter=0;
global_counter=0;
#empty textfile in beginning for fresh results
TEXTFILE=open("results.csv","w")
TEXTFILE.truncate()
TEXTFILE.close()
TEXTFILE=open("results.csv","w")
TEXTFILE.write("Local water use,CIMIS water use,Water Saved,counter\n")
TEXTFILE.close()

#code for scrolling text
framebuffer=['Hourly Result:',
             '',
             ]
def write_to_lcd(lcd,framebuffer,num_cols):
    lcd.home()
    for row in framebuffer:
        lcd.write_string(row.ljust(num_cols)[:num_cols])
        lcd.write_string('\r\n')
def loop_string(string,lcd,framebuffer,row,num_cols,delay=0.15):
    padding=' '*num_cols
    s=padding+string+padding
    for i in range(len(s)-num_cols+1):
        framebuffer[row]=s[i:i+num_cols]
        write_to_lcd(lcd,framebuffer,num_cols)
        time.sleep(delay)
#function that is called once an hour
def get_hourly():
    global temp_sum
    global humid_sum
    global counter
    global global_counter
    #getting hourly rates
    hourly_temp=temp_sum/60
    hourly_humid=humid_sum/60
    print("Averages: Temp={0:0.1f}C Humidity={1:0.01f}%".format(hourly_temp,hourly_humid))
    #need to get the station data
    ftp=urllib.request.urlopen("ftp://ftpcimis.water.ca.gov/pub2/hourly/hourly075.csv")
    csv_file=csv.reader(codecs.iterdecode(ftp,'utf-8'))
    #get most recent data for hourly
    #so need to go until we see a '--'
    for line in csv_file:
        if(line[14]=='--' or line[12]=='--' or line[4]=='--'):
            continue #this is an empty line so that means data is not good so BREAK
        else:
            ftp_eto=float(line[4])
            ftp_temperature=float(line[12])
            ftp_humidity=float(line[14])
    #calculating derating factor
    real_eto=ftp_eto #keep the original
    ftp_temperature=(ftp_temperature-32)/1.8
    #if eto is 0 and temp is higher and humid is lower
    if(ftp_eto==0.00000 and (hourly_temp>ftp_temperature or hourly_humid<ftp_humidity)):
        ftp_eto=.0001 #if its 0 then we need to make it small when printing
    #eto_temp=hourly_temp/ftp_temperature
    #temp should be swapped with humid because higher temp==more water
    eto_temp=ftp_temperature/hourly_temp
    
    eto_humidity=hourly_humid/ftp_humidity
    #i think im supposed to divied eto by both of these?
    ftp_eto=ftp_eto/eto_temp
    ftp_eto=ftp_eto/eto_humidity

    #calculate how much to water the lawn by
    #(eto x PF x SF x 0.62)/IE
    #print("ftp_eto={0:0.4f}".format(ftp_eto))
    gallons_per_day= (ftp_eto*1*40000*.62)/.75 #this is a given formula
    gallons_per_day2=(real_eto*1*40000*.62)/.75
    print("water needed today is {0:0.2f}".format(gallons_per_day))
    print("original water needed today is {0:0.2f}".format(gallons_per_day2))
    gallons_per_hour=gallons_per_day/24
    gallons_per_hour2=gallons_per_day2/24
    #currently needs to irrigate this much
    print("I must irrigate {0:0.2f} gallons of water now".format(gallons_per_hour))
    print("I was supposed to irrigate {0:0.2f} gallons of water now".format(gallons_per_hour2))
    lcd.cursor_pos=(0,0)
    long_string="Cimis: Avg temp={0:0.1f} Avg humidity={1:0.2f} ET value:{2:0.5f} ".format(ftp_temperature,ftp_humidity,real_eto)
    long_string2="Local: Avg temp={0:0.1f} Avg humidity={1:0.2f} ET value:{2:0.5f} ".format(hourly_temp,hourly_humid,ftp_eto)
    if(gallons_per_hour-gallons_per_hour2<0):
        gallon_diff=gallons_per_hour2-gallons_per_hour
        long_string3="  Saved {0:0.2f} gallons ".format(gallon_diff)
    elif(gallons_per_hour-gallons_per_hour2>0):
        gallon_diff=gallons_per_hour-gallons_per_hour2
        long_string3="  Used {0:0.2f} gallons extra".format(gallon_diff)
    else:
        long_string3="  Did not save or lose any water"
    long_string_final=long_string+long_string2+long_string3
    loop_string(long_string_final,lcd,framebuffer,1,16)
    lcd.clear()
    time.sleep(.5)
    #write to a file to save output
    khoi=gallons_per_hour2-gallons_per_hour
    with open('results.csv',mode='a') as TEXTFILE:
        TEXTFILE.write("{0:0.02f},{1:0.02f},{2:0.02f},{3:0.0f}\n".format(gallons_per_hour,gallons_per_hour2,khoi,global_counter))
    TEXTFILE.close()
    print("wrote in file global counter: {0:0.0f}".format(global_counter))
    
    #time to sprinkle
    if(gallons_per_hour==0):
        lcd.write_string("No sprinkle")
        time.sleep(2)
        lcd.clear()
    elif(gallons_per_hour>0):
        wait_time=gallons_per_hour/.2833333 #.283333 is the gallons per second
        lcd.write_string("Sprinkling water")
        lcd.cursor_pos=(1,0)
        swait_time="{0:0.2f}".format(wait_time)
        sprinkle_string=str(swait_time)+"sec"
        lcd.write_string(sprinkle_string)
        time.sleep(wait_time)
        lcd.clear()
        
    #reset variables
    global_counter+=1
    counter=0
    temp_sum=0
    humid_sum=0
    

    
def get_stats():
    global temp_sum
    global humid_sum
    #check if an hour as passed (cant be exact since have to wait for tech)
    global counter
    
    humidity,temperature=Adafruit_DHT.read(DHT_SENSOR,DHT_PIN)
    while(humidity is None or temperature is None or humidity>100):
        humidity,temperature=Adafruit_DHT.read(DHT_SENSOR,DHT_PIN)
        time.sleep(2)
    print("Temp={0:0.1f}C  Humidity={1:0.01f}%".format(temperature,humidity))
    string = "Temp={0:0.1f}C".format(temperature)
    string2= "Humidity={0:0.01f}%".format(humidity)
    #for calculating the average
    temp_sum+=temperature
    humid_sum+=humidity
    counter+=1
    print("Total temp={0:0.1f}C Humidity={1:0.01f}%".format(temp_sum,humid_sum))
    print("Count is:{0:0d}".format(counter))
    lcd.write_string(str(string))
    lcd.cursor_pos=(1,0)
    lcd.write_string(str(string2))
    time.sleep(2)
    lcd.clear();
    #testing with 10 first
    #change this to 60 for hourly cimis
    if(counter>=60):
        get_hourly()
    

try:
    while True:
        #change this to one minute for actual testing
        get_stats()
        time.sleep(55)
        
        
finally:
    lcd.clear()
