# Imports
from .globals import LOG_LEVEL
import os
from datetime import datetime
###################################################################################
# Purpose: Generate persistent log files for future review
###################################################################################


# Logger Class
class Logger:
    def __init__(self, filename="NO/FILENAME/NO-FILE-PASSED"):
        self.log_levels = {
            "NONE": 0,
            "DEBUG": 1,
            "INFO": 2,
            "WARNING": 3,
            "ERROR": 4,
            "CRITICAL": 5,
        }
        self.filename = filename.split("/")[-1] 
        try:
            self.level = self.log_levels[LOG_LEVEL if not os.getenv("LOG_LEVEL") else os.getenv("LOG_LEVEL")]
        except:
            print(f"{__file__} Logger init failure")

    def debug(self, message="", details=""):
        if 0 < self.level < 2:
            text1 = f"[DEBUG] {self.filename} {details}"
            text2 = f"{message}"
            print(text1)
            print(message, end="\n\n")
            self.write_to_file(text1)
            self.write_to_file(text2)

    def info(self, message="", details=""):
        if 0 < self.level < 3:
            text1 = f"[INFO] {self.filename} {details}"
            text2 = f"{message}"
            print(text1)
            print(message, end="\n\n")
            self.write_to_file(text1)
            self.write_to_file(text2)

    def warning(self, message="", details=""):
        if 0 < self.level < 4:
            text1 = f"[WARNING] {self.filename} {details}"
            text2 = f"{message}"
            print(text1)
            print(message, end="\n\n")
            self.write_to_file(text1)
            self.write_to_file(text2)

    def error(self, message="", details=""):
        if 0 < self.level < 5:
            text1 = f"[ERROR] {self.filename} {details}"
            text2 = f"{message}"
            print(text1)
            print(message, end="\n\n")
            self.write_to_file(text1)
            self.write_to_file(text2)

    def critical(self, message="", details=""):
        if 0 < self.level < 6:
            text1 = f"[CRITICAL] {self.filename} {details}"
            text2 = f"{message}"
            print(text1)
            print(text2, end="\n\n")
            self.write_to_file(text1)
            self.write_to_file(text2)

    @staticmethod
    def write_to_file(output):
        datetime_now = datetime.now()
        export_location = f"/var/log/{datetime_now.strftime('%Y%m%d')}-dashboard.log"
        with open(export_location, "a") as logging_file:
            logging_file.write(datetime_now.strftime('[%X:%f]') + " " + output + '\n')
            logging_file.close()
