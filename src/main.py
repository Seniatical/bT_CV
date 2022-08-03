"""
Main.py -> Runs the bot

Simple :D
"""
from core.bot import bT_CV
from core.loggers import setupLoggers

inst = bT_CV()
setupLoggers()

inst.run()
