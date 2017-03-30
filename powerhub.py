# PowerHub - Set Power Plugs ON / OFF based upon time of day overridden by sun rise, sun set, and whether the TV is ON

import os
from datetime import date, timedelta, time, datetime, tzinfo
import math, pytz


def is_BST ():
    # Is today the same offset as Jan 1
    x = datetime(datetime.now().year, 1, 1, 0, 0, 0, tzinfo=pytz.timezone('Europe/London')) # Jan 1 of this year
    y = datetime.now(pytz.timezone('Europe/London'))

    # if BST is in effect, their offsets will be different
    return not (y.utcoffset() == x.utcoffset())


def TVisON():
    # Check if TV is turned on (will be on LAN if it is)
    response = os.system("ping -c 1 -t 2 192.168.1.80 > /dev/null")
    if response == 0:
        print ( "TV ONLINE" )
        return True
    else:
        print ( "TV OFFLINE")
        return False


def sinrad(deg):
    return math.sin(deg * math.pi/180)

def cosrad(deg):
    return math.cos(deg * math.pi/180)

def calculatetimefromjuliandate(jd):
    jd=jd+.5
    secs=int((jd-int(jd))*24*60*60+.5)
    mins=int(secs/60)
    hour=int(mins/60)  
    return time(hour, mins % 60, secs % 60, tzinfo=pytz.timezone('Europe/London'))
    
def calcsunriseandsunset(dt):
    a=math.floor((14-dt.month)/12)
    y = dt.year+4800-a
    m = dt.month+12*a -3
    julian_date=dt.day+math.floor((153*m+2)/5)+365*y+math.floor(y/4)-math.floor(y/100)+math.floor(y/400)-32045
    
    nstar= (julian_date - 2451545.0 - 0.0009)-(longitude/360)
    n=round(nstar)
    jstar = 2451545.0+0.0009+(longitude/360) + n
    M=(357.5291+0.98560028*(jstar-2451545)) % 360
    c=(1.9148*sinrad(M))+(0.0200*sinrad(2*M))+(0.0003*sinrad(3*M))
    l=(M+102.9372+c+180) % 360
    jtransit = jstar + (0.0053 * sinrad(M)) - (0.0069 * sinrad(2 * l))
    delta=math.asin(sinrad(l) * sinrad(23.45))*180/math.pi
    H = math.acos((sinrad(-0.83)-sinrad(latitude)*sinrad(delta))/(cosrad(latitude)*cosrad(delta)))*180/math.pi
    jstarstar=2451545.0+0.0009+((H+longitude)/360)+n
    jset=jstarstar+(0.0053*sinrad(M))-(0.0069*sinrad(2*l))
    jrise=jtransit-(jset-jtransit)
    return (calculatetimefromjuliandate(jrise), calculatetimefromjuliandate(jset))

    
longitude=3.1355 #West
latitude=51.8565  #North
seven_am = datetime.combine(datetime.now().date(),time( 7, 0, 0 ) , tzinfo= pytz.timezone('Europe/London'))
eight_am = datetime.combine(datetime.now().date(),time( 8, 0, 0 ) , tzinfo= pytz.timezone('Europe/London'))
four_pm = datetime.combine(datetime.now().date(),time( 16, 0, 0 ) , tzinfo= pytz.timezone('Europe/London'))
eleven_pm = datetime.combine(datetime.now().date(),time( 23, 0, 0 ) , tzinfo= pytz.timezone('Europe/London'))


def main():
    #Default light settings
    LIGHTS_ON=False
    LEDS_ON=False

    # get today's sunrise and sunset times, these are used to determined light ON/OFF schedule
    today=date.today()
    current_time =  datetime.now(tz= pytz.timezone('Europe/London'))
    #datetime.now( tz = pytz.timezone('Europe/London'))

    print ( "Current Time:",current_time )
    rise,sset = calcsunriseandsunset(today)
    sunrise = datetime.combine(datetime.now().date(),rise, tzinfo= pytz.timezone('Europe/London'))
    sunset = datetime.combine(datetime.now().date(),sset, tzinfo= pytz.timezone('Europe/London'))

    print ( "Sunrise:",sunrise,"\nSunSet :", sunset )
   
    if is_BST():
        print ( "Add an hour for BST" )
        sunrise = sunrise + timedelta(hours=1)
        sunset  = sunset  + timedelta(hours=1)
        print ( "Adjusted Sunrise:",sunrise,"\nAdjusted SunSet :", sunset )



    # Lights and LEDS on if the time is after 7am and before Sunrise
    if ( current_time > seven_am and current_time < eight_am ):
        print ( "It is past 7am and before 8am" )
        LIGHTS_ON = True
        LEDS_ON = True
    else:
        print ( "It is before 7am or after 8am" )

    # Lights off if is is after 11pm and the TV is OFF
    if ( current_time > eleven_pm ):
        print (" It is After 11")
        if TVisON():
            print ( "It is past 11pm BUT the TV is still on" )
            LIGHTS_ON = True
            LEDS_ON = True
    else:
        print ( "It is before 11pm" )
        if ( current_time > sunset ):
            print( "It is AFTER sunset")
            LIGHTS_ON = True
            LEDS_ON = True
        else:
            print ("It is before sunset")


    if LIGHTS_ON:
        print( "Lights: ON" )
    else:
        print( "Lights: OFF" )


    if LEDS_ON:
        print( "LEDs: ON")
    else:
        print( "LEDs: OFF") 




if __name__ == '__main__':
    main()



# Get Sunset and Sunrise


# Lights have a default schedule for evenings, Sunset -> 11pm.
# if the TV is on when the lights are scheduled to go off,
# keep them on, we're obviously staying up late watching something 


