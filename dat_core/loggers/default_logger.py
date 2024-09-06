from dat_core.pydantic_models import DatLogMessage, DatMessage, Type, Level

class DefaultLogger:
    """
    Singleton class for logging messages with various levels of severity. This logger ensures that 
    all log messages are output in a consistent format using the DatMessage and DatLogMessage models.
    
    The logger supports multiple log levels:
    - INFO
    - DEBUG
    - ERROR
    - WARNING
    - TRACE
    - FATAL
    - CRITICAL
    
    This class is implemented as a singleton, meaning only one instance of DefaultLogger will 
    exist throughout the lifetime of the application.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures only one instance of DefaultLogger is created. If an instance already exists, 
        it returns the existing instance.
        """
        if cls._instance is None:
            cls._instance = super(DefaultLogger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def info(self, msg: str) -> None:
        """
        Logs a message at the INFO level.
        
        Args:
            msg (str): The message to be logged.
        """
        _msg = DatMessage(
            type=Type.LOG,
            log=DatLogMessage(
                level=Level.INFO,
                message=msg
            )
        )
        print(_msg.model_dump_json(), flush=True)

    def debug(self, msg: str) -> None:
        """
        Logs a message at the DEBUG level.
        
        Args:
            msg (str): The message to be logged.
        """
        _msg = DatMessage(
            type=Type.LOG,
            log=DatLogMessage(
                level=Level.DEBUG,  # Adjusted level to DEBUG
                message=msg
            )
        )
        print(_msg.model_dump_json(), flush=True)

    def error(self, msg: str) -> None:
        """
        Logs a message at the ERROR level.
        
        Args:
            msg (str): The message to be logged.
        """
        _msg = DatMessage(
            type=Type.LOG,
            log=DatLogMessage(
                level=Level.ERROR,  # Adjusted level to ERROR
                message=msg
            )
        )
        print(_msg.model_dump_json(), flush=True)

    def warning(self, msg: str) -> None:
        """
        Logs a message at the WARNING level.
        
        Args:
            msg (str): The message to be logged.
        """
        _msg = DatMessage(
            type=Type.LOG,
            log=DatLogMessage(
                level=Level.WARNING,  # Adjusted level to WARNING
                message=msg
            )
        )
        print(_msg.model_dump_json(), flush=True)

    def trace(self, msg: str) -> None:
        """
        Logs a message at the TRACE level.
        
        Args:
            msg (str): The message to be logged.
        """
        _msg = DatMessage(
            type=Type.LOG,
            log=DatLogMessage(
                level=Level.TRACE,  # Adjusted level to TRACE
                message=msg
            )
        )
        print(_msg.model_dump_json(), flush=True)

    def fatal(self, msg: str) -> None:
        """
        Logs a message at the FATAL level.
        
        Args:
            msg (str): The message to be logged.
        """
        _msg = DatMessage(
            type=Type.LOG,
            log=DatLogMessage(
                level=Level.FATAL,  # Adjusted level to FATAL
                message=msg
            )
        )
        print(_msg.model_dump_json(), flush=True)

    def critical(self, msg: str) -> None:
        """
        Logs a message at the CRITICAL level. In DAT's context,
        FATAL and CRITICAL are same. So this is equivalent to fatal()
        
        Args:
            msg (str): The message to be logged.
        """
        _msg = DatMessage(
            type=Type.LOG,
            log=DatLogMessage(
                level=Level.FATAL,  # Adjusted level to FATAL
                message=msg
            )
        )
        print(_msg.model_dump_json(), flush=True)



# Use this object for logging in other modules
logger = DefaultLogger()
