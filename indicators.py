from dbintegration import DbCommands


class Indicators:

    def __init__(self):

        self.database = DbCommands()

    def get_indicator_value(self, indicator_id):

        indicator_value = self.database.get_indicator(indicator_id)

        return indicator_value


