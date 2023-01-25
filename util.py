import logging
import string

class Util:
    def __init__(self):
        self.__class_name = 'UTIL'
        self.logger       = logging.getLogger(self.__class_name)
        self.logger.info(self.__class_name.capitalize() + " object created.")

    def iToA(self, nr, base=10):
        "Convert the integer to string representing the nr in the given base"
        if nr == 0: return '0'
        
        tmp_list = []
        posIns   = 0
        digits   = string.digits + string.uppercase
        if nr < 0:
            nr = -nr
            tmp_list.append('-')
            posIns = 1
           
        while nr > 0:
            nr, lastDigit = divmod(nr, base)
            tmp_list.insert(posIns, digits[lastDigit])
            
        return ''.join(tmp_list)