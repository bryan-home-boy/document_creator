import tkinter as tk
from tkinter import ttk, messagebox


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
            text="Text to Add",
            font=("Arial", 10, "bold"),
        ).pack(anchor=tk.W)

        ttk.Entry(
            panel,
            textvariable=self.label_text_var,
            width=25,
        ).pack(fill=tk.X, pady=(6, 4))

        ttk.Button(
            panel,
            text="Add Text to Page",
            command=self.add_text,
            width=24,
        ).pack(fill=tk.X, pady=(0, 6))

        ttk.Button(
            panel,
            text="Add Barcode Placeholder",
            command=self.add_barcode,
            width=24,
        ).pack(fill=tk.X)

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
                    ("Arial", 12),
                )

                self.canvas.create_text(
                    x,
                    y,
                    text=item.get("text", ""),
                    anchor=tk.NW,
                    fill=item.get("fill", "#222222"),
                    font=(
                        font_name,
                        max(1, int(font_size * self.zoom)),
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
        self.canvas.tag_raise("object_selection")

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
        text = self.label_text_var.get().strip()

        if not text:
            self.status_var.set("Enter text before adding it.")
            return

        self.document_objects.append(
            {
                "type": "text",
                "text": text,
                "x": 0.50,
                "y": 1.05,
                "font": ("Arial", 12),
                "fill": "#222222",
            }
        )

        self.draw_page()
        self.status_var.set(f'Text added: "{text}"')

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

    def canvas_click(self, event):
        self.canvas.focus_set()

        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)

        # Document objects are selected before label guides so that an
        # object placed on a label can be clicked and moved directly.
        object_index = self.get_object_at_canvas_position(x, y)

        if object_index is not None:
            self.selected_object_index = object_index
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
