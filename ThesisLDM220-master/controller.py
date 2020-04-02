import datetime
import multiprocessing
import os

from serial import SerialException

import CSV
import dosimeter
import pdf
import rpyc
import Constants
import pickle
import error

class Controller():

    def __init__(self, app):
        self.app = app
        self.ALL_PROCESSES = []
        self.create_directories()
        self.load_previous_values()


    @staticmethod
    def create_directories():
        if not os.path.exists("Saved_Values"):
            os.mkdir(os.getcwd() + "/Saved_Values")

        if not os.path.exists("Reports"):
            os.mkdir(os.getcwd() + "/Reports")


    @staticmethod
    def load_previous_values():
        if os.path.exists("Saved_Values/ip_config.txt"):
            print("hello")
            Constants.IP_and_PORT = pickle.load(open("Saved_Values/ip_config.txt", "rb"))

        if os.path.exists("Saved_Values/dosimeter_config.txt"):
            print("hello")
            Constants.DOSIMETER_IDS = pickle.load(open("Saved_Values/dosimeter_values.txt", "rb"))

        if os.path.exists("Saved_Values/dosimeter_bytecode_config.txt"):
            print("hello")
            Constants.VALUECOMMAND = pickle.load(open("Saved_Values/dosimeter_bytecode_values.txt", "rb"))

        if os.path.exists("Saved_Values/SerialPort_config.txt"):
            print("hello")
            Constants.PORT = pickle.load(open("Saved_Values/SerialPort_config.txt", "rb"))


    def submit_scan(self):
        DosimeterID, dose, reactorStatus, people, Notes = self.app.get_values()
        tupledPeople = [self.app.filter_values_from_listbox(person) for person in people]  # list of tuples containing each value

        try:
            c = rpyc.connect(Constants.IP_and_PORT[0], Constants.IP_and_PORT[1])
        except ConnectionError:
            self.app.warning("Server Connection", "Could not connect to server. Please check your IP settings")
            return

        is_exit = c.root.check_entry_or_exit(DosimeterID)  # TODO: should we pass this value below so only 1 call to the db to check is made?
        if not is_exit and not people:  # entry scan that has no people attached to it
            self.app.warning("Scan Submission", "You must have at least one person attached to an entry scan. Please try again")
            c.close()
            return
        dosage = c.root.submit_scan(DosimeterID, dose, reactorStatus, tupledPeople, Notes)
        c.close()

        self.app.comment = ''
        self.app.complete_scan()
        if is_exit:
            is_warning = True if dosage >= Constants.VISIT_DOSAGE_LIMIT else False
            if is_warning:
                self.app.warning("Scan Submission", f"YOU HAVE RECEIVED {dosage} AND MUST CONSULT HELP")
            else:
                self.app.information_box("Scan Submission", f"Scan successfully submitted. Received dose: {dosage}")
        else:
            self.app.information_box("Scan Submission", "Entry Scan Successful!")


    def scanner(self):
        self.app.Current_Dosimeter_ID.set("")
        self.app.Current_Dosimeter_Value.set(0)
        self.app.clear_peoplelist()
        try:
            identifier, value = dosimeter.FullRun()
            self.app.set_dosimeter(identifier, value)
        except SerialException:
            self.app.warning("Dosimeter Error", "Could not open serial port. check serial port settings")
            return
        except error.DosimeterNotFound:
            self.app.warning("Dosimeter Error", "Could not read/find dosimeter please try again")
            return
        c = rpyc.connect(Constants.IP_and_PORT[0], Constants.IP_and_PORT[1])
        is_exit = c.root.check_entry_or_exit(identifier)
        perm_person = c.root.check_for_perm_person(identifier)
        c.close()
        if perm_person:
            self.app.add_person_to_listbox(perm_person)

        if is_exit:
            enable_buttons = False
        else:
            enable_buttons = True

        self.app.toggle_buttons(enable_buttons)


    def add_person(self):
        self.app.add_person()


    def return_person_info(self, first_name, last_name, contact, employer):
        c = rpyc.connect(Constants.IP_and_PORT[0], Constants.IP_and_PORT[1])
        if c.root.insert_new_person(first_name, last_name, contact, employer):
            self.app.return_person_info(first_name, last_name, contact, employer)
        else:
            self.app.person_added_error()
        c.close()


    def query_for_people(self):
        c = rpyc.connect(Constants.IP_and_PORT[0], Constants.IP_and_PORT[1])
        people_query = c.root.get_all_people()

        self.app.query_for_people(people_query)
        c.close()


    def remove_selected_from_list(self):
        self.app.remove_from_person_list()


    def submit_people(self, listbox, toplevel):
        self.app.submit_people(listbox, toplevel)


    def query_for_comment(self):
        self.app.add_comment()
        self.start_keyboard_thread()


    def start_keyboard_thread(self):
        proc = multiprocessing.Process(target=Controller.threaded_keyboard)
        proc.start()
        self.ALL_PROCESSES.append(proc)


    @staticmethod
    def threaded_keyboard():
        os.system("osk")


    def add_permanent_person(self):
        c = rpyc.connect(Constants.IP_and_PORT[0], Constants.IP_and_PORT[1])
        people_query = c.root.get_all_people()
        self.app.add_permanent_person(people_query)
        c.close()


    def remove_perm_person_database(self, dosimeterID):
        if not dosimeterID:  # field was empty and needs to be scanned
            self.app.warning("Dosimeter ID not Found", "You must scan a Dosimeter in order to add a person to it")
            return
        self.app.confirm_box(dosimeterID)


    def okay_remove_perm_person_database(self, dosimeterID):
        c = rpyc.connect(Constants.IP_and_PORT[0], Constants.IP_and_PORT[1])
        c.root.remove_permanent_person_from_dosimeter(dosimeterID)
        c.close()
        self.app.information_box("Permanent Dosimeter Relation", "Relation Removed.")


    def send_perm_person_to_database(self, person_data, dosimeterID, window):
        self.app.close_window(window)
        if not dosimeterID:  # field was empty and needs to be scanned
            self.app.warning("Dosimeter ID not Found", "You must scan a Dosimeter in order to add a person to it")
            return
        c = rpyc.connect(Constants.IP_and_PORT[0], Constants.IP_and_PORT[1])
        dosimeter_relation_added = c.root.add_permanent_person_to_dosimeter(person_data, dosimeterID)
        c.close()
        if dosimeter_relation_added:
            self.app.warning("Permanent Dosimeter Relation", "A person has already been assigned as the holder of this Dosimeter.\nPlease remove them before "
                                                             "adding another.")
        else:
            self.app.information_box("Permanent Dosimeter Relation", "Relation added!")
            self.app.add_person_to_listbox(person_data)


    def add_comment_to_visit(self, window, comment):
        print(comment)
        self.app.comment = comment
        window.destroy()


    def report_creation_clicked(self):
        self.app.report_date_selection()


    def create_report(self, startrange, endrange, is_PDF, window):
        self.app.close_window(window)
        c = rpyc.connect(Constants.IP_and_PORT[0], Constants.IP_and_PORT[1])
        data = c.root.create_report(startrange, endrange)
        if data:
            formatted_data = Controller.format_report_data(data)
            if is_PDF:
                filename = self.app.choose_filename(".pdf")
                if not filename: # user clicked cancel
                    return
                pdf.simple_table(formatted_data, filename)
                message = "PDF report created!"
            else:
                filename = self.app.choose_filename(".csv")
                if not filename:  # user clicked cancel
                    return
                CSV.report_creation(formatted_data, filename)
                message = "CSV report created!"
            self.app.information_box("Report Creation", message)
        else:
            self.app.warning("Database Error", "No data in the Database")
        c.close()


    @staticmethod
    def date_format(epoch):
        return datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M')


    @staticmethod
    def total_date_format(epoch):
        return datetime.datetime.fromtimestamp(epoch)


    @staticmethod
    def bool_to_string(boolean):
        return "ON" if boolean else "OFF"


    @staticmethod
    def format_report_data(data):
        formatted = []
        for entry in data: # tuple
            new_entry = [f"{entry[0]} {entry[1]}",entry[2],entry[3], entry[4], Controller.date_format(entry[5]), Controller.date_format(entry[6]),
                         entry[8]-entry[7], Controller.bool_to_string(bool(entry[9])), entry[10]]
            formatted.append(new_entry)
        return formatted


    def update_ip_and_port(self, ip, port, window):
        self.app.close_window(window)
        Constants.IP_and_PORT = (str(ip), int(port))

        with open("Saved_Values/ip_config.txt", "wb") as fp:
            pickle.dump(Constants.IP_and_PORT, fp)


    def update_serial_port(self, port, window):
        self.app.close_window(window)
        Constants.PORT = str(port)
        with open("Saved_Values/SerialPort_config.txt", "wb") as fp:
            pickle.dump(Constants.PORT, fp)


    def remove_dosimeter_from_system(self):
        DosimeterID = self.app.request_dosimeter() #TODO: should this be done by listbox instead?
        try:
            Constants.DOSIMETER_IDS = Constants.DOSIMETER_IDS.remove(DosimeterID)
            Constants.VALUECOMMAND.pop(DosimeterID)
        except ValueError:
            pass #dont care if its already removed
        with open("Saved_Values/dosimeter_values.txt", "wb") as fp:
            pickle.dump(Constants.DOSIMETER_IDS, fp)
        with open("Saved_Values/dosimeter_bytecode_values.txt", "wb") as fp:
            pickle.dump(Constants.VALUECOMMAND, fp)
        self.app.information_box("Dosimeter Removal", f"Dosimeter {DosimeterID} has been removed!")


    def add_new_dosimeter(self):
        DosimeterID, bytecode = self.app.add_dosimeter()
        if not DosimeterID or not bytecode:
            return
        Constants.DOSIMETER_IDS.append(DosimeterID)
        Constants.VALUECOMMAND[DosimeterID] = bytecode

        c = rpyc.connect(Constants.IP_and_PORT[0], Constants.IP_and_PORT[1])
        c.root.add_dosimeter_to_db(DosimeterID)
        c.close()

        with open("Saved_Values/dosimeter_config.txt", "wb") as fp:
            pickle.dump(Constants.DOSIMETER_IDS, fp)
        with open("Saved_Values/dosimeter_bytecode_config.txt", "wb") as fp:
            pickle.dump(Constants.VALUECOMMAND, fp)
        self.app.information_box("Dosimeter Addition", f"Dosimeter {DosimeterID} has been added to the system!")


    def change_server_IP(self):
        self.app.change_ip_popup(Constants.IP_and_PORT[0], Constants.IP_and_PORT[1])


    def change_serial_port(self):
        self.app.change_serial_port_popup(Constants.PORT)


    def quit(self):
        self.app.quit()
