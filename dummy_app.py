import tkinter as tk

BG, FG, BTN = "#24292e", "#ffffff", "#2da44e"

def on_start():
    start_btn.config(state=tk.DISABLED, text="Running…")
    root.after(800, show_done)            # simulate 0.8-s task

def show_done():
    done_lbl.place(relx=.5, rely=.6, anchor="center")

root = tk.Tk()
root.title("S I M  L A B")
root.geometry("450x250")
root.configure(bg=BG)

# keep the window on top for the first second so PyCharm can't hide it
root.lift()
root.attributes('-topmost', True)
root.after(1000, lambda: root.attributes('-topmost', False))

start_btn = tk.Button(root, text="Start", font=("Segoe UI", 16, "bold"),
                      bg=BTN, fg=FG, activebackground="#2c974b",
                      padx=24, pady=12, command=on_start)
start_btn.place(relx=.5, rely=.3, anchor="center")

done_lbl = tk.Label(root, text="Simulation Complete ✔",
                    font=("Segoe UI", 14, "bold"),
                    fg="#33d17a", bg=BG)

if __name__ == "__main__":
    root.mainloop()
