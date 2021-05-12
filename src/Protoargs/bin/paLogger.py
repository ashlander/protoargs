import os
import sys
import logging

'''Initialize logger'''
def init(level, logDir, logFilename='protoargs.log'):

    loggingLevel = logging.INFO;
    if level == "ERROR":
        loggingLevel = logging.ERROR
    if level == "WARNING":
        loggingLevel = logging.WARN
    if level == "INFO":
        loggingLevel = logging.INFO
    if level == "DEBUG":
        loggingLevel = logging.DEBUG

    logFormat = '%(asctime)s [%(threadName)-12.12s] %(filename)s:%(lineno)d [%(levelname)-5.5s] %(message)s'
    logging.basicConfig(filename=os.path.join(logDir,logFilename), level=loggingLevel, format=logFormat)

    logFormatter = logging.Formatter(logFormat)
    rootLogger = logging.getLogger()

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
