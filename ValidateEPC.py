import logging

class Validate_EPC:
    def __init__(self):
        self.__class_name = 'ValidateEPC'
        self.logger       = logging.getLogger(self.__class_name)
        self.logger.info(self.__class_name.capitalize() + " object created.")

    def Validate(self,tag_id):
        ret=False
        if tag_id[:2] == "34":
            ret=True
        if tag_id[:2] == "91":
            ret=True
##        if tag_id[:4] == "DBAE":
##            ret=True
##        if tag_id[:4] == "DBAF":
##            ret=True
        return ret

    