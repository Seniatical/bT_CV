"""
Main.py -> Runs the bot

Simple :D
"""
from core.bot import bT_CV
from core.loggers import setupLoggers
from web import start

inst = bT_CV()
setupLoggers()
start()

inst.run()
