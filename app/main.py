import tkinter as tk
from tkinter import ttk, messagebox, colorchooser, font as tkfont


# ============================================================
# Constants
# ============================================================

DPI = 96

PAGE_WIDTH_INCHES = 8.5
PAGE_HEIGHT_INCHES = 11.0

TEMPLATES = {
    "Plain Document": {
        "columns": 0,
        "rows": 0,
        "left_margin": 0,
        "top_margin": 0,
        "label_width": 0,
        "label_height": 0,
        "horizontal_gap": 0,
        "vertical_gap": 0,
    },
    "Avery 5160": {
        "columns": 3,
        "rows": 10,
        "left_margin": 0.1875,
        "top_margin": 0.5,
        "label_width": 2.625,
        "label_height": 1.0,
        "horizontal_gap": 0.125,
        "vertical_gap": 0.0,
    },
    "Avery 5163": {
        "columns": 2,
        "rows": 5,
        "left_margin": 0.5,
        "top_margin": 0.5,
        "label_width": 4.0,
        "label_height": 2.0,
        "horizontal_gap": 0.125,
        "vertical_gap": 0.0,
    },
}


class DocumentCreatorApp:
    # ========================================================
    # Initialization
    # ========================================================

    def __init__(self, root):
        self.root = root
        self.root.title("Document Creator")
        self.root.geometry("1280x820")
        self.root.minsize(1000, 650)

        self.dpi = DPI
        self.zoom = 0.85

        self.selected_label = 1

        # Saved document objects remain available after redraws.
        self.document_objects = []
        self.selected_object_index = None
        self.dragging_object = False
        self.drag_start_x = 0
        self.drag_start_y = 0

        self.label_text_var = tk.StringVar(value="Sample Label")
        self.selected_label_var = tk.StringVar(value="Selected Label: 1")
        self.start_label_var = tk.StringVar(value="Label 1")
        self.template_var = tk.StringVar(value="Plain Document")
        self.object_count_var = tk.StringVar(value="0")
        self.status_var = tk.StringVar(value="Ready")

        # Text formatting defaults used when new text is added.
        self.text_font_family_var = tk.StringVar(value="Arial")
        self.text_font_size_var = tk.StringVar(value="12")
        self.text_bold_var = tk.BooleanVar(value=False)
        self.text_italic_var = tk.BooleanVar(value=False)
        self.text_underline_var = tk.BooleanVar(value=False)
        self.text_alignment = "Left"
        self.text_color = "#222222"
        self.alignment_buttons = {}
        self.text_edit_entry = None
        self.text_edit_window = None

        self.create_menu()
        self.create_main_layout()
        self.draw_page()

    # ========================================================
    # Menus
    # ========================================================

    def create_menu(self):
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="New", command=self.new_document)
        file_menu.add_command(label="Open", command=self.not_implemented)
        file_menu.add_command(label="Save", command=self.not_implemented)
        file_menu.add_command(label="Save As...", command=self.not_implemented)
        file_menu.add_separator()
        file_menu.add_command(
            label="Print Preview",
            command=self.print_preview,
        )
        file_menu.add_command(label="Print", command=self.not_implemented)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)

        options_menu = tk.Menu(menu_bar, tearoff=False)
        options_menu.add_command(
            label="Document Settings",
            command=self.not_implemented,
        )
        options_menu.add_command(
            label="Application Options",
            command=self.not_implemented,
        )
        menu_bar.add_cascade(label="Options", menu=options_menu)

        database_menu = tk.Menu(menu_bar, tearoff=False)
        database_menu.add_command(
            label="Import CSV",
            command=self.not_implemented,
        )
        database_menu.add_command(
            label="Manage Data Sources",
            command=self.not_implemented,
        )
        menu_bar.add_cascade(label="Database", menu=database_menu)

        objects_menu = tk.Menu(menu_bar, tearoff=False)
        objects_menu.add_command(label="Add Text", command=self.add_text)
        objects_menu.add_command(
            label="Add Barcode Placeholder",
            command=self.add_barcode,
        )
        objects_menu.add_separator()
        objects_menu.add_command(
            label="Delete Selected Object",
            command=self.delete_selected_object,
        )
        menu_bar.add_cascade(label="Objects", menu=objects_menu)

        view_menu = tk.Menu(menu_bar, tearoff=False)
        view_menu.add_command(label="Zoom In", command=self.zoom_in)
        view_menu.add_command(label="Zoom Out", command=self.zoom_out)
        view_menu.add_command(label="Fit Page", command=self.fit_page)
        menu_bar.add_cascade(label="View", menu=view_menu)

        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="About", command=self.show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menu_bar)

    # ========================================================
    # Main layout
    # ========================================================

    def create_main_layout(self):
        self.create_formatting_toolbar()

        main_frame = ttk.Frame(self.root, padding=8)
        main_frame.pack(fill=tk.BOTH, expand=True)

        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        self.create_left_panel(main_frame)
        self.create_canvas_panel(main_frame)
        self.create_right_panel(main_frame)

        ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=(6, 3),
        ).pack(side=tk.BOTTOM, fill=tk.X)

    def create_formatting_toolbar(self):
        """Create a familiar word-processor style formatting toolbar."""
        toolbar = ttk.Frame(self.root, padding=(8, 5))
        toolbar.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(toolbar, text="Font").pack(side=tk.LEFT, padx=(0, 4))

        try:
            families = sorted(set(tkfont.families()))
        except tk.TclError:
            families = ["Arial", "Calibri", "Times New Roman", "Courier New"]

        self.font_family_combo = ttk.Combobox(
            toolbar,
            textvariable=self.text_font_family_var,
            values=families,
            state="readonly",
            width=18,
        )
        self.font_family_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.font_family_combo.bind(
            "<<ComboboxSelected>>",
            self.toolbar_font_family_selected,
        )

        self.font_size_combo = ttk.Combobox(
            toolbar,
            textvariable=self.text_font_size_var,
            values=[str(size) for size in (8, 9, 10, 11, 12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 72)],
            width=5,
        )
        self.font_size_combo.pack(side=tk.LEFT, padx=(0, 5))
        self.font_size_combo.bind(
            "<<ComboboxSelected>>",
            self.toolbar_size_selected,
        )
        self.font_size_combo.bind("<Return>", self.toolbar_font_changed)
        # Do not apply formatting on FocusOut: it can steal focus while the
        # user is choosing a value from the dropdown and cancel that choice.
        self.font_size_combo.bind("<KeyRelease>", self.toolbar_size_key_release)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=5
        )

        ttk.Checkbutton(
            toolbar,
            text="B",
            variable=self.text_bold_var,
            command=self.toolbar_toggle_format,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Checkbutton(
            toolbar,
            text="I",
            variable=self.text_italic_var,
            command=self.toolbar_toggle_format,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Checkbutton(
            toolbar,
            text="U",
            variable=self.text_underline_var,
            command=self.toolbar_toggle_format,
        ).pack(side=tk.LEFT, padx=2)

        self.text_color_button = tk.Button(
            toolbar,
            text="A",
            width=3,
            command=self.choose_text_color,
            font=("Arial", 10, "bold"),
            relief=tk.RAISED,
        )
        self.text_color_button.pack(side=tk.LEFT, padx=(4, 6))
        self.update_color_button()

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=5
        )

        ttk.Label(toolbar, text="Alignment").pack(side=tk.LEFT, padx=(0, 4))

        for alignment in ("Left", "Center", "Right"):
            button = tk.Canvas(
                toolbar,
                width=30,
                height=24,
                highlightthickness=1,
                highlightbackground="#b5b5b5",
                background="#f0f0f0",
                cursor="hand2",
            )
            button.pack(side=tk.LEFT, padx=2)
            button.bind(
                "<Button-1>",
                lambda event, value=alignment: self.set_text_alignment(value),
            )
            self.alignment_buttons[alignment] = button
            self.draw_alignment_icon(alignment)

        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(
            side=tk.LEFT, fill=tk.Y, padx=8
        )

        ttk.Button(
            toolbar,
            text="Add Text",
            command=self.add_text,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Button(
            toolbar,
            text="Delete",
            command=self.delete_selected_object,
        ).pack(side=tk.LEFT, padx=2)

        ttk.Label(
            toolbar,
            text="  Select text to format; changes also become the defaults for new text.",
        ).pack(side=tk.LEFT, padx=(8, 0))

    def get_toolbar_font_size(self):
        try:
            return max(1, int(self.text_font_size_var.get()))
        except (TypeError, ValueError):
            self.text_font_size_var.set("12")
            return 12

    def update_color_button(self):
        if hasattr(self, "text_color_button"):
            self.text_color_button.configure(fg=self.text_color, activeforeground=self.text_color)

    def choose_text_color(self):
        color = colorchooser.askcolor(
            color=self.text_color,
            title="Choose Text Color",
            parent=self.root,
        )
        if color and color[1]:
            self.text_color = color[1]
            self.update_color_button()
            self.toolbar_format_changed()

    def update_toolbar_from_selected_object(self):
        if self.selected_object_index is None:
            self.update_alignment_buttons()
            return
        if not (0 <= self.selected_object_index < len(self.document_objects)):
            return

        item = self.document_objects[self.selected_object_index]
        if item.get("type") != "text":
            return

        self.text_font_family_var.set(item.get("font_family", item.get("font", ("Arial", 12))[0]))
        self.text_font_size_var.set(str(item.get("font_size", item.get("font", ("Arial", 12))[1])))
        self.text_bold_var.set(item.get("bold", False))
        self.text_italic_var.set(item.get("italic", False))
        self.text_underline_var.set(item.get("underline", False))
        self.text_color = item.get("fill", "#222222")
        self.text_alignment = item.get("alignment", "Left")
        self.update_color_button()
        self.update_alignment_buttons()

    def toolbar_font_family_selected(self, event=None):
        """Apply the font family chosen from the dropdown immediately."""
        # Read directly from the combobox so the handler uses the user's
        # actual selection, even if Tk has not yet refreshed the StringVar.
        family = self.font_family_combo.get().strip()
        if not family:
            return

        self.text_font_family_var.set(family)

        # If the text editor is open, save its text before redrawing the page.
        if self.text_edit_entry is not None:
            self.finish_text_edit(save=True)

        if self.selected_object_index is None:
            self.status_var.set(
                f"New text will use the {family} font."
            )
            return

        if not (0 <= self.selected_object_index < len(self.document_objects)):
            return

        item = self.document_objects[self.selected_object_index]
        if item.get("type") != "text":
            self.status_var.set("Select a text object to change its font.")
            return

        size = self.get_toolbar_font_size()
        item["font_family"] = family
        item["font_size"] = size
        item["font"] = (family, size)

        self.draw_page()
        self.canvas.focus_set()
        self.status_var.set(f"Font changed to {family}.")

    def toolbar_size_selected(self, event=None):
        """Apply a selected drop-down size after Tk finishes its focus events."""
        # Tk can deliver FocusOut and ComboboxSelected close together. Waiting
        # until idle lets the selected value settle before we apply it.
        self.root.after_idle(self.apply_selected_font_size)

    def apply_selected_font_size(self):
        """Apply the font-size value currently displayed in the size combo."""
        value = self.font_size_combo.get().strip()
        if not value.isdigit():
            return

        size = int(value)
        if size < 1 or size > 200:
            return

        self.text_font_size_var.set(str(size))

        # Finish inline editing before updating the saved object and redrawing.
        if self.text_edit_entry is not None:
            self.finish_text_edit(save=True)

        if self.selected_object_index is None:
            self.status_var.set(f"New text will use {size}-point font.")
            return

        if not (0 <= self.selected_object_index < len(self.document_objects)):
            return

        item = self.document_objects[self.selected_object_index]
        if item.get("type") != "text":
            self.status_var.set("Select a text object to change its font size.")
            return

        family = self.text_font_family_var.get().strip() or "Arial"
        item["font_family"] = family
        item["font_size"] = size
        item["font"] = (family, size)

        self.draw_page()
        self.canvas.focus_set()
        self.status_var.set(f"Font size changed to {size}.")

    def toolbar_size_key_release(self, event=None):
        """Apply a typed font size to the selected text as soon as it is valid."""
        value = self.font_size_combo.get().strip()
        if not value.isdigit():
            return

        size = int(value)
        if size < 1 or size > 200:
            return

        self.text_font_size_var.set(str(size))
        self.toolbar_format_changed()

    def toolbar_format_changed(self):
        self.text_alignment = getattr(self, "text_alignment", "Left")

        if self.selected_object_index is None:
            self.update_color_button()
            self.update_alignment_buttons()
            return

        if not (0 <= self.selected_object_index < len(self.document_objects)):
            return

        item = self.document_objects[self.selected_object_index]
        if item.get("type") != "text":
            return

        family = self.text_font_family_var.get() or "Arial"
        size = self.get_toolbar_font_size()
        item["font_family"] = family
        item["font_size"] = size
        item["font"] = (family, size)
        item["bold"] = self.text_bold_var.get()
        item["italic"] = self.text_italic_var.get()
        item["underline"] = self.text_underline_var.get()
        item["fill"] = self.text_color
        item["alignment"] = self.text_alignment

        self.update_color_button()
        self.update_alignment_buttons()
        self.apply_alignment_to_item(item)
        self.draw_page()
        self.status_var.set("Text formatting updated.")

    def toolbar_font_changed(self, event=None):
        """Immediately apply font family and size to selected text."""
        if self.selected_object_index is None:
            return

        if not (0 <= self.selected_object_index < len(self.document_objects)):
            return

        obj = self.document_objects[self.selected_object_index]
        if obj.get("type") != "text":
            return

        family = self.text_font_family_var.get().strip() or "Arial"

        try:
            size = int(self.text_font_size_var.get())
        except (TypeError, ValueError):
            return

        size = max(1, min(size, 200))

        obj["font_family"] = family
        obj["font_size"] = size
        obj["font"] = (family, size)

        self.draw_page()
        self.canvas.focus_set()

    def toolbar_toggle_format(self):
        """Immediately apply bold, italic, and underline to selected text."""
        if self.selected_object_index is None:
            return

        if not (0 <= self.selected_object_index < len(self.document_objects)):
            return

        obj = self.document_objects[self.selected_object_index]
        if obj.get("type") != "text":
            return

        obj["bold"] = bool(self.text_bold_var.get())
        obj["italic"] = bool(self.text_italic_var.get())
        obj["underline"] = bool(self.text_underline_var.get())
        obj["fill"] = self.text_color
        obj["alignment"] = self.text_alignment

        self.draw_page()
        self.canvas.focus_set()

    def set_text_alignment(self, alignment):
        self.text_alignment = alignment
        self.update_alignment_buttons()

        if self.selected_object_index is None:
            self.status_var.set(f"New text will be {alignment.lower()} aligned.")
            return

        if not (0 <= self.selected_object_index < len(self.document_objects)):
            return

        item = self.document_objects[self.selected_object_index]
        if item.get("type") != "text":
            return

        item["alignment"] = alignment
        self.apply_alignment_to_item(item)
        self.draw_page()
        self.status_var.set(f"Text aligned {alignment.lower()}.")

    def get_alignment_region(self, item):
        template_name = self.template_var.get()
        if template_name == "Plain Document":
            return 0.50, PAGE_WIDTH_INCHES - 0.50

        template = TEMPLATES[template_name]
        object_x = item.get("x", 0)
        object_y = item.get("y", 0)
        total_labels = template["columns"] * template["rows"]

        for number in range(1, total_labels + 1):
            index = number - 1
            row = index // template["columns"]
            column = index % template["columns"]
            label_x = template["left_margin"] + column * (template["label_width"] + template["horizontal_gap"])
            label_y = template["top_margin"] + row * (template["label_height"] + template["vertical_gap"])

            if (label_x <= object_x <= label_x + template["label_width"] and
                    label_y <= object_y <= label_y + template["label_height"]):
                return label_x, label_x + template["label_width"]

        return 0.50, PAGE_WIDTH_INCHES - 0.50

    def apply_alignment_to_item(self, item):
        alignment = item.get("alignment", "Left")
        left, right = self.get_alignment_region(item)

        if alignment == "Left":
            item["x"] = left
        elif alignment == "Center":
            item["x"] = (left + right) / 2
        elif alignment == "Right":
            item["x"] = right

    def draw_alignment_icon(self, alignment):
        """Draw a simple Word/LibreOffice-style alignment icon."""
        canvas = self.alignment_buttons[alignment]
        canvas.delete("all")

        widths = [18, 12, 18, 14]
        y_positions = [5, 9, 13, 17]
        canvas_width = 30

        for width, y in zip(widths, y_positions):
            if alignment == "Left":
                x1 = 4
            elif alignment == "Center":
                x1 = (canvas_width - width) / 2
            else:
                x1 = canvas_width - width - 4

            canvas.create_line(
                x1, y, x1 + width, y,
                fill="#222222",
                width=2,
            )

        self.update_alignment_buttons()

    def update_alignment_buttons(self):
        for alignment, canvas in self.alignment_buttons.items():
            if alignment == self.text_alignment:
                canvas.configure(
                    background="#d7eaff",
                    highlightbackground="#0066cc",
                )
            else:
                canvas.configure(
                    background="#f0f0f0",
                    highlightbackground="#b5b5b5",
                )

    def create_left_panel(self, parent):
        panel = ttk.LabelFrame(
            parent,
            text="Documents and Templates",
            padding=8,
        )
        panel.grid(row=0, column=0, sticky="ns", padx=(0, 8))

        ttk.Label(
            panel,
            text="Document",
            font=("Arial", 10, "bold"),
        ).pack(anchor=tk.W)

        ttk.Button(
            panel,
            text="New Document",
            command=self.new_document,
            width=24,
        ).pack(fill=tk.X, pady=(6, 14))

        ttk.Label(
            panel,
            text="Template",
            font=("Arial", 10, "bold"),
        ).pack(anchor=tk.W)

        ttk.Combobox(
            panel,
            textvariable=self.template_var,
            values=list(TEMPLATES.keys()),
            state="readonly",
            width=22,
        ).pack(fill=tk.X, pady=(6, 4))

        ttk.Button(
            panel,
            text="Apply Template",
            command=self.apply_template,
            width=24,
        ).pack(fill=tk.X, pady=(0, 14))

        ttk.Separator(panel).pack(fill=tk.X, pady=6)

        ttk.Label(
            panel,
            text="Objects",
            font=("Arial", 10, "bold"),
        ).pack(anchor=tk.W)

        ttk.Button(
            panel,
            text="Add Barcode Placeholder",
            command=self.add_barcode,
            width=24,
        ).pack(fill=tk.X, pady=(6, 4))

        ttk.Label(
            panel,
            text="Tip: double-click text to edit it.",
            wraplength=175,
        ).pack(anchor=tk.W, pady=(8, 0))

    def create_canvas_panel(self, parent):
        panel = ttk.LabelFrame(
            parent,
            text="Document Designer",
            padding=8,
        )
        panel.grid(row=0, column=1, sticky="nsew")
        panel.rowconfigure(0, weight=1)
        panel.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            panel,
            background="#777777",
            highlightthickness=0,
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        vertical_scrollbar = ttk.Scrollbar(
            panel,
            orient=tk.VERTICAL,
            command=self.canvas.yview,
        )
        vertical_scrollbar.grid(row=0, column=1, sticky="ns")

        horizontal_scrollbar = ttk.Scrollbar(
            panel,
            orient=tk.HORIZONTAL,
            command=self.canvas.xview,
        )
        horizontal_scrollbar.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(
            xscrollcommand=horizontal_scrollbar.set,
            yscrollcommand=vertical_scrollbar.set,
        )

        self.canvas.bind("<Button-1>", self.canvas_click)
        self.canvas.bind("<Double-Button-1>", self.canvas_double_click)
        self.canvas.bind("<Delete>", self.delete_selected_object)
        self.canvas.bind("<B1-Motion>", self.canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.canvas_release)

    def create_right_panel(self, parent):
        panel = ttk.LabelFrame(
            parent,
            text="Properties and Status",
            padding=8,
        )
        panel.grid(row=0, column=2, sticky="ns", padx=(8, 0))

        ttk.Label(
            panel,
            textvariable=self.selected_label_var,
            font=("Arial", 10, "bold"),
        ).pack(anchor=tk.W, pady=(0, 12))

        ttk.Label(panel, text="Start Printing At").pack(anchor=tk.W)

        values = [f"Label {number}" for number in range(1, 31)]

        self.start_label_combo = ttk.Combobox(
            panel,
            textvariable=self.start_label_var,
            values=values,
            state="readonly",
            width=20,
        )
        self.start_label_combo.pack(fill=tk.X, pady=(6, 12))
        self.start_label_combo.bind(
            "<<ComboboxSelected>>",
            self.start_label_changed,
        )

        ttk.Separator(panel).pack(fill=tk.X, pady=8)

        ttk.Label(
            panel,
            text="View",
            font=("Arial", 10, "bold"),
        ).pack(anchor=tk.W)

        ttk.Button(
            panel,
            text="Zoom In",
            command=self.zoom_in,
            width=22,
        ).pack(fill=tk.X, pady=(6, 4))

        ttk.Button(
            panel,
            text="Zoom Out",
            command=self.zoom_out,
            width=22,
        ).pack(fill=tk.X, pady=4)

        ttk.Button(
            panel,
            text="Fit Page",
            command=self.fit_page,
            width=22,
        ).pack(fill=tk.X, pady=4)

        ttk.Separator(panel).pack(fill=tk.X, pady=12)

        ttk.Label(panel, text="Objects on Page").pack(anchor=tk.W)

        ttk.Label(
            panel,
            textvariable=self.object_count_var,
            font=("Arial", 14, "bold"),
        ).pack(anchor=tk.W, pady=(4, 12))

        ttk.Button(
            panel,
            text="Print Preview",
            command=self.print_preview,
            width=22,
        ).pack(fill=tk.X)

    # ========================================================
    # Drawing
    # ========================================================

    def draw_page(self):
        self.canvas.delete("all")

        page_width = PAGE_WIDTH_INCHES * self.dpi * self.zoom
        page_height = PAGE_HEIGHT_INCHES * self.dpi * self.zoom
        padding = 35

        self.page_left = padding
        self.page_top = padding

        page_right = self.page_left + page_width
        page_bottom = self.page_top + page_height

        self.canvas.create_rectangle(
            self.page_left + 5,
            self.page_top + 5,
            page_right + 5,
            page_bottom + 5,
            fill="#444444",
            outline="",
        )

        self.canvas.create_rectangle(
            self.page_left,
            self.page_top,
            page_right,
            page_bottom,
            fill="white",
            outline="#222222",
        )

        self.draw_label_guides()
        self.draw_document_objects()

        self.canvas.configure(
            scrollregion=(
                0,
                0,
                page_right + padding,
                page_bottom + padding,
            )
        )

        self.object_count_var.set(str(len(self.document_objects)))

    def draw_label_guides(self):
        template = TEMPLATES[self.template_var.get()]

        columns = template["columns"]
        rows = template["rows"]

        if columns == 0 or rows == 0:
            return

        for number in range(1, columns * rows + 1):
            index = number - 1
            row = index // columns
            column = index % columns

            x = template["left_margin"] + column * (
                template["label_width"] + template["horizontal_gap"]
            )
            y = template["top_margin"] + row * (
                template["label_height"] + template["vertical_gap"]
            )

            x1 = self.page_left + x * self.dpi * self.zoom
            y1 = self.page_top + y * self.dpi * self.zoom
            x2 = x1 + template["label_width"] * self.dpi * self.zoom
            y2 = y1 + template["label_height"] * self.dpi * self.zoom

            tag = f"label_{number}"
            fill = "#e9f3ff" if number == self.selected_label else ""

            self.canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                outline="#72a7d8",
                fill=fill,
                tags=(tag, "label"),
            )

            self.canvas.create_text(
                x1 + 4,
                y1 + 3,
                text=str(number),
                anchor=tk.NW,
                fill="#6d8ca8",
                font=("Arial", max(7, int(8 * self.zoom))),
                tags=(tag, "label_number"),
            )

    def draw_document_objects(self):
        for index, item in enumerate(self.document_objects):
            x = self.page_left + (
                item.get("x", 0) * self.dpi * self.zoom
            )
            y = self.page_top + (
                item.get("y", 0) * self.dpi * self.zoom
            )

            object_tag = f"object_{index}"
            tags = ("document_object", object_tag)

            if item["type"] == "text":
                font_name, font_size = item.get(
                    "font",
                    (item.get("font_family", "Arial"), item.get("font_size", 12)),
                )

                if item.get("font_family"):
                    font_name = item.get("font_family")
                if item.get("font_size"):
                    font_size = item.get("font_size")

                font_weight = "bold" if item.get("bold", False) else "normal"
                font_slant = "italic" if item.get("italic", False) else "roman"

                alignment = item.get("alignment", "Left")
                anchor = {
                    "Left": tk.NW,
                    "Center": tk.N,
                    "Right": tk.NE,
                }.get(alignment, tk.NW)

                self.canvas.create_text(
                    x,
                    y,
                    text=item.get("text", ""),
                    anchor=anchor,
                    fill=item.get("fill", "#222222"),
                    font=tkfont.Font(
                        family=font_name,
                        size=max(1, int(font_size * self.zoom)),
                        weight=font_weight,
                        slant=font_slant,
                        underline=item.get("underline", False),
                    ),
                    tags=tags,
                )

            elif item["type"] == "barcode":
                self.draw_barcode_placeholder(
                    x,
                    y,
                    tags=tags,
                )

        self.draw_object_selection()

    def draw_object_selection(self):
        self.canvas.delete("selection_box")

        if self.selected_object_index is None:
            return

        if not (0 <= self.selected_object_index < len(self.document_objects)):
            return

        object_tag = f"object_{self.selected_object_index}"
        bbox = self.canvas.bbox(object_tag)

        if not bbox:
            return

        x1, y1, x2, y2 = bbox
        margin = max(3, int(4 * self.zoom))

        self.canvas.create_rectangle(
            x1 - margin,
            y1 - margin,
            x2 + margin,
            y2 + margin,
            outline="#0066cc",
            dash=(4, 2),
            width=max(1, int(self.zoom)),
            tags=("selection_box",),
        )
        self.canvas.tag_raise("selection_box")

    def draw_barcode_placeholder(self, x, y, tags=("document_object",)):
        width = 1.65 * self.dpi * self.zoom
        height = 0.42 * self.dpi * self.zoom

        self.canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill="white",
            outline="#222222",
            tags=tags,
        )

        bar_widths = [2, 1, 1, 3, 1, 2, 1, 1, 3, 2, 1, 2, 3, 1]

        current_x = x + 5 * self.zoom

        for index, bar_width in enumerate(bar_widths):
            scaled_width = max(1, bar_width * self.zoom)

            self.canvas.create_rectangle(
                current_x,
                y + 5 * self.zoom,
                current_x + scaled_width,
                y + height - 5 * self.zoom,
                fill="#111111" if index % 2 == 0 else "white",
                outline="",
                tags=tags,
            )

            current_x += scaled_width

        self.canvas.create_text(
            x + width / 2,
            y + height + 4 * self.zoom,
            text="CODE 128 PLACEHOLDER",
            anchor=tk.N,
            fill="#444444",
            font=("Arial", max(7, int(7 * self.zoom))),
            tags=tags,
        )

    # ========================================================
    # Object actions
    # ========================================================

    def add_text(self):
        """Add a new text object and immediately make it editable."""
        font_size = self.get_toolbar_font_size()

        item = {
            "type": "text",
            "text": "New Text",
            "x": 0.50,
            "y": 1.05,
            "font": (self.text_font_family_var.get(), font_size),
            "font_family": self.text_font_family_var.get(),
            "font_size": font_size,
            "bold": self.text_bold_var.get(),
            "italic": self.text_italic_var.get(),
            "underline": self.text_underline_var.get(),
            "fill": self.text_color,
            "alignment": self.text_alignment,
        }

        self.document_objects.append(item)
        self.selected_object_index = len(self.document_objects) - 1
        self.apply_alignment_to_item(item)

        self.draw_page()
        self.status_var.set("New text added. Type your text, then press Enter.")
        self.root.after(50, lambda: self.begin_text_edit(self.selected_object_index))

    def add_barcode(self):
        self.document_objects.append(
            {
                "type": "barcode",
                "x": 0.50,
                "y": 1.45,
            }
        )

        self.draw_page()
        self.status_var.set("Barcode placeholder added.")

    # ========================================================
    # Document actions
    # ========================================================

    def new_document(self):
        self.finish_text_edit(save=True)
        self.document_objects.clear()
        self.selected_object_index = None
        self.dragging_object = False
        self.template_var.set("Plain Document")
        self.selected_label = 1
        self.selected_label_var.set("Selected Label: 1")
        self.start_label_var.set("Label 1")
        self.label_text_var.set("Sample Label")

        self.draw_page()
        self.status_var.set("New plain document created.")

    def apply_template(self):
        template_name = self.template_var.get()

        self.finish_text_edit(save=True)
        self.document_objects.clear()
        self.selected_object_index = None
        self.dragging_object = False
        self.selected_label = 1
        self.selected_label_var.set("Selected Label: 1")
        self.start_label_var.set("Label 1")

        self.draw_page()
        self.status_var.set(f"{template_name} template applied.")

    # ========================================================
    # Selection and view
    # ========================================================

    def canvas_double_click(self, event):
        """Begin editing a text object directly on the page."""
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        object_index = self.get_object_at_canvas_position(x, y)

        if object_index is None:
            return

        item = self.document_objects[object_index]
        if item.get("type") != "text":
            return

        self.selected_object_index = object_index
        self.update_toolbar_from_selected_object()
        self.draw_page()
        self.begin_text_edit(object_index)

    def begin_text_edit(self, object_index):
        """Place an editable Entry over the selected text object."""
        if not (0 <= object_index < len(self.document_objects)):
            return

        item = self.document_objects[object_index]
        if item.get("type") != "text":
            return

        self.finish_text_edit(save=True)
        self.selected_object_index = object_index

        bbox = self.canvas.bbox(f"object_{object_index}")
        if not bbox:
            return

        font_name = item.get("font_family", "Arial")
        font_size = max(1, int(item.get("font_size", 12) * self.zoom))
        font_weight = "bold" if item.get("bold", False) else "normal"
        font_slant = "italic" if item.get("italic", False) else "roman"
        edit_font = tkfont.Font(
            family=font_name,
            size=font_size,
            weight=font_weight,
            slant=font_slant,
            underline=item.get("underline", False),
        )

        x1, y1, x2, y2 = bbox
        width = max(100, int(x2 - x1 + 24))
        height = max(28, int(y2 - y1 + 14))

        justify = {
            "Left": tk.LEFT,
            "Center": tk.CENTER,
            "Right": tk.RIGHT,
        }.get(item.get("alignment", "Left"), tk.LEFT)

        entry = tk.Entry(
            self.canvas,
            font=edit_font,
            fg=item.get("fill", "#222222"),
            bg="white",
            relief=tk.SOLID,
            bd=1,
            justify=justify,
        )
        entry.insert(0, item.get("text", ""))
        entry.select_range(0, tk.END)

        self.text_edit_entry = entry
        self.text_edit_window = self.canvas.create_window(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            window=entry,
            width=width,
            height=height,
            tags=("text_editor",),
        )

        entry.bind("<Return>", self.finish_text_edit)
        entry.bind("<Escape>", self.cancel_text_edit)
        entry.bind("<FocusOut>", self.finish_text_edit)
        entry.focus_set()

        self.status_var.set(
            "Editing text. Press Enter to save or Escape to cancel."
        )

    def finish_text_edit(self, event=None, save=True):
        """Finish direct text editing and save the new text."""
        entry = self.text_edit_entry
        if entry is None:
            return "break" if event is not None else None

        object_index = self.selected_object_index
        if save and object_index is not None and 0 <= object_index < len(self.document_objects):
            item = self.document_objects[object_index]
            if item.get("type") == "text":
                new_text = entry.get().strip()
                item["text"] = new_text if new_text else "New Text"

        if self.text_edit_window is not None:
            try:
                self.canvas.delete(self.text_edit_window)
            except tk.TclError:
                pass

        self.text_edit_entry = None
        self.text_edit_window = None
        self.draw_page()

        if save:
            self.status_var.set("Text updated.")

        return "break" if event is not None else None

    def cancel_text_edit(self, event=None):
        """Cancel direct text editing without changing the stored text."""
        if self.text_edit_entry is None:
            return "break"

        if self.text_edit_window is not None:
            try:
                self.canvas.delete(self.text_edit_window)
            except tk.TclError:
                pass

        self.text_edit_entry = None
        self.text_edit_window = None
        self.draw_page()
        self.status_var.set("Text edit cancelled.")
        return "break"

    def canvas_click(self, event):
        self.canvas.focus_set()

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # Document objects are selected before label guides so that an
        # object placed on a label can be clicked and moved directly.
        object_index = self.get_object_at_canvas_position(x, y)

        if object_index is not None:
            self.selected_object_index = object_index
            self.update_toolbar_from_selected_object()
            self.dragging_object = True
            self.drag_start_x = x
            self.drag_start_y = y
            self.draw_object_selection()
            self.status_var.set(
                f"Object {object_index + 1} selected. Drag to move it."
            )
            return

        self.selected_object_index = None
        self.dragging_object = False
        self.draw_object_selection()

        if self.template_var.get() == "Plain Document":
            self.status_var.set("No object selected.")
            return

        page_x = (x - self.page_left) / (self.dpi * self.zoom)
        page_y = (y - self.page_top) / (self.dpi * self.zoom)

        template = TEMPLATES[self.template_var.get()]
        total_labels = template["columns"] * template["rows"]

        for number in range(1, total_labels + 1):
            index = number - 1
            row = index // template["columns"]
            column = index % template["columns"]

            label_x = template["left_margin"] + column * (
                template["label_width"] + template["horizontal_gap"]
            )
            label_y = template["top_margin"] + row * (
                template["label_height"] + template["vertical_gap"]
            )

            if (
                label_x <= page_x <= label_x + template["label_width"]
                and label_y <= page_y <= label_y + template["label_height"]
            ):
                self.selected_label = number
                self.selected_label_var.set(
                    f"Selected Label: {number}"
                )
                self.start_label_var.set(f"Label {number}")
                self.draw_page()
                self.status_var.set(f"Label {number} selected.")
                return

        self.status_var.set("No object or label selected.")

    def delete_selected_object(self, event=None):
        """Delete the currently selected document object."""
        self.finish_text_edit(save=True)
        if self.selected_object_index is None:
            self.status_var.set("No object selected to delete.")
            return "break"

        if not (0 <= self.selected_object_index < len(self.document_objects)):
            self.selected_object_index = None
            self.dragging_object = False
            self.draw_page()
            self.status_var.set("No object selected to delete.")
            return "break"

        deleted_index = self.selected_object_index
        deleted_object = self.document_objects[deleted_index]
        deleted_type = deleted_object.get("type", "object")

        del self.document_objects[deleted_index]
        self.selected_object_index = None
        self.dragging_object = False
        self.text_font_family_var.set("Arial")
        self.text_font_size_var.set("12")
        self.text_bold_var.set(False)
        self.text_italic_var.set(False)
        self.text_underline_var.set(False)
        self.text_color = "#222222"
        self.text_alignment = "Left"
        self.update_color_button()
        self.update_alignment_buttons()

        self.draw_page()
        self.status_var.set(
            f"{deleted_type.capitalize()} object {deleted_index + 1} deleted."
        )

        return "break"

    def get_object_at_canvas_position(self, x, y):
        """Return the topmost document object at a canvas position."""
        overlapping_items = self.canvas.find_overlapping(x, y, x, y)

        for canvas_item in reversed(overlapping_items):
            tags = self.canvas.gettags(canvas_item)

            for tag in tags:
                if tag.startswith("object_"):
                    try:
                        index = int(tag.split("_", 1)[1])
                    except (ValueError, IndexError):
                        continue

                    if 0 <= index < len(self.document_objects):
                        return index

        return None

    def canvas_drag(self, event):
        if not self.dragging_object:
            return

        if self.selected_object_index is None:
            return

        if not (0 <= self.selected_object_index < len(self.document_objects)):
            return

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        delta_x_pixels = x - self.drag_start_x
        delta_y_pixels = y - self.drag_start_y

        if delta_x_pixels == 0 and delta_y_pixels == 0:
            return

        object_tag = f"object_{self.selected_object_index}"
        self.canvas.move(object_tag, delta_x_pixels, delta_y_pixels)
        self.canvas.move("selection_box", delta_x_pixels, delta_y_pixels)

        item = self.document_objects[self.selected_object_index]
        item["x"] += delta_x_pixels / (self.dpi * self.zoom)
        item["y"] += delta_y_pixels / (self.dpi * self.zoom)

        self.drag_start_x = x
        self.drag_start_y = y

        self.status_var.set(
            f"Object {self.selected_object_index + 1} position: "
            f"{item['x']:.2f}, {item['y']:.2f} in"
        )

    def canvas_release(self, event):
        if not self.dragging_object:
            return

        self.dragging_object = False

        # Redraw from the saved page-coordinate model so the canvas and
        # stored object position stay synchronized after dragging.
        self.draw_page()

        if self.selected_object_index is not None:
            item = self.document_objects[self.selected_object_index]
            self.status_var.set(
                f"Object {self.selected_object_index + 1} moved to "
                f"{item['x']:.2f}, {item['y']:.2f} in."
            )

    def start_label_changed(self, event=None):
        try:
            number = int(self.start_label_var.get().split()[-1])
        except (ValueError, IndexError):
            number = 1

        self.selected_label = number
        self.selected_label_var.set(f"Selected Label: {number}")
        self.draw_page()
        self.status_var.set(
            f"Printing will start at Label {number}."
        )

    def zoom_in(self):
        self.zoom = min(2.0, self.zoom + 0.10)
        self.draw_page()
        self.status_var.set(f"Zoom: {int(self.zoom * 100)}%")

    def zoom_out(self):
        self.zoom = max(0.40, self.zoom - 0.10)
        self.draw_page()
        self.status_var.set(f"Zoom: {int(self.zoom * 100)}%")

    def fit_page(self):
        available_width = max(400, self.canvas.winfo_width() - 70)
        available_height = max(400, self.canvas.winfo_height() - 70)

        width_zoom = available_width / (PAGE_WIDTH_INCHES * self.dpi)
        height_zoom = available_height / (PAGE_HEIGHT_INCHES * self.dpi)

        self.zoom = min(width_zoom, height_zoom)
        self.zoom = max(0.40, min(self.zoom, 2.0))

        self.draw_page()
        self.status_var.set(f"Page fitted: {int(self.zoom * 100)}%")

    # ========================================================
    # Dialogs
    # ========================================================

    def print_preview(self):
        messagebox.showinfo(
            "Print Preview",
            (
                "Print preview is planned for a future version.\n\n"
                f"Template: {self.template_var.get()}\n"
                f"Starting label: {self.start_label_var.get()}\n"
                f"Objects: {len(self.document_objects)}"
            ),
        )

    def show_about(self):
        messagebox.showinfo(
            "About Document Creator",
            (
                "Document Creator\n\n"
                "A label and document designer inspired by "
                "Bear Rock Labeler."
            ),
        )

    def not_implemented(self):
        self.status_var.set(
            "This feature is planned for a future version."
        )


def main():
    root = tk.Tk()
    DocumentCreatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
