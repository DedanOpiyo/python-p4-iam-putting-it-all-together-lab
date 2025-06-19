class APIException(Exception): # Subclass Exception to extend/augment/enrich/customize its behavior
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message) # Optionall. Store in python's Exception - for str(e), logging etc. work correctly
        self._errors = None
        self.errors = message # Trigger setter
        self.status_code = status_code or self.status_code
        self.payload = payload or {}

    @property
    def errors(self):
        return self._errors
    
    @errors.setter
    def errors(self, message):
        if isinstance(message, list):
            self._errors = message
        elif message:
            self._errors = [message]
        else:
            self._errors = ["An unknown error occured."]
        

    def to_dict(self):
        response_dict = dict(self.payload) # Copy payload
        response_dict['errors'] = self.errors # Response_dic to always have this attr       
        return response_dict