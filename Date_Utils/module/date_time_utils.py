import datetime
import time
import calendar


class Date_Utils:
        def __init__(self, date_optional=None) -> None:        
                months = {
                        1: "january",
                        2:"february",
                        3:"march",
                        4:"april",
                        5:"may",
                        6:"june",
                        7:"july",
                        8:"august",
                        9:"september",
                        10:"october",
                        11:"november",
                        12:"december"
                        }
                self.date_optional = date_optional
                self.period_setted = dict()

        def return_period(self):
                """
                Asks the user to select a time period, with a start date and an end date.

                Arguments:
                        date_array (list, optional): A list containing the start date and the end date in the format of string ('dd/mm/yyyy' HH:MM:SS).

                Returns:
                        list: A list containing the datetime objects of the selected start and end dates.

                Example:
                        >>> return_period()
                        Enter the start date in dd/mm/yyyy format: 01/01/2023
                        Enter the end date in dd/mm/yyyy format: 31/01/2023
                        [datetime.datetime(2023, 1, 1, 0, 0), datetime.datetime(2023, 1, 31, 23, 59, 59)]
                """

                def loop_data():
                        """
                Requests the user to select a time period, with a start date and an end date.

                Returns:
                        dict: A dictionary containing information about the start date and the end date, including month, day, year,
                        parsed dates, and Unix time.

                Example:
                        >>> loop_data()
                        Enter the start date in dd/mm/yyyy format: 01/01/2023
                        Enter the end date in dd/mm/yyyy format: 31/01/2023
                        {
                        "start_date": {
                                "month": "January",
                                "num_month": "1",
                                "day": "1",
                                "year": "2023",
                                "date_parsed_": "01_01_2023",
                                "date_parsed": "01/01/2023",
                                "unix_time": "timestamp_unix"
                        },
                        "final_date": {
                                "month": "January",
                                "num_month": "1",
                                "day": "31",
                                "year": "2023",
                                "date_parsed_": "31_01_2023",
                                "date_parsed": "31/01/2023",
                                "unix_time": "timestamp_unix"
                        }
                        }
                        """

                        while True:
                                if self.date_optional == None:
                                        start_date = input("Selecione a data inicial em formato dd/mm/yyyy HH:MM:SS: ")
                                        final_date = input("Selecione a data final em formato dd/mm/yyyy HH:MM:SS: ")
                                else:
                                        start_date = self.date_optional[0]
                                        final_date = self.date_optional[1]
                                if len(start_date) <= 10:
                                        start_date = ' '.join([start_date, "00:00:00"])
                                if len(final_date) <= 10:
                                        final_date = ' '.join([final_date, "23:59:59"])
                                try:
                                        start_date_parsed = datetime.datetime.strptime(start_date, "%d/%m/%Y %H:%M:%S")
                                        final_date_parsed = datetime.datetime.strptime(final_date, "%d/%m/%Y %H:%M:%S")
                                except:
                                        print("Alguma das datas é inválida, favor tentar novamente!")
                                        self.date_optional = None
                                        continue
                                if start_date_parsed < final_date_parsed:
                                        break
                                print("Você selecionou um período inválido, por favor tente novamente!")
                                self.date_optional = None
                        return [start_date_parsed,final_date_parsed]

                arrayDatas = loop_data()
                start_date_parsed = arrayDatas[0]
                final_date_parsed = arrayDatas[1]

                detailed_start_Month = self.months.get(start_date_parsed.month)
                detailed_final_Month = self.months.get(final_date_parsed.month)

                dates = {
                        "start_date": {
                        "value": start_date_parsed,
                        "parsed_camel" : start_date_parsed.strftime("%d_%m_%Y"),
                        "parsed_slash" :start_date_parsed.strftime("%d/%m/%Y"),
                        "mes" : detailed_start_Month,
                        "num_mes":str(start_date_parsed.month),
                        "dia" :str(start_date_parsed.day),
                        "ano" :str(start_date_parsed.year),
                        "unix_time": str(int(time.mktime(start_date_parsed.timetuple())) - int(10800))
                        },

                        "final_date": {
                        "value": final_date_parsed,
                        "parsed_camel" : final_date_parsed.strftime("%d_%m_%Y"),
                        "parsed_slash" :final_date_parsed.strftime("%d/%m/%Y"),
                        "mes" : detailed_final_Month,
                        "num_mes":str(final_date_parsed.month),
                        "dia" :str(final_date_parsed.day),
                        "ano" :str(final_date_parsed.year),
                        "unix_time": str(int(time.mktime(final_date_parsed.timetuple())) - int(10800))
                        }
                }
                print(dates)
                return dates

        def month_year():
                """    
                Requests the user to select a start and end month by specifying the month and year in the format 'month/year'.

                Returns:
                        dict: A dictionary containing the start and end dates of the selected months, along with their respective month-year representations.

                Example:
                        >>> month_year()
                        select the begin month by writing 'month/year':
                        month have a format mm, and year have a format yyyy: 01/2023
                        select the end month by writing 'month/year':
                        month have a format mm, and year have a format yyyy: 12/2023
                        {
                        "start_date": datetime.datetime(2023, 1, 31, 0, 0),
                        "end_date": datetime.datetime(2023, 12, 31, 0, 0),
                        "start_month": "01-2023",
                        "end_month": "12-2023"
                        }
                """
                since_month_input = input("select the begin month by writing 'month/year':\nmonth have a format mm, and year have a format yyyy: ")
                until_month_input = input("select the end month by writing 'month/year':\nmonth have a format mm, and year have a format yyyy: ")
                split_since_month = since_month_input.split('/')
                split_until_month = until_month_input.split('/')

                last_day_since = calendar.monthrange(int(split_since_month[1]), int(split_since_month[0]))[1]
                last_day_until = calendar.monthrange(int(split_until_month[1]), int(split_until_month[0]))[1]
                start_date_parsed = datetime.datetime(int(split_since_month[1]), int(split_since_month[0]), last_day_since, 0, 0, 0)
                end_date_parsed = datetime.datetime(int(split_until_month[1]), int(split_until_month[0]),last_day_until, 23, 59, 59)

                dates = {
                        "start_date" : start_date_parsed,
                        "end_date" : end_date_parsed,
                        "start_month": split_since_month[0] + "-" + split_since_month[1],
                        "end_month": split_until_month[0] + "-" + split_until_month[1]
                        }
                return dates