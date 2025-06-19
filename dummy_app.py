import tkinter as tk


class SimApp(tk.Tk):
    BG  = "#24292e"
    FG  = "#ffffff"
    BTN = "#2da44e"

    def __init__(self) -> None:
        super().__init__()

        # -- window basics --
        self.title("S I M  L A B")
        self.geometry("520x270")
        self.configure(bg=self.BG)

        # -- value entry --
        tk.Label(self, text="Value:", bg=self.BG, fg=self.FG,
                 font=("Segoe UI", 12)).place(relx=.15, rely=.25, anchor="e")

        self.val_entry = tk.Entry(self, width=10, font=("Segoe UI", 12))
        self.val_entry.place(relx=.18, rely=.25, anchor="w")

        # -- speed entry --
        tk.Label(self, text="Speed:", bg=self.BG, fg=self.FG,
                 font=("Segoe UI", 12)).place(relx=.15, rely=.40, anchor="e")

        self.spd_entry = tk.Entry(self, width=10, font=("Segoe UI", 12))
        self.spd_entry.place(relx=.18, rely=.40, anchor="w")

        # -- start button --
        tk.Button(
            self,
            text="Start",
            font=("Segoe UI", 14, "bold"),
            bg=self.BTN,
            fg=self.FG,
            activebackground="#2c974b",
            padx=20,
            pady=6,
            command=self.validate,          # ← bound method
        ).place(relx=.5, rely=.55, anchor="center")

        # -- feedback labels (initially hidden) --
        self.msg_ok = tk.Label(
            self,
            text="All values OK ✔",
            fg="#32c86c",
            bg=self.BG,
            font=("Segoe UI", 14, "bold")
        )
        self.msg_bad = tk.Label(
            self,
            text="Invalid input ✖",
            fg="#ff5959",
            bg=self.BG,
            font=("Segoe UI", 14, "bold")
        )

    # -----------------------------------------------------------------
    # validation logic (now an instance method)
    # -----------------------------------------------------------------
    def validate(self) -> None:
        """Check both entries and show green/red feedback."""
        try:
            v = float(self.val_entry.get())
            s = float(self.spd_entry.get())
            ok = 10 <= v <= 50 and 0 <= s <= 100
        except ValueError:
            ok = False

        # hide both, then show the correct one
        self.msg_ok.place_forget()
        self.msg_bad.place_forget()
        (self.msg_ok if ok else self.msg_bad).place(
            relx=.5, rely=.75, anchor="center"
        )


# ---------------------------------------------------------------------
# entry-point
# ---------------------------------------------------------------------
if __name__ == "__main__":
    SimApp().mainloop()
