import tkinter as tk
from tkinter import ttk


class DocumentCreatorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Document Creator")
        self.geometry("1100x700")
        self.minsize(900, 600)

        self.selected_label = None
        self.label_buttons = []

        self.create_menu()
        self.create_layout()
        self.create_label_sheet()

    def create_menu(self):
        menu_bar = tk.Menu(self)

        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="New", command=self.new_document)
        file_menu.add_command(label="Open...")
        file_menu.add_command(label="Save")
        file_menu.add_separator()
        file_menu.add_command(label="Print Preview", command=self.print_preview)
        file_menu.add_command(label="Print")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)

        options_menu = tk.Menu(menu_bar, tearoff=False)
        options_menu.add_command(label="Application Options...")
        options_menu.add_command(label="Printer Setup...")
        menu_bar.add_cascade(label="Options", menu=options_menu)

        database_menu = tk.Menu(menu_bar, tearoff=False)
        database_menu.add_command(label="Import CSV...")
        database_menu.add_command(label="Manage Data Sources...")
        menu_bar.add_cascade(label="Database", menu=database_menu)

        objects_menu = tk.Menu(menu_bar, tearoff=False)
        objects_menu.add_command(label="Add Text", command=self.add_text)
        objects_menu.add_command(label="Add Barcode")
        objects_menu.add_command(label="Add Image")
        menu_bar.add_cascade(label="Objects", menu=objects_menu)

        view_menu = tk.Menu(menu_bar, tearoff=False)
        view_menu.add_command(label="Zoom In")
        view_menu.add_command(label="Zoom Out")
        view_menu.add_command(label="Fit Sheet")
        menu_bar.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="About Document Creator")
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.config(menu=menu_bar)

    def create_layout(self):
        self.left_panel = ttk.Frame(self, padding=12)
        self.left_panel.pack(side=tk.LEFT, fill=tk.Y)

        self.center_panel = ttk.Frame(self, padding=12)
        self.center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.right_panel = ttk.Frame(self, padding=12)
        self.right_panel.pack(side=tk.RIGHT, fill=tk.Y)

        ttk.Label(
            self.left_panel,
            text="Document",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor=tk.W, pady=(0, 15))

        ttk.Label(self.left_panel, text="Label template").pack(anchor=tk.W)

        self.template_var = tk.StringVar(
            value="Avery 5160 - Address Labels"
        )

        template_box = ttk.Combobox(
            self.left_panel,
            textvariable=self.template_var,
            state="readonly",
            width=28,
            values=[
                "Avery 5160 - Address Labels",
                "Avery 5163 - Shipping Labels",
                "Custom Template",
            ],
        )
        template_box.pack(anchor=tk.W, pady=(4, 15))

        ttk.Label(
            self.left_panel,
            text="Start printing at label",
        ).pack(anchor=tk.W)

        self.start_label_var = tk.StringVar(value="Label 1")

        self.start_label_box = ttk.Combobox(
            self.left_panel,
            textvariable=self.start_label_var,
            state="readonly",
            width=28,
        )
        self.start_label_box.pack(anchor=tk.W, pady=(4, 15))

        ttk.Button(
            self.left_panel,
            text="Apply Template",
            command=self.apply_template,
        ).pack(anchor=tk.W, pady=10)

        ttk.Label(
            self.right_panel,
            text="Properties",
            font=("Segoe UI", 16, "bold"),
        ).pack(anchor=tk.W, pady=(0, 15))

        self.selected_label_var = tk.StringVar(
            value="No label selected"
        )

        ttk.Label(
            self.right_panel,
            textvariable=self.selected_label_var,
        ).pack(anchor=tk.W, pady=(0, 15))

        ttk.Label(self.right_panel, text="Label text").pack(anchor=tk.W)

        self.label_text_var = tk.StringVar(value="Sample Label")

        ttk.Entry(
            self.right_panel,
            textvariable=self.label_text_var,
            width=28,
        ).pack(anchor=tk.W, pady=(4, 10))

        ttk.Button(
            self.right_panel,
            text="Update Selected Label",
            command=self.update_selected_label,
        ).pack(anchor=tk.W)

        self.status_var = tk.StringVar(value="Ready")

        ttk.Label(
            self.right_panel,
            textvariable=self.status_var,
            foreground="gray",
        ).pack(anchor=tk.W, pady=(25, 0))

    def create_label_sheet(self):
        self.sheet = tk.Frame(
            self.center_panel,
            background="white",
            relief=tk.SOLID,
            borderwidth=1,
        )
        self.sheet.pack(fill=tk.BOTH, expand=True)

        self.label_grid = tk.Frame(
            self.sheet,
            background="white",
        )
        self.label_grid.pack(
            fill=tk.BOTH,
            expand=True,
            padx=35,
            pady=35,
        )

        self.rebuild_labels()

    def rebuild_labels(self):
        for widget in self.label_grid.winfo_children():
            widget.destroy()

        self.label_buttons.clear()

        for number in range(1, 31):
            row = (number - 1) // 3
            column = (number - 1) % 3

            button = tk.Button(
                self.label_grid,
                text="Sample Label",
                background="white",
                relief=tk.GROOVE,
                borderwidth=1,
                command=lambda n=number: self.select_label(n),
            )

            button.grid(
                row=row,
                column=column,
                sticky="nsew",
                padx=3,
                pady=3,
            )

            self.label_buttons.append(button)

        for row in range(10):
            self.label_grid.rowconfigure(row, weight=1)

        for column in range(3):
            self.label_grid.columnconfigure(column, weight=1)

        self.start_label_box["values"] = [
            f"Label {number}" for number in range(1, 31)
        ]

    def select_label(self, number):
        self.selected_label = number
        self.selected_label_var.set(f"Label {number} selected")

        selected_button = self.label_buttons[number - 1]
        self.label_text_var.set(selected_button["text"])

        for button in self.label_buttons:
            button.configure(
                background="white",
                relief=tk.GROOVE,
            )

        selected_button.configure(
            background="#D9ECFF",
            relief=tk.SOLID,
        )

        self.status_var.set(f"Label {number} selected")

    def update_selected_label(self):
        if self.selected_label is None:
            self.status_var.set("Select a label first")
            return

        text = self.label_text_var.get()
        self.label_buttons[self.selected_label - 1].configure(text=text)
        self.status_var.set("Selected label updated")

    def new_document(self):
        self.selected_label = None
        self.selected_label_var.set("No label selected")
        self.label_text_var.set("Sample Label")
        self.rebuild_labels()
        self.status_var.set("New document created")

    def apply_template(self):
        self.rebuild_labels()
        self.status_var.set(
            f"{self.template_var.get()} applied"
        )

    def add_text(self):
        if self.selected_label is None:
            self.status_var.set("Select a label first")
            return

        self.label_text_var.set("New Text Object")
        self.update_selected_label()
        self.status_var.set("Text object added")

    def print_preview(self):
        self.status_var.set("Print preview will be added later")


if __name__ == "__main__":
    app = DocumentCreatorApp()
    app.mainloop()

