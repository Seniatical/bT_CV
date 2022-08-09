import logging
import typing
import sys

command_logger = logging.getLogger("ct_commands")
database_logger = logging.getLogger("sqlite")
discord_logger = logging.getLogger("discord")
status_logger = logging.getLogger("bt_status")


def emit_logger(self):
    def emitter(record):
        try:
            msg = self.format(record)
            stream = self.stream
            # issue 35046: merged two stream.writes into one.
            stream.write((msg + self.terminator).encode("utf-8", errors="ignore").decode("utf-8", errors="ignore"))
            self.flush()
        except RecursionError:  # See issue 36272
            raise
        except Exception:
            pass
    return emitter


def pipeLoggerTo(logger: logging.Logger, pipe: typing.TextIO,
                 formatting="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                 ) -> None:
    """ Pipe a logger to an output source """
    if not pipe.writable():
        raise ValueError("Pipe provided cannot be written to")

    hndlr = logging.StreamHandler(pipe)
    hndlr.emit = emit_logger(hndlr)

    hndlr.setFormatter(logging.Formatter(formatting))
    logger.addHandler(hndlr)


def setupLoggers(*formatting: str):
    loggers = [
        [command_logger, "./src/logs/commands.log", *formatting],
        [database_logger, "./src/logs/database.log", *formatting],
        [discord_logger, "./src/logs/discord.log", *formatting],
        [status_logger, sys.stdout, *formatting]
    ]

    for logger in loggers:
        logger[0].setLevel(logging.DEBUG)
        logger[1] = open(logger[1], "a") if isinstance(logger[1], str) else logger[1]
        pipeLoggerTo(*logger)
