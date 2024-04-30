from tkinter import ttk
import tkinter
import multiprocessing

def print_me(x):
    print("i got pressed: %d"% x)

def wind_func():
    tk = tkinter.Tk()
    tk.title("PyRecording")

    frm = ttk.Frame(tk, padding=10)
    frm.grid()
    ttk.Label(frm, text="Hello world").grid(column=0, row=0)
    ttk.Button(frm, text="Quit", command=tk.destroy).grid(column=1, row=0)
    ttk.Button(frm, text="Test Button", command=lambda: print_me(5)).grid(column=1, row=1)
    tk.mainloop()

def test_1(var):
    print(f"var in test 1: {var}")
    var += 1
    test_2(var)

def test_2(var):
    print(f"var in test2: {var}")
    var += 1
    test_3(var)

def test_3(var):
    print(f"var in test3: {var}")

if __name__ == "__main__":
    x = 0
    test_1(x)
    print(f"x after all calls: {x}")
#      print("hello")
#      prc1 = multiprocessing.Process(target=wind_func)
#      prc1.start()
#      print("after wind_func")
#      prc1.join()
