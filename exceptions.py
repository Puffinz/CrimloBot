class SheetException(Exception):

  def __init__(self, field: str, user: str = None):
      self.field = field
      self.user = user
      self.message = 'Error - ' + field + ' is missing or invalid'
      if user:
        self.message += ' for user: ' + user
      self.message = '`' + self.message + '`'
      super().__init__(self.message)
