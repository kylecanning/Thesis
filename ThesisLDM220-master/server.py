import rpyc
import DataBase
import sqlite3
from rpyc.utils.server import ThreadedServer


class MyService(rpyc.Service):

    @staticmethod
    def exposed_remove_permanent_person_from_dosimeter(dosimeterID):
        DataBase.remove_permanent_person_from_dosimeter(dosimeterID)


    @staticmethod
    def exposed_insert_new_person(first_name, last_name, contact, employer):
        try:
            DataBase.insert_new_person(first_name, last_name, contact, employer)
            return True
        except sqlite3.IntegrityError:
            return False


    @staticmethod
    def exposed_submit_scan(DosimeterID, dose, reactorStatus, tupledPeople, Notes):
        return DataBase.add_entry_scan(DosimeterID, dose, reactorStatus, tupledPeople, Notes)


    @staticmethod
    def exposed_check_entry_or_exit(DosimeterID):
        return DataBase.check_entry_or_exit(DosimeterID)


    @staticmethod
    def exposed_check_for_perm_person(DosimeterID):
        return DataBase.check_for_perm_person(DosimeterID)


    @staticmethod
    def exposed_get_all_people():
        return DataBase.find_people()  # list of all people in database


    @staticmethod
    def exposed_add_permanent_person_to_dosimeter(person_data, dosimeterID):
        return DataBase.add_permanent_person(person_data[0], person_data[1], dosimeterID)  # send first and last name to get person ID


    @staticmethod
    def exposed_create_report(start_date, end_date):
        return DataBase.create_report(start_date, end_date)


    @staticmethod
    def exposed_add_dosimeter_to_db(DosimeterID):
        DataBase.add_dosimeter_to_db(DosimeterID)


def main():
    print("Starting...")
    DataBase.create_tables()
    DataBase.init_dosimeter_table_data()
    server = ThreadedServer(MyService, port=8000)
    server.start()
    print("The server has been started.")

