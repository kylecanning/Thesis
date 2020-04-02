import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog, ttk
import controller
import time
import datetime
from tkcalendar import DateEntry


class Application(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.controller = controller.Controller(self)
        self.comment = ''

        for x in range(2):
            self.grid_columnconfigure(x, weight=1)
        for x in range(6):
            self.grid_rowconfigure(x, weight=1)

        self.new_person_window = None
        self.Current_Dosimeter_ID = tk.StringVar()
        self.Current_Dosimeter_Value = tk.DoubleVar()
        self.ReactorBool = tk.BooleanVar()

        self.add_menubar(master)
        self.add_dosimeter_data()
        self.create_button_interface()

    def create_button_interface(self):
        self.Scan_Dossimeter = tk.Button(master=self, text="Scan Dosimeter", command=self.controller.scanner, bd=5, font="Calibri 16", overrelief="groove")
        self.Scan_Dossimeter.grid(row=0, column=0, columnspan=2, sticky="nswe")

        self.ReactorStatus = tk.Checkbutton(self, bd=5, onvalue=True, offvalue=False, text="Reactor ON", variable=self.ReactorBool, #selectcolor="#31363b"
                                            activeforeground="black", overrelief="groove", indicatoron=False, font="Calibri 14")
        self.ReactorStatus.grid(column=1, row=1, sticky="wens")

        self.add_new_person = tk.Button(self, text="Add New Person to Scan", command=self.controller.add_person, bd=5, font="Calibri 14", overrelief="groove")
        self.add_new_person.grid(row=2, column=1, sticky="wens")

        self.add_person_button = tk.Button(self, text="Add Existing Person to Scan", bd=5, font="Calibri 14", overrelief="groove",
                                           command=self.controller.query_for_people)
        self.add_person_button.grid(row=3, column=1, sticky="wens")

        self.add_comment_button = tk.Button(self, text="Add Comments to Visit", bd=5, font="Calibri 14",
                                            overrelief="groove",
                                            command=self.controller.query_for_comment)
        self.add_comment_button.grid(row=4, column=1, sticky="wens")

        self.OK = tk.Button(self, text="Submit Scan", command=self.controller.submit_scan, fg="green", bd=5, font="Calibri 16", overrelief="groove")
        self.OK.grid(row=5, column=0, columnspan=2, sticky="nswe")

    def toggle_buttons(self, enable_buttons):
        state = tk.NORMAL if enable_buttons else tk.DISABLED

        self.ReactorStatus.config(state=state)
        self.add_new_person.config(state=state)
        self.add_person_button.config(state=state)
        self.add_comment_button.config(state=state)
        self.peoplelist_button.config(state=state)

    def clear_peoplelist(self):
        self.peoplelist.delete(0, tk.END)

    def get_values(self):
        return self.Current_Dosimeter_ID.get(), self.Current_Dosimeter_Value.get(), self.ReactorBool.get(), self.peoplelist.get(0, tk.END), self.comment

    def set_dosimeter(self, id, value):
        self.Current_Dosimeter_ID.set(id)
        self.Current_Dosimeter_Value.set(value)

    def add_person_to_listbox(self, person_data):
        self.peoplelist.insert(tk.END, f"{person_data[0]:<20}{person_data[1]:<20}{person_data[2]:<20}{person_data[3]:<20}")


    def add_person(self):
        self.new_person_window = tk.Toplevel(self)
        tk.Label(self.new_person_window, text="First Name:", relief="groove", bd=5, font="Calibri 10").grid(row=0, column=0, sticky="nswe")
        tk.Label(self.new_person_window, text="Last Name:", relief="groove", bd=5, font="Calibri 10").grid(row=1, column=0, sticky="nswe")
        tk.Label(self.new_person_window, text="Contact Number:", relief="groove", bd=5, font="Calibri 10").grid(row=2, column=0, sticky="nswe")
        tk.Label(self.new_person_window, text="Employer:", relief="groove", bd=5, font="Calibri 10").grid(row=3, column=0, sticky="nswe")

        first_name = tk.StringVar()
        last_name = tk.StringVar()
        contact = tk.StringVar()
        employer = tk.StringVar()

        tk.Entry(self.new_person_window, textvariable=first_name, bd=3, font="Calibri 12").grid(column=1, row=0, sticky='we')
        tk.Entry(self.new_person_window, textvariable=last_name, bd=3, font="Calibri 12").grid(column=1, row=1, sticky='we')
        tk.Entry(self.new_person_window, textvariable=contact, bd=3, font="Calibri 12").grid(column=1, row=2, sticky='we')
        tk.Entry(self.new_person_window, textvariable=employer, bd=3, font="Calibri 12").grid(column=1, row=3, sticky='we')

        tk.Button(self.new_person_window, command=lambda: self.controller.return_person_info(first_name.get(), last_name.get(), contact.get(), employer.get()),
                  bd=5, text="Submit", font="Calibri 14", overrelief="groove").grid(row=4, columnspan=2, sticky="wens")

    def return_person_info(self, firstname, lastname, contact, employer):
        self.peoplelist.insert(tk.END, f"{firstname:<20}{lastname:<20}{contact:<20}{employer:<20}")  # only added to list if not already in db
        if self.new_person_window:
            self.new_person_window.destroy()

    def complete_scan(self):
        self.Current_Dosimeter_ID.set("")
        self.Current_Dosimeter_Value.set(0.0)
        self.peoplelist.delete(0, tk.END)
        self.ReactorBool.set(False)


    def person_added_error(self):
        messagebox.showerror("Adding Person", "This Person Already Exists. Please Use the Add Existing Person to Scan Button")
        self.new_person_window.destroy()

    def add_menubar(self, master):
        menubar = tk.Menu(master, font="Calibri 14")

        perm_person_dosimeter = tk.Menu(menubar, tearoff=0, relief="groove")
        perm_person_dosimeter.add_command(label="Add Person  to Dosimeter", command=self.controller.add_permanent_person, font="Calibri 14")
        perm_person_dosimeter.add_command(label="Remove Person from Dosimeter", command=lambda: self.controller.remove_perm_person_database(
            self.Dosimeter_ID.get()), font="Calibri 14")
        menubar.add_cascade(label="Assign/Dissociate Dosimeter", menu=perm_person_dosimeter)
        menubar.add_command(label="\u22EE", activebackground=menubar.cget("background"))  # easiest way to separate commands to show that each can be pressed


        menubar.add_command(label="Create Report ...", command=self.controller.report_creation_clicked)
        menubar.add_command(label="\u22EE", activebackground=menubar.cget("background"))

        configuration_menu = tk.Menu(menubar, tearoff=0)
        configuration_menu.add_command(label="Change IP", command=self.controller.change_server_IP, font="Calibri 14")
        configuration_menu.add_command(label="Change Serial Port", command=self.controller.change_serial_port, font="Calibri 14")
        configuration_menu.add_command(label="Add New Dosimeter", command=self.controller.add_new_dosimeter, font="Calibri 14")
        configuration_menu.add_command(label="Remove Dosimeter", command=self.controller.remove_dosimeter_from_system, font="Calibri 14")
        menubar.add_cascade(label="Configuration", menu=configuration_menu)
        master.config(menu=menubar)

    def add_dosimeter_data(self):
        labelframe = tk.LabelFrame(self, text="Dosimeter Data", font="Calibri 14", bd=5)
        labelframe.grid(row=1, sticky="nswe", rowspan=4)

        labelframe.grid_columnconfigure(0, weight=1)
        labelframe.grid_columnconfigure(1, weight=1)
        labelframe.grid_rowconfigure(0, weight=1)
        labelframe.grid_rowconfigure(1, weight=1)
        labelframe.grid_rowconfigure(2, weight=2)

        tk.Label(labelframe, text="Current Dosimeter ID:", relief="groove", bd=5, font="Calibri 16").grid(row=0, column=0, sticky="nswe")

        tk.Label(labelframe, text="Current Dosimeter Value (mSv):", relief="groove", bd=5, font="Calibri 16").grid(row=1, column=0, sticky="nswe")

        self.Dosimeter_ID = tk.Entry(labelframe, state=tk.DISABLED, textvariable=self.Current_Dosimeter_ID, background="white",
                                     disabledforeground="black", font="Calibri 18", bd=3)
        self.Dosimeter_ID.grid(column=1, row=0, sticky='we')

        self.Dosimeter_Value = tk.Entry(labelframe, state=tk.DISABLED, textvariable=self.Current_Dosimeter_Value, bd=3, disabledforeground="black",
                                        font="Calibri 18")
        self.Dosimeter_Value.grid(column=1, row=1, sticky='we')

        self.peoplelist = tk.Listbox(labelframe, bd=5, font="Calibri 12", selectmode="extended")
        self.peoplelist.grid(row=2, columnspan=2, sticky="nsew")
        self.peoplelist_button = tk.Button(labelframe, text="Remove Selected", bd=5, font="Calibri 14",
                         overrelief="groove",
                         command=self.controller.remove_selected_from_list)
        self.peoplelist_button.grid(row=3, columnspan=2, sticky="wens")

    def report_date_selection(self):
        top = tk.Toplevel(self)
        file_format = ttk.Combobox(top, state="readonly", values=("CSV", "PDF"))
        file_format.current(0)
        file_format.pack()
        start = DateEntry(top)
        start.pack()
        end = DateEntry(top)
        end.pack()
        # Convert datetime.date object to datetime.datetime to then convert to epoch time for use in db.
        tk.Button(top, text="Confirm Selection", command=lambda: self.controller.create_report(
            (datetime.datetime.combine(start.get_date(), datetime.datetime.min.time()) - datetime.datetime(1970, 1, 1)).total_seconds(),
            (datetime.datetime.combine(end.get_date(), datetime.datetime.min.time()) - datetime.datetime(1970, 1, 1)).total_seconds(),
            True if "PDF" in file_format.get() else False, top), fg="green", bd=5, font="Calibri 16", overrelief="groove").pack()


    def query_for_people(self, People):
        existing_person_window = tk.Toplevel(self)
        existing_person_window.geometry("480x480")
        people_list = tk.Listbox(existing_person_window, bd=5, font="Calibri 12", selectmode="extended")
        people_list.pack(fill=tk.BOTH, expand=1)
        okay = tk.Button(existing_person_window, text="OK", command=lambda: self.controller.submit_people(people_list, existing_person_window), fg="green",
                         bd=5,
                         font="Calibri 16", overrelief="groove")
        okay.pack()
        for person in People:
            people_list.insert(tk.END, f"{person[0]:<20}{person[1]:<20}{person[2]:<20}{person[3]:<20}")  # Only added to list if not already in db

    def add_permanent_person(self, People):
        existing_person_window = tk.Toplevel(self)
        existing_person_window.geometry("480x480")
        people_list = tk.Listbox(existing_person_window, bd=5, font="Calibri 12")
        people_list.pack(fill=tk.BOTH, expand=1)
        okay = tk.Button(existing_person_window, text="OK",
                         command=lambda: self.controller.send_perm_person_to_database(self.filter_values_from_listbox(people_list.get(
                             people_list.curselection())), self.Dosimeter_ID.get(), existing_person_window),
                         fg="green", bd=5, font="Calibri 16", overrelief="groove")

        okay.pack()
        for person in People:
            people_list.insert(tk.END, f"{person[0]:<20}{person[1]:<20}{person[2]:<20}{person[3]:<20}")  # Only added to list if not already in db

    def update_personlist(self, person_data):
        self.peoplelist.insert(tk.END, f"{person_data[0]:<20}{person_data[1]:<20}{person_data[2]:<20}{person_data[3]:<20}")  # Only added to list if not already in db

    def submit_people(self, listbox, toplevel):
        people = [listbox.get(idx) for idx in listbox.curselection()]
        previously_added_people = self.peoplelist.get(0, tk.END)
        for person in people:
            if person not in previously_added_people:
                self.peoplelist.insert(tk.END, person)
        toplevel.destroy()

    def add_comment(self):
        add_comment_window = tk.Toplevel(self)
        add_comment_window.geometry("720x530")
        tk.Label(add_comment_window, text="Comments:", relief="groove", bd=5, font="Calibri 10").pack(fill="both")
        comment = tk.Text(add_comment_window, bd=3, font="Calibri 12")
        comment.insert(tk.INSERT, self.comment)
        comment.pack(fill="both")
        buttonvar = tk.Button(add_comment_window, command=lambda: self.controller.add_comment_to_visit(add_comment_window, comment.get("1.0", tk.END)),
                              bd=5, text="Add Comment To Visit", font="Calibri 14", overrelief="groove")
        buttonvar.pack(fill="both")

    def remove_from_person_list(self, person=None):
        if not person:
            selection = self.peoplelist.curselection()
            for row in reversed(selection):
                self.peoplelist.delete(row)
        elif person:
            self.peoplelist.delete(0)

    def change_serial_port_popup(self, serial_port):
        top = tk.Toplevel(self)
        top.geometry("720x300")
        top.title("Serial Port configuration")
        tk.Message(top, text="Please enter the SerialPort you have the LDM220 connected to (EXAMPLE: COM3)", width=350, font="Calibri 14").pack(fill="x")

        port_entry = tk.Entry(top, font="Calibri 14")
        port_entry.insert(0, serial_port)
        port_entry.pack(fill="x")

        tk.Button(top, text="submit", font="Calibri 42", command=lambda: self.controller.update_serial_port(port_entry.get(), top)).pack(
            fill="both")

    def change_ip_popup(self, ip, port ):
        top = tk.Toplevel(self)
        top.geometry("720x300")
        top.title("IP and Port configuration")
        tk.Message(top, text="Please enter the ip and port you would like to connect to the server for. (localhost and 8000 work for running a server "
                                   "on the same machine)", width=350, font="Calibri 14").pack(fill="x")

        ip_entry = tk.Entry(top, font="Calibri 14")
        ip_entry.insert(0, ip)
        ip_entry.pack(fill="x")
        port_entry = tk.Entry(top, font="Calibri 14")
        port_entry.insert(0, str(port))
        port_entry.pack(fill="x")

        tk.Button(top, text="submit", font="Calibri 42", command= lambda : self.controller.update_ip_and_port(ip_entry.get(), port_entry.get(),
                                                                                                              top)).pack(fill="both")
    def request_dosimeter(self):
        return simpledialog.askstring("Dosimeter Removal", "Please enter the dosimeter Id you would like removed EXAMPLE: 806110")

    def add_dosimeter(self):
        DosimeterID = simpledialog.askstring("Adding Dosimeter", "add the dosimeter id for this dosimeter usually found on the back EXAMPLE: 806110")
        bytecode = simpledialog.askstring("Adding Dosimeter", "Please insert the 4 byte hexcode for this dosimeter EXAMPLE: \\x35\\x41\\x31\\x46")
        return DosimeterID, bytecode

    def confirm_box(self, dosimeterID):
        response = messagebox.askyesno("Dosimeter Removal", "Are you sure you want to remove this permanent association?")
        if response:
            self.controller.okay_remove_perm_person_database(dosimeterID)

    def choose_filename(self, extension):
         return filedialog.asksaveasfilename(parent=self, title="Save File as", defaultextension=extension, initialdir="Reports", initialfile=
             f"report-{datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d')}")

    @staticmethod
    def filter_values_from_listbox(person):
        return tuple(person.split())

    @staticmethod
    def close_window(window):
        window.destroy()

    @staticmethod
    def warning(title, text):
        messagebox.showerror(title, text)

    @staticmethod
    def information_box(title, text):
        messagebox.showinfo(title, text)


if __name__ == "__main__":
    root = tk.Tk()
    tk.Grid.rowconfigure(root, 0, weight=1)  # Used for resizing
    tk.Grid.columnconfigure(root, 0, weight=1)  # Used for resizing
    root.title('Dosimeter Logging System')
    root.geometry('1080x720')
    app = Application(master=root)
    app.grid(row=0, column=0, sticky="nsew")  # Used for resizing match frame to root size
    app.mainloop()
