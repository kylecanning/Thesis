import sqlite3
import time
import Constants


def create_tables():
    conn = sqlite3.connect("Dosimeter.db")
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS Person(firstName TEXT NOT NULL, lastName TEXT NOT NULL, contact TEXT, Employer TEXT NOT NULL, PersonID INTEGER "
              "PRIMARY KEY, UNIQUE(firstName, lastName))")
    c.execute("CREATE TABLE IF NOT EXISTS Dosimeter(ID TEXT PRIMARY KEY,PermPersonID INTEGER,  FOREIGN KEY(PermPersonID) REFERENCES Person(PersonID))")

    c.execute("CREATE TABLE IF NOT EXISTS Visit(VisitKey INTEGER PRIMARY KEY, DosimeterID TEXT NOT NULL, ExitDose REAL, EntryTime NUMERIC NOT NULL, "
              "ExitTime NUMERIC, ReactorStatus BOOLEAN NOT NULL, Notes TEXT, EntryDose REAL NOT NULL,FOREIGN KEY(DosimeterID) REFERENCES Dosimeter(ID))")

    c.execute("CREATE TABLE IF NOT EXISTS PersonOnVisit(VisitKey INTEGER PRIMARY KEY, PersonID INTEGER NOT NULL, VisitID INTEGER NOT NULL,"
              "FOREIGN KEY(PersonID) REFERENCES Person(PersonID), FOREIGN KEY(VisitID) REFERENCES Visit(VisitKey))")

    conn.commit()
    c.close()
    conn.close()


def init_dosimeter_table_data():
    conn = sqlite3.connect("Dosimeter.db")
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()

    for Identifier in Constants.DOSIMETER_IDS:
        c.execute("INSERT OR IGNORE INTO Dosimeter(ID) VALUES(?)", (Identifier,))
    conn.commit()
    c.close()
    conn.close()


def add_dosimeter_to_db(dosimeterID):
    conn = sqlite3.connect("Dosimeter.db")
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO Dosimeter(ID) VALUES(?)", (dosimeterID,))
    conn.commit()
    c.close()
    conn.close()


def add_permanent_person(first, last, dosimeterID):
    conn = sqlite3.connect("Dosimeter.db")
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()
    c.execute("SELECT PersonID FROM Person WHERE firstName=? AND lastName=?", (first, last))
    identifier = c.fetchall()[0][0]
    c.execute("SELECT EXISTS(SELECT 1 FROM Dosimeter WHERE ID=? AND PermPersonID IS NOT NULL)", (dosimeterID,))
    boolval = bool(c.fetchone()[0])
    if not boolval:  # This is overwriting
        c.execute("UPDATE Dosimeter SET PermPersonID=? WHERE ID=?", (identifier, dosimeterID))
    conn.commit()
    c.close()
    conn.close()
    return boolval


def remove_permanent_person_from_dosimeter(dosimeterID):
    conn = sqlite3.connect("Dosimeter.db")
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()
    c.execute("UPDATE Dosimeter SET PermPersonID = NULL WHERE ID=?", (dosimeterID,))
    conn.commit()
    c.close()
    conn.close()


def check_for_perm_person(DosimeterID):
    conn = sqlite3.connect("Dosimeter.db")
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()
    c.execute("SELECT firstName, lastName, contact, Employer FROM Person inner join Dosimeter ON Person.PersonID = Dosimeter.PermPersonID WHERE Dosimeter.ID=?"
    , (DosimeterID,))
    permperson = c.fetchone()  # Should always be a single entry
    conn.commit()
    c.close()
    conn.close()
    return permperson


def insert_new_person(firstName, lastName, contact, Employer):
    conn = sqlite3.connect("Dosimeter.db")
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO Person(firstName, lastName, contact, Employer)  VALUES(?,?,?,?)", (firstName, lastName, contact, Employer))
    except sqlite3.IntegrityError:
        raise sqlite3.IntegrityError
    finally:
        conn.commit()
        c.close()
        conn.close()


def check_entry_or_exit(DosimeterID):
    conn = sqlite3.connect("Dosimeter.db")
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()

    c.execute("SELECT EXISTS(SELECT 1 FROM Visit WHERE DosimeterID=? AND ExitDose IS NULL)", (DosimeterID,))  # this is an exit
    exit_bool = bool(c.fetchone()[0])

    conn.commit()
    c.close()
    conn.close()
    return exit_bool


def add_entry_scan(DosimeterID, dose, reactorStatus, people, Notes):
    dosage_delta = None
    conn = sqlite3.connect("Dosimeter.db")
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()
    current_time = int(time.time())

    is_exit = check_entry_or_exit(DosimeterID)

    if is_exit:  # Exit
        c.execute("SELECT VisitKey FROM Visit WHERE DosimeterID=? AND ExitDose IS NULL", (DosimeterID,))
        key = c.fetchone()[0]
        c.execute("UPDATE Visit SET ExitDose=?, ExitTime=? WHERE VisitKey=?", (dose, current_time, key))
        c.execute("SELECT EntryDose, ExitDose FROM VISIT WHERE VisitKey=?", (key,))
        dosage = c.fetchall()[0]  # tuple returned
        dosage_delta = dosage[1] - dosage[0]

    else:  # Entry
        c.execute("INSERT INTO Visit(Entrydose, DosimeterID, EntryTime, ReactorStatus, Notes) VALUES(?,?,?,?,?)", (dose, DosimeterID, current_time,
                                                                                                                   reactorStatus, Notes))
        c.execute("SELECT VisitKey FROM Visit WHERE DosimeterID=? AND EntryTime=?", (DosimeterID, current_time))
        currentvisitid = c.fetchone()[0]
        for person in people:  # People will be a list of tuples with first and last name
            c.execute("SELECT PersonID FROM Person WHERE firstName=? AND lastName=?", (person[0], person[1]))
            person_id = c.fetchone()[0]
            c.execute("INSERT INTO PersonOnVisit(VisitID, PersonID) VALUES(?,?)", (currentvisitid, person_id))
    conn.commit()
    c.close()
    conn.close()
    return dosage_delta


def find_people():
    conn = sqlite3.connect("Dosimeter.db")
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()
    c.execute("SELECT firstName, lastName, contact, Employer FROM Person")
    people = c.fetchall()
    c.close()
    conn.close()
    return people


def create_report(start_date, end_date):
    conn = sqlite3.connect("Dosimeter.db")
    conn.execute("PRAGMA foreign_keys = 1")
    c = conn.cursor()
    data = []
    for row in c.execute("""SELECT firstName, lastName, contact, Employer, DosimeterID, EntryTime, ExitTime, EntryDose, ExitDose, ReactorStatus, 
    Notes FROM Visit INNER 
    JOIN 
    PersonOnVisit POV on 
    Visit.VisitKey = POV.VisitID INNER JOIN Person P on POV.PersonID = P.PersonID WHERE ExitDose IS NOT NULL AND EntryTime >= (?) AND ExitTime <= (?)""",
                         (start_date, end_date)):
        data.append(row)
    c.close()
    conn.close()
    return data
