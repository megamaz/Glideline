import tkinter as tk
from tkinter import ttk


class Window(tk.Frame):

  def __init__(self, master=None):    
      tk.Frame.__init__(self, master)
            
      self.master = master
      self.master.title("Glideline")


def main():
    root = tk.Tk()
    app = Window()
    root.mainloop()


if __name__ == "__main__":
    main()