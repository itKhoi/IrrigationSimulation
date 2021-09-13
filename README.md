# IrrigationSimulation

I used DHT from Adafruit in order to read the humidity and temperature from the
DHT11. For a good number of my readings, I would either get error or a humidity over 100%
which is impossible, so in order to fix this, I made a while loop that would take the reading until
a good reading was found each time I used the DHT. I would then display this value onto the
LCD using RPLCD which was just a simple command. The DHT11 read function would be
called every 55 seconds since it took around 5 seconds on average to get a good reading,
averaging out to a reading every minute and once a reading was taken, a counter would be
incremented until it hit 60 which meant an hour had passed. I implemented the one minute read
this way because sometimes it would take over 3 reads to get a good read. Another way I could
have implemented it was to have a time variable in order to count once 60 seconds had passed,
but I thought this would not be as good since the time to get a good reading varied by quite a bit.
Once the counter hit 60, an hourly function was called which used the ftp url provided by the
cimis website to read the Irvine station in order to get their hourly temperature, humidity, and eto
value. I used Irvine because all the centers near me on the CIMIS website said that the towers
were inactive and if they ever did come back online, it would be a simple change of numbers in
the code when typing the url to pull data from. The data was already parsed once I got it, so I just
had to read the README provided and index each line for the 3 measurements needed. Using
the three measurements, I calculated the amount of water needed to water the lawn based on my
local calculations and the tower calculations with the method provided in the appendix of the lab
procedure. I used a rolling text code provided by RPLCD in order to display this message so that
the long string of data could fit in one row. After this data was calculated, I used the rate of the
sprinklers which was provided to find out how long the sprinkler had to be turned on for that
hour and had the LCD just print “sprinkling” when the sprinkler was on. After it would go back
to the main function and begin taking DHT measurements every minute to begin the process
again.

Main functions: get_temp()- this function was the one called every minute which would take a
valid measurement from the DHT and display it on the LCD. Everytime it was called a counter
variable would be incremented and once counter==60, get_hourly() would be called.
get_hourly()- this function would take the url from the datasheet of the Irvine tower weather and
take the most recent temperature, humidity, and eto value. I calculated the eto value using the
linear derating method which was given. The number of gallons needed to water the
lawn was then calculated and divided by the rate of the sprinkler system to find how long to turn
on the sprinkler. All this information was put on a rolling message on the LCD. Additionally,
since we had to show the amount of water saved over a 24 hour period of time, I had this
function write the amount of water saved, water calculated by local, and water calculated by
Irvine tower into a csv file called results.csv which would start fresh every time the program ran.
loopstring()-This was just a function I got from the RPLCD github website which would display
scrolling text in order to fit a large string into one row.

Materials:
- DHT11
- Raspberry Pi 3
- 1x 10k ohm resistor

Connections to Raspberry Pi 3:
- DHT
    - VCC: Pin2 (5V)
    - Signal: Pin7 (GPIO4)
    - Resistor: Between VCC and signal
    - GND: Pin6
- LCD
    - VCC: Pin4 (5V)
    - GND: Pin14
    - SDA: Pin3 (SDA1)
    - SCL: Pin5 (SCL1)
Conclusion: My implementation of the circuit was able to successfully read temperature and
humidity and display these values onto the LCD along with hourly reports of the CIMIS tower
averages with my averages and calculated the amount of water needed per hour for both of these
cases. It also writes these results onto a csv file for convenience. I believe that I was able to
complete all the required tasks with my code.
