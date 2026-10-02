import tkinter as tk
from tkinter import ttk, messagebox


class DocumentCreatorApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Document Creator")
        self.geometry("1200x800")
        self.minsize(950, 650)

        self.selected_label = None

        self.zoom = 0.75
        self.dpi = 96

        self.page_width_inches = 8.5
        self.page_height_inches = 11.0

        self.create_menu()
        self.create_layout()
        self.create_page_designer()

    # ---------------------------------------------------------
    # Menus
    # ---------------------------------------------------------

    def create_menu(self):
        menu_bar = tk.Menu(self)

        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(
            label="New",
            command=self.new_document,
        )
        file_menu.add_command(label="Open...")
        file_menu.add_command(label="Save")
        file_menu.add_separator()
        file_menu.add_command(
            label="Print Preview",
            command=self.print_preview,
        )
        file_menu.add_command(label="Print")
        file_menu.add_separator()
        file_menu.add_command(
            label="Exit",
            command=self.destroy,
        )
        menu_bar.add_cascade(
            label="File",
            menu=file_menu,
        )

        options_menu = tk.Menu(menu_bar, tearoff=False)
        options_menu.add_command(label="Application Options...")
        options_menu.add_command(label="Printer Setup...")
        menu_bar.add_cascade(
            label="Options",
            menu=options_menu,
        )

        database_menu = tk.Menu(menu_bar, tearoff=False)
        database_menu.add_command(label="Import CSV...")
        database_menu.add_command(
            label="Manage Data Sources..."
        )
        menu_bar.add_cascade(
            label="Database",
            menu=database_menu,
        )

        objects_menu = tk.Menu(menu_bar, tearoff=False)
        objects_menu.add_command(
            label="Add Text",
            command=self.add_text,
        )
        objects_menu.add_command(
            label="Add Barcode",
            command=self.add_barcode,
        )
        objects_menu.add_command(label="Add Image")
        menu_bar.add_cascade(
            label="Objects",
            menu=objects_menu,
        )

        view_menu = tk.Menu(menu_bar, tearoff=False)
        view_menu.add_command(
            label="Zoom In",
            command=self.zoom_in,
        )
        view_menu.add_command(
            label="Zoom Out",
            command=self.zoom_out,
        )
        view_menu.add_command(
            label="Fit Page",
            command=self.fit_page,
        )
        menu_bar.add_cascade(
            label="View",
            menu=view_menu,
        )

        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(
            label="About Document Creator",
            command=self.show_about,
        )
        menu_bar.add_cascade(
            label="Help",
            menu=help_menu,
        )

        self.config(menu=menu_bar)

    # ---------------------------------------------------------
    # Main layout
    # ---------------------------------------------------------

    def create_layout(self):
        self.left_panel = ttk.Frame(
            self,
            padding=12,
        )
        self.left_panel.pack(
            side=tk.LEFT,
            fill=tk.Y,
        )

        self.center_panel = ttk.Frame(
            self,
            padding=12,
        )
        self.center_panel.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True,
        )

        self.right_panel = ttk.Frame(
            self,
            padding=12,
        )
        self.right_panel.pack(
            side=tk.RIGHT,
            fill=tk.Y,
        )

        # Left panel
        ttk.Label(
            self.left_panel,
            text="Document",
            font=("Segoe UI", 16, "bold"),
        ).pack(
            anchor=tk.W,
            pady=(0, 15),
        )

        ttk.Label(
            self.left_panel,
            text="Page size",
        ).pack(anchor=tk.W)

        self.page_size_var = tk.StringVar(
            value="Letter - 8.5 x 11 inches"
        )

        ttk.Combobox(
            self.left_panel,
            textvariable=self.page_size_var,
            state="readonly",
            width=28,
            values=[
                "Letter - 8.5 x 11 inches",
                "A4 - 8.27 x 11.69 inches",
                "Custom",
            ],
        ).pack(
            anchor=tk.W,
            pady=(4, 15),
        )

        ttk.Label(
            self.left_panel,
            text="Template",
        ).pack(anchor=tk.W)

        self.template_var = tk.StringVar(
            value="Avery 5160 - Address Labels"
        )

        ttk.Combobox(
            self.left_panel,
            textvariable=self.template_var,
            state="readonly",
            width=28,
            values=[
                "None",
                "Avery 5160 - Address Labels",
                "Avery 5163 - Shipping Labels",
                "Custom Template",
            ],
        ).pack(
            anchor=tk.W,
            pady=(4, 15),
        )

        ttk.Label(
            self.left_panel,
            text="Start printing at label",
        ).pack(anchor=tk.W)

        self.start_label_var = tk.StringVar(
            value="Label 1"
        )

        self.start_label_box = ttk.Combobox(
            self.left_panel,
            textvariable=self.start_label_var,
            state="readonly",
            width=28,
        )
        self.start_label_box.pack(
            anchor=tk.W,
            pady=(4, 15),
        )

        ttk.Button(
            self.left_panel,
            text="Apply Template",
            command=self.apply_template,
        ).pack(
            anchor=tk.W,
            pady=10,
        )

        ttk.Separator(
            self.left_panel,
            orient=tk.HORIZONTAL,
        ).pack(
            fill=tk.X,
            pady=18,
        )

        ttk.Label(
            self.left_panel,
            text="Zoom",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W)

        ttk.Button(
            self.left_panel,
            text="Zoom In",
            command=self.zoom_in,
        ).pack(
            anchor=tk.W,
            fill=tk.X,
            pady=(6, 2),
        )

        ttk.Button(
            self.left_panel,
            text="Zoom Out",
            command=self.zoom_out,
        ).pack(
            anchor=tk.W,
            fill=tk.X,
            pady=2,
        )

        ttk.Button(
            self.left_panel,
            text="Fit Page",
            command=self.fit_page,
        ).pack(
            anchor=tk.W,
            fill=tk.X,
            pady=2,
        )

        # Right panel
        ttk.Label(
            self.right_panel,
            text="Properties",
            font=("Segoe UI", 16, "bold"),
        ).pack(
            anchor=tk.W,
            pady=(0, 15),
        )

        self.selected_label_var = tk.StringVar(
            value="No label selected"
        )

        ttk.Label(
            self.right_panel,
            textvariable=self.selected_label_var,
        ).pack(
            anchor=tk.W,
            pady=(0, 15),
        )

        ttk.Label(
            self.right_panel,
            text="Text object content",
        ).pack(anchor=tk.W)

        self.label_text_var = tk.StringVar(
            value="Sample Label"
        )

        ttk.Entry(
            self.right_panel,
            textvariable=self.label_text_var,
            width=28,
        ).pack(
            anchor=tk.W,
            pady=(4, 10),
        )

        ttk.Button(
            self.right_panel,
            text="Add Text to Page",
            command=self.add_text,
        ).pack(
            anchor=tk.W,
            fill=tk.X,
            pady=2,
        )

        ttk.Button(
            self.right_panel,
            text="Update Selected Label",
            command=self.update_selected_label,
        ).pack(
            anchor=tk.W,
            fill=tk.X,
            pady=2,
        )

        ttk.Button(
            self.right_panel,
            text="Add Barcode Placeholder",
            command=self.add_barcode,
        ).pack(
            anchor=tk.W,
            fill=tk.X,
            pady=2,
        )

        ttk.Separator(
            self.right_panel,
            orient=tk.HORIZONTAL,
        ).pack(
            fill=tk.X,
            pady=20,
        )

        ttk.Label(
            self.right_panel,
            text="Status",
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor=tk.W)

        self.status_var = tk.StringVar(
            value="Ready"
        )

        ttk.Label(
            self.right_panel,
            textvariable=self.status_var,
            foreground="gray",
            wraplength=210,
        ).pack(
            anchor=tk.W,
            pady=(5, 0),
        )

    # ---------------------------------------------------------
    # Full-page canvas designer
    # ---------------------------------------------------------

    def create_page_designer(self):
        self.canvas_frame = ttk.Frame(
            self.center_panel
        )
        self.canvas_frame.pack(
            fill=tk.BOTH,
            expand=True,
        )

        self.canvas_frame.rowconfigure(
            0,
            weight=1,
        )
        self.canvas_frame.columnconfigure(
            0,
            weight=1,
        )

        self.canvas = tk.Canvas(
            self.canvas_frame,
            background="#D8D8D8",
            highlightthickness=0,
        )
        self.canvas.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        vertical_scrollbar = ttk.Scrollbar(
            self.canvas_frame,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
        )
        vertical_scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
        )

        horizontal_scrollbar = ttk.Scrollbar(
            self.canvas_frame,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview,
        )
        horizontal_scrollbar.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        self.canvas.configure(
            yscrollcommand=vertical_scrollbar.set,
            xscrollcommand=horizontal_scrollbar.set,
        )

        self.canvas.bind(
            "<Button-1>",
            self.canvas_clicked,
        )

        self.draw_page()

    def draw_page(self):
        self.canvas.delete("all")

        page_width = int(
            self.page_width_inches
            * self.dpi
            * self.zoom
        )

        page_height = int(
            self.page_height_inches
            * self.dpi
            * self.zoom
        )

        page_x = 60
        page_y = 45

        self.page_x = page_x
        self.page_y = page_y
        self.page_width = page_width
        self.page_height = page_height

        self.canvas.configure(
            scrollregion=(
                0,
                0,
                page_x + page_width + 80,
                page_y + page_height + 80,
            )
        )

        # Page shadow
        self.canvas.create_rectangle(
            page_x + 5,
            page_y + 5,
            page_x + page_width + 5,
            page_y + page_height + 5,
            fill="#AAAAAA",
            outline="",
            tags="page_shadow",
        )

        # White page
        self.canvas.create_rectangle(
            page_x,
            page_y,
            page_x + page_width,
            page_y + page_height,
            fill="white",
            outline="#777777",
            width=1,
            tags="page",
        )

        self.canvas.create_text(
            page_x,
            page_y - 12,
            text=(
                f"Letter page — "
                f"{self.page_width_inches} x "
                f"{self.page_height_inches} inches — "
                f"{int(self.zoom * 100)}%"
            ),
            anchor=tk.SW,
            fill="#555555",
            font=("Segoe UI", 9),
        )

        if self.template_var.get() != "None":
            self.draw_label_guides(
                page_x,
                page_y,
            )

        # Initial sample objects
        self.canvas.create_text(
            page_x + 45,
            page_y + 45,
            text="Sample Document",
            anchor=tk.NW,
            fill="#222222",
            font=("Arial", 18, "bold"),
            tags=(
                "document_object",
                "sample_text",
            ),
        )

        self.canvas.create_text(
            page_x + 45,
            page_y + 88,
            text="Full-page document designer",
            anchor=tk.NW,
            fill="#555555",
            font=("Arial", 11),
            tags=(
                "document_object",
                "sample_instruction",
            ),
        )

        self.status_var.set(
            f"Page displayed at {int(self.zoom * 100)}%"
        )

    def draw_label_guides(self, page_x, page_y):
        columns = 3
        rows = 10

        # Approximate Avery 5160 dimensions
        left_margin = 0.1875
        top_margin = 0.5
        label_width = 2.625
        label_height = 1.0
        horizontal_gap = 0.125
        vertical_gap = 0.0

        scale = self.dpi * self.zoom

        for row in range(rows):
            for column in range(columns):
                x = page_x + (
                    left_margin
                    + column * (
                        label_width
                        + horizontal_gap
                    )
                ) * scale

                y = page_y + (
                    top_margin
                    + row * (
                        label_height
                        + vertical_gap
                    )
                ) * scale

                width = label_width * scale
                height = label_height * scale

                label_number = row * columns + column + 1

                self.canvas.create_rectangle(
                    x,
                    y,
                    x + width,
                    y + height,
                    outline="#8FAECC",
                    dash=(4, 3),
                    width=1,
                    tags=(
                        "label_guide",
                        f"label_{label_number}",
                    ),
                )

                self.canvas.create_text(
                    x + 5,
                    y + 4,
                    text=str(label_number),
                    anchor=tk.NW,
                    fill="#7892AD",
                    font=("Segoe UI", 8),
                    tags=(
                        "label_guide",
                        f"label_{label_number}",
                    ),
                )

    # ---------------------------------------------------------
    # Canvas interaction
    # ---------------------------------------------------------

    def canvas_clicked(self, event):
        canvas_x = self.canvas.canvasx(event.x)
        canvas_y = self.canvas.canvasy(event.y)

        clicked_items = self.canvas.find_overlapping(
            canvas_x,
            canvas_y,
            canvas_x,
            canvas_y,
        )

        selected_label = None

        for item_id in clicked_items:
            tags = self.canvas.gettags(item_id)

            for tag in tags:
                if tag.startswith("label_"):
                    selected_label = int(
                        tag.replace("label_", "")
                    )
                    break

            if selected_label is not None:
                break

        if selected_label is not None:
            self.select_canvas_label(
                selected_label
            )

    def select_canvas_label(self, number):
        self.selected_label = number

        self.selected_label_var.set(
            f"Label {number} selected"
        )

        self.start_label_var.set(
            f"Label {number}"
        )

        self.canvas.delete("selection")

        columns = 3

        left_margin = 0.1875
        top_margin = 0.5
        label_width = 2.625
        label_height = 1.0
        horizontal_gap = 0.125
        vertical_gap = 0.0

        scale = self.dpi * self.zoom

        row = (number - 1) // columns
        column = (number - 1) % columns

        x = self.page_x + (
            left_margin
            + column * (
                label_width
                + horizontal_gap
            )
        ) * scale

        y = self.page_y + (
            top_margin
            + row * (
                label_height
                + vertical_gap
            )
        ) * scale

        width = label_width * scale
        height = label_height * scale

        self.canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            outline="#1473E6",
            width=3,
            tags="selection",
        )

        self.canvas.tag_raise("selection")

        self.status_var.set(
            f"Label {number} selected"
        )

    # ---------------------------------------------------------
    # Document actions
    # ---------------------------------------------------------

    def add_text(self):
        self.canvas.create_text(
            self.page_x + 45,
            self.page_y + 150,
            text=self.label_text_var.get(),
            anchor=tk.NW,
            fill="#222222",
            font=("Arial", 12),
            tags=(
                "document_object",
                "text_object",
            ),
        )

        self.status_var.set(
            "Text object added to page"
        )

    def add_barcode(self):
        self.canvas.create_rectangle(
            self.page_x + 45,
            self.page_y + 200,
            self.page_x + 240,
            self.page_y + 250,
            fill="white",
            outline="#222222",
            width=1,
            tags=(
                "document_object",
                "barcode_placeholder",
            ),
        )

        self.canvas.create_text(
            self.page_x + 142,
            self.page_y + 225,
            text="CODE 128 BARCODE",
            fill="#222222",
            font=("Arial", 10),
            tags=(
                "document_object",
                "barcode_placeholder",
            ),
        )

        self.status_var.set(
            "Barcode placeholder added"
        )

    def update_selected_label(self):
        if self.selected_label is None:
            self.status_var.set(
                "Select a label first"
            )
            return

        self.status_var.set(
            f"Text for label "
            f"{self.selected_label} set to: "
            f"{self.label_text_var.get()}"
        )

    def new_document(self):
        self.selected_label = None
        self.selected_label_var.set(
            "No label selected"
        )
        self.label_text_var.set(
            "Sample Label"
        )
        self.template_var.set(
            "Avery 5160 - Address Labels"
        )
        self.draw_page()
        self.status_var.set(
            "New document created"
        )

    def apply_template(self):
        self.selected_label = None
        self.selected_label_var.set(
            "No label selected"
        )
        self.draw_page()
        self.status_var.set(
            f"{self.template_var.get()} applied"
        )

    def print_preview(self):
        self.status_var.set(
            "Print preview will be added later"
        )

    # ---------------------------------------------------------
    # Zoom
    # ---------------------------------------------------------

    def zoom_in(self):
        self.zoom = min(
            self.zoom + 0.10,
            2.0,
        )
        self.draw_page()

    def zoom_out(self):
        self.zoom = max(
            self.zoom - 0.10,
            0.30,
        )
        self.draw_page()

    def fit_page(self):
        available_width = max(
            self.center_panel.winfo_width() - 100,
            400,
        )

        available_height = max(
            self.center_panel.winfo_height() - 100,
            400,
        )

        width_zoom = available_width / (
            self.page_width_inches * self.dpi
        )

        height_zoom = available_height / (
            self.page_height_inches * self.dpi
        )

        self.zoom = min(
            width_zoom,
            height_zoom,
        )

        self.zoom = max(
            min(self.zoom, 1.5),
            0.30,
        )

        self.draw_page()

    def show_about(self):
        messagebox.showinfo(
            "About Document Creator",
            "Document Creator\n\n"
            "Python label and document designer",
        )


if __name__ == "__main__":
    app = DocumentCreatorApp()
    app.mainloop()