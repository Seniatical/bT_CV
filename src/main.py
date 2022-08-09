"""
Main.py -> Runs the bot

Simple :D
"""
from core.bot import bT_CV
from core.loggers import setupLoggers
from web import start

# Any load funcs
from commands.compare import load_model
load_model()

inst = bT_CV()
setupLoggers()
start()

inst.run()
