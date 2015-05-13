#!/usr/bin/python

""" Contains common utility functions to be used internally """
import logging

log = logging.getLogger(__name__)

# set Log Level
log.setLevel(logging.DEBUG)


# Set Stream Handler
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# set Formatter
formatter = logging.Formatter('%(asctime)s - %(filename)s:%(funcName)s:%(lineno)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

log.addHandler(handler)
log.propagate = False
