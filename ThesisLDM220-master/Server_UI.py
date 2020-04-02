import server
import tkinter as tk


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Dosimeter Logging System Server')
    root.geometry('480x240')
    tk.Button(root, text="QUIT", command=root.destroy, fg="red", bd=5, font="Calibri 16", overrelief="groove").pack(fill=tk.BOTH)
    root.after(1000, server.main())
    server.main()
    #root.mainloop()
