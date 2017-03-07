import abc

class abstract_instrument(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def __init__(self, address, vtype, channel):
        """Build the class"""
        return

    @abc.abstractmethod
    def model(self):
        """return the instrument model"""
        return

    @abc.abstractmethod
    def connect(self):
        """Create a connection with the instrument"""
        return

    @abc.abstractmethod
    def disconnect(self):
        """Disconnect the instrument"""
        return

    @abc.abstractmethod
    def configure(self):
        """Configure the instrument"""
        return

    @abc.abstractmethod
    def read(self):
        """read the buffer"""
        return

    @abc.abstractmethod
    def send(self):
        """send a command"""
        return

    @abc.abstractmethod
    def getValue(self):
        """return the value of measurment"""
        return
