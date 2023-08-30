import os
import subprocess
from time import sleep, strftime
from RPLCD.i2c import CharLCD
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

LCD_WIDTH = 16
LCD_HEIGHT = 2
LCD_ADDRESS = 0x27  # Change this to the correct I2C address for your LCD (typically 0x27 or 0x3F)

lcd = CharLCD('PCF8574', LCD_ADDRESS)
lcd.clear()

class SongFileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == "/var/local/www/current_song.txt":
            update_display()

def get_song_info():
    try:
        with open("/var/local/www/current_song.txt", "r") as song_file:
            song_info = song_file.read().strip()
            return song_info
    except FileNotFoundError:
        return "No song info"

def scroll_text(text, lcd_row, lcd_col, delay=0.4):
    text = text + " " * LCD_WIDTH  # Add padding to ensure smooth scrolling
    for i in range(len(text) - LCD_WIDTH + 1):
        lcd.cursor_pos = (lcd_row, lcd_col)
        lcd.write_string(text[i:i + LCD_WIDTH])
        sleep(delay)

def update_display():
    song_info = get_song_info()
    current_time = strftime("%H:%M")
    
    # Scroll the song info if it's too long to fit
    if len(song_info) > LCD_WIDTH:
        scroll_text(song_info, 0, 0)
    else:
        lcd.cursor_pos = (0, 0)
        lcd.write_string(song_info)
    
    # Center the time on the second line
    time_col = max((LCD_WIDTH - len(current_time)) // 2, 0)
    lcd.cursor_pos = (1, time_col)
    lcd.write_string(current_time)

try:
    # Initial display update
    update_display()

    # Watch for changes to the song file
    event_handler = SongFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path="/var/local/www", recursive=False)
    observer.start()

    while True:
        sleep(1)  # Keep the script running

except KeyboardInterrupt:
    lcd.clear()
    lcd.close()
    observer.stop()
    observer.join()
