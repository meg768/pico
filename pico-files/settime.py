def setTime(timezone = 1):
    
    import ntptime, machine, utime, time
    
    ntptime.settime()

    rtc = machine.RTC()

    (year, month, day, hour, minute, second, weekday, yearday) = utime.localtime(utime.time() + 3600 * timezone)
    rtc.datetime((year, month, day, weekday, hour, minute, second, 0))
    time.sleep_ms(100)
    
    now = time.localtime()
    (year, month, day, hour, minute, second, weekday, yearday) = utime.localtime(utime.time())
    
    print('Local time is {year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}'.format(year = now[0], month = now[1], day = now[2], hour = now[3], minute = now[4]))




