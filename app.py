import json
import os
import uuid
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime, timedelta

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(APP_DIR, "foodwise_data.json")

BG = "#F4F7F1"
PAPER = "#FFFFFF"
INK = "#172B24"
MUTED = "#718078"
GREEN = "#187A55"
DEEP = "#123C2B"
LIME = "#D9F27C"
LINE = "#E5EBE2"
RED = "#B95134"
AMBER = "#9A6816"

CATEGORIES = ["Fruit", "Vegetable", "Dairy", "Meat / Fish", "Bakery", "Grains", "Other"]
ICONS = {"Fruit": "🍓", "Vegetable": "🥦", "Dairy": "🥛", "Meat / Fish": "🐟",
         "Bakery": "🍞", "Grains": "🌾", "Other": "🥫"}
MEALS = {
    "Fruit": ("Fruit bowl or smoothie", "Combine with yoghurt or oats if available."),
    "Vegetable": ("Quick vegetable bowl", "Try it in soup, an omelette, pasta, or a stir-fry."),
    "Dairy": ("Breakfast or creamy sauce", "Use in breakfast or a sauce if still within safe-use guidance."),
    "Meat / Fish": ("Plan a protein meal", "Plan a complete meal and follow safe storage and cooking guidance."),
    "Bakery": ("Toast or breadcrumbs", "Try toast, croutons, or breadcrumbs if still suitable."),
    "Grains": ("Grain bowl", "Pair with vegetables and a protein already in your kitchen."),
    "Other": ("Kitchen-clear-out meal", "Build a meal around this item and ingredients already on hand.")
}

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data.setdefault("items", [])
            data.setdefault("shopping", [])
            data.setdefault("budget", 0)
            return data
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {"items": [], "shopping": [], "budget": 0}

def save_data(data):
    temp = DATA_FILE + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(temp, DATA_FILE)

def days_left(item):
    try:
        return (datetime.strptime(item["expiry"], "%Y-%m-%d").date() - date.today()).days
    except (ValueError, KeyError, TypeError):
        return 999

def money(value):
    return f"AED {float(value or 0):,.2f}"

class FoodWiseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FoodWise — Your Smart Kitchen")
        self.root.geometry("1180x780")
        self.root.minsize(850, 620)
        self.root.configure(bg=BG)
        self.data = load_data()
        self.current_page = "Overview"
        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Your kitchen, made smarter.")
        self.setup_style()
        self.build_shell()
        self.show_page("Overview")

    def setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Treeview", background=PAPER, fieldbackground=PAPER, foreground=INK,
                        rowheight=34, bordercolor=LINE, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background="#E9EEE6", foreground=DEEP,
                        font=("Segoe UI", 10, "bold"), relief="flat")
        style.map("Treeview", background=[("selected", "#D9F0E2")], foreground=[("selected", INK)])
        style.configure("TCombobox", padding=7)
        style.configure("TEntry", padding=7)

    def build_shell(self):
        top = tk.Frame(self.root, bg=PAPER, highlightbackground=LINE, highlightthickness=1)
        top.pack(fill="x")
        brand = tk.Frame(top, bg=PAPER)
        brand.pack(side="left", padx=22, pady=14)
        tk.Label(brand, text="✳", bg=GREEN, fg="white", font=("Segoe UI", 18, "bold"),
                 width=2, pady=3).pack(side="left", padx=(0, 10))
        tk.Label(brand, text="FoodWise", bg=PAPER, fg=INK,
                 font=("Segoe UI", 19, "bold")).pack(side="left")
        tk.Label(top, text="SMART KITCHEN  •  DESKTOP APP", bg=PAPER, fg=MUTED,
                 font=("Segoe UI", 9, "bold")).pack(side="right", padx=22)

        hero = tk.Frame(self.root, bg=GREEN)
        hero.pack(fill="x", padx=22, pady=(18, 12))
        left = tk.Frame(hero, bg=GREEN)
        left.pack(side="left", fill="both", expand=True, padx=24, pady=18)
        tk.Label(left, text="YOUR KITCHEN, MADE SMARTER", bg=GREEN, fg=LIME,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        tk.Label(left, text="Waste less. Save more.", bg=GREEN, fg="white",
                 font=("Segoe UI", 25, "bold")).pack(anchor="w", pady=(5, 3))
        tk.Label(left, text="Track food, plan meals, and avoid buying duplicates.",
                 bg=GREEN, fg="#E0EEE6", font=("Segoe UI", 10)).pack(anchor="w")
        tk.Label(hero, text="🥑", bg=GREEN, fg="white", font=("Segoe UI Emoji", 45)).pack(side="right", padx=28)

        self.nav = tk.Frame(self.root, bg=BG)
        self.nav.pack(fill="x", padx=22, pady=(0, 12))
        self.nav_buttons = {}
        for name in ["Overview", "Food inventory", "Meal planner", "Shopping list", "Budget & impact"]:
            b = tk.Button(self.nav, text=name, command=lambda n=name: self.show_page(n),
                          font=("Segoe UI", 9, "bold"), relief="flat", bd=0, padx=13, pady=9,
                          cursor="hand2", bg=DEEP if name == "Overview" else "#E9EEE6",
                          fg="white" if name == "Overview" else "#5C6D62",
                          activebackground=GREEN, activeforeground="white")
            b.pack(side="left", padx=(0, 6))
            self.nav_buttons[name] = b

        self.content = tk.Frame(self.root, bg=BG)
        self.content.pack(fill="both", expand=True, padx=22, pady=(0, 10))
        footer = tk.Frame(self.root, bg=BG)
        footer.pack(fill="x", padx=22, pady=(0, 10))
        tk.Label(footer, text="FoodWise student prototype • Your data stays on this computer",
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack(side="left")
        tk.Label(footer, textvariable=self.status_var, bg=BG, fg=GREEN,
                 font=("Segoe UI", 8, "bold")).pack(side="right")

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def show_page(self, name):
        self.current_page = name
        for n, b in self.nav_buttons.items():
            b.configure(bg=DEEP if n == name else "#E9EEE6",
                        fg="white" if n == name else "#5C6D62")
        self.clear_content()
        if name == "Overview":
            self.page_overview()
        elif name == "Food inventory":
            self.page_inventory()
        elif name == "Meal planner":
            self.page_meals()
        elif name == "Shopping list":
            self.page_shopping()
        else:
            self.page_budget()

    def card(self, parent, title=None):
        frame = tk.Frame(parent, bg=PAPER, highlightbackground=LINE, highlightthickness=1)
        if title:
            tk.Label(frame, text=title, bg=PAPER, fg=INK,
                     font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=17, pady=(15, 10))
        return frame

    def button(self, parent, text, command, primary=True):
        return tk.Button(parent, text=text, command=command, relief="flat", bd=0,
                         bg=GREEN if primary else "#E9EEE6",
                         fg="white" if primary else INK,
                         activebackground=DEEP if primary else "#DDE6DB",
                         activeforeground="white" if primary else INK,
                         font=("Segoe UI", 9, "bold"), padx=12, pady=8, cursor="hand2")

    def section_title(self, parent, title, subtitle=None):
        tk.Label(parent, text=title, bg=BG, fg=INK,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(parent, text=subtitle, bg=BG, fg=MUTED,
                     font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 12))

    def enriched(self):
        items = self.data["items"]
        return sorted(items, key=days_left)

    def urgency(self, item):
        d = days_left(item)
        if d < 0:
            return "Past date"
        if d <= 2:
            return "Use soon"
        if d <= 5:
            return "Coming up"
        return "Fresh"

    def total_value(self):
        return sum(float(i.get("price") or 0) for i in self.data["items"])

    def stat_card(self, parent, title, value, note, col):
        f = tk.Frame(parent, bg=PAPER, highlightbackground=LINE, highlightthickness=1)
        f.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 6, 0), pady=0)
        tk.Label(f, text=title, bg=PAPER, fg=MUTED, font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=13, pady=(12, 2))
        tk.Label(f, text=value, bg=PAPER, fg=INK, font=("Segoe UI", 21, "bold")).pack(anchor="w", padx=13)
        tk.Label(f, text=note, bg=PAPER, fg=GREEN, font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=13, pady=(0, 12))

    def page_overview(self):
        items = self.enriched()
        urgent = sum(1 for i in items if days_left(i) <= 2)
        shopping_count = sum(not s.get("done") for s in self.data["shopping"])
        stats = tk.Frame(self.content, bg=BG)
        stats.pack(fill="x", pady=(0, 12))
        for c in range(4):
            stats.grid_columnconfigure(c, weight=1, uniform="stats")
        self.stat_card(stats, "FOOD ITEMS", str(len(items)), "Know what you own", 0)
        self.stat_card(stats, "USE SOON", str(urgent), "Prioritise these items", 1)
        self.stat_card(stats, "FOOD VALUE", money(self.total_value()), "Estimated inventory value", 2)
        self.stat_card(stats, "SHOPPING LIST", str(shopping_count), "Items to remember", 3)

        body = tk.Frame(self.content, bg=BG)
        body.pack(fill="both", expand=True)
        body.grid_columnconfigure(0, weight=1, uniform="body")
        body.grid_columnconfigure(1, weight=1, uniform="body")
        form_card = self.card(body, "Add food to your kitchen")
        form_card.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        right = self.card(body, "Use these first")
        right.grid(row=0, column=1, sticky="nsew", padx=(7, 0))
        self.build_food_form(form_card)
        tk.Label(right, text="Items with the shortest time left appear first.",
                 bg=PAPER, fg=MUTED, font=("Segoe UI", 9)).pack(anchor="w", padx=17, pady=(0, 10))
        if items:
            for item in items[:4]:
                self.food_row(right, item, compact=True)
            first = items[0]
            title, desc = MEALS.get(first.get("category", "Other"), MEALS["Other"])
            idea = tk.Frame(right, bg=DEEP)
            idea.pack(fill="x", padx=14, pady=(9, 14))
            tk.Label(idea, text="✦ SMART MEAL IDEA", bg=DEEP, fg=LIME,
                     font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
            tk.Label(idea, text=title, bg=DEEP, fg="white",
                     font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12)
            tk.Label(idea, text=f"Use {first['name']}: {desc}", bg=DEEP, fg="#D0DED5",
                     font=("Segoe UI", 8), wraplength=340, justify="left").pack(anchor="w", padx=12, pady=(3, 10))
        else:
            tk.Label(right, text="🧺\nYour kitchen list is empty\nAdd food or load sample data.",
                     bg=PAPER, fg=MUTED, font=("Segoe UI", 10), justify="center").pack(expand=True, pady=25)
        self.button(right, "Load demo data", self.load_demo, primary=False).pack(anchor="w", padx=14, pady=(0, 14))

    def build_food_form(self, parent):
        form = tk.Frame(parent, bg=PAPER)
        form.pack(fill="x", padx=17, pady=(0, 15))
        self.name_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Fruit")
        self.expiry_var = tk.StringVar(value=(date.today() + timedelta(days=3)).isoformat())
        self.price_var = tk.StringVar()
        self.quantity_var = tk.StringVar()
        fields = [
            ("Food name", self.name_var, "e.g. Strawberries"),
            ("Use-by date (YYYY-MM-DD)", self.expiry_var, "2026-10-17"),
            ("Value (AED)", self.price_var, "e.g. 12"),
            ("Quantity", self.quantity_var, "e.g. 1 box")
        ]
        for idx, (label, var, hint) in enumerate(fields):
            r, c = divmod(idx, 2)
            cell = tk.Frame(form, bg=PAPER)
            cell.grid(row=r, column=c, sticky="ew", padx=(0, 8 if c == 0 else 0), pady=5)
            tk.Label(cell, text=label, bg=PAPER, fg="#506057",
                     font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 4))
            ent = ttk.Entry(cell, textvariable=var)
            ent.pack(fill="x")
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)
        cell = tk.Frame(form, bg=PAPER)
        cell.grid(row=2, column=0, columnspan=2, sticky="ew", pady=5)
        tk.Label(cell, text="Category", bg=PAPER, fg="#506057",
                 font=("Segoe UI", 8, "bold")).pack(anchor="w", pady=(0, 4))
        ttk.Combobox(cell, textvariable=self.category_var, values=CATEGORIES,
                     state="readonly").pack(fill="x")
        self.button(form, "＋ Add to inventory", self.add_food).grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        tk.Label(form, text="Smart priority: check items with the shortest dates first. This app cannot tell if food is safe.",
                 bg="#F6F9EC", fg="#51613C", wraplength=420, justify="left",
                 font=("Segoe UI", 8), padx=9, pady=9).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(10, 0))

    def add_food(self):
        name = self.name_var.get().strip()
        expiry = self.expiry_var.get().strip()
        if not name:
            messagebox.showwarning("Missing food name", "Please enter a food name.")
            return
        try:
            datetime.strptime(expiry, "%Y-%m-%d")
        except ValueError:
            messagebox.showwarning("Invalid date", "Enter the date in YYYY-MM-DD format, for example 2026-10-17.")
            return
        try:
            price = max(0, float(self.price_var.get() or 0))
        except ValueError:
            messagebox.showwarning("Invalid price", "Enter a number for the value, or leave it blank.")
            return
        self.data["items"].append({
            "id": uuid.uuid4().hex[:12], "name": name, "category": self.category_var.get(),
            "expiry": expiry, "price": price, "quantity": self.quantity_var.get().strip()
        })
        save_data(self.data)
        self.status_var.set(f"Added {name} to your kitchen.")
        self.show_page("Overview")

    def food_row(self, parent, item, compact=False):
        d = days_left(item)
        status = self.urgency(item)
        row = tk.Frame(parent, bg=PAPER)
        row.pack(fill="x", padx=14, pady=4)
        tk.Label(row, text=ICONS.get(item.get("category", "Other"), "🥫"),
                 bg="#F0F6E7", fg=INK, font=("Segoe UI Emoji", 17),
                 width=3, pady=4).pack(side="left", padx=(0, 8))
        middle = tk.Frame(row, bg=PAPER)
        middle.pack(side="left", fill="x", expand=True)
        tk.Label(middle, text=item.get("name", "Food item"), bg=PAPER, fg=INK,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w")
        day_text = f"{abs(d)} day(s) past date" if d < 0 else ("Use today" if d == 0 else f"{d} day(s) left")
        tk.Label(middle, text=f"{item.get('quantity') or 'Quantity not set'} · {day_text} · {money(item.get('price', 0))}",
                 bg=PAPER, fg=MUTED, font=("Segoe UI", 8)).pack(anchor="w")
        color = RED if d <= 2 else (AMBER if d <= 5 else GREEN)
        tk.Label(row, text=status, bg="#FFF0DF" if d <= 2 else ("#F5F3D8" if d <= 5 else "#E5F5E9"),
                 fg=color, font=("Segoe UI", 7, "bold"), padx=6, pady=5).pack(side="right", padx=(5, 0))
        if not compact:
            self.button(row, "Remove", lambda i=item["id"]: self.remove_food(i), primary=False).pack(side="right", padx=5)
        tk.Frame(parent, bg=LINE, height=1).pack(fill="x", padx=14, pady=(3, 0))

    def remove_food(self, item_id):
        item = next((i for i in self.data["items"] if i.get("id") == item_id), None)
        if not item:
            return
        if messagebox.askyesno("Remove food", f"Remove {item.get('name')} from your inventory?"):
            self.data["items"] = [i for i in self.data["items"] if i.get("id") != item_id]
            save_data(self.data)
            self.show_page(self.current_page)

    def page_inventory(self):
        self.section_title(self.content, "Food inventory", "Search, review, and manage everything in your kitchen.")
        toolbar = tk.Frame(self.content, bg=BG)
        toolbar.pack(fill="x", pady=(0, 10))
        self.search_var = tk.StringVar()
        ent = ttk.Entry(toolbar, textvariable=self.search_var)
        ent.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.button(toolbar, "Search", self.render_inventory, primary=False).pack(side="left")
        self.button(toolbar, "Add food", lambda: self.show_page("Overview")).pack(side="left", padx=(8, 0))
        self.inventory_holder = tk.Frame(self.content, bg=BG)
        self.inventory_holder.pack(fill="both", expand=True)
        ent.bind("<KeyRelease>", lambda _e: self.render_inventory())
        self.render_inventory()

    def render_inventory(self):
        if not hasattr(self, "inventory_holder") or not self.inventory_holder.winfo_exists():
            return
        for w in self.inventory_holder.winfo_children():
            w.destroy()
        q = self.search_var.get().strip().casefold()
        items = [i for i in self.enriched() if q in (i.get("name", "") + " " + i.get("category", "")).casefold()]
        card = self.card(self.inventory_holder)
        card.pack(fill="both", expand=True)
        tk.Label(card, text=f"{len(items)} ITEM(S)", bg=PAPER, fg=GREEN,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=15, pady=12)
        if not items:
            tk.Label(card, text="No matching food. Add an item from Overview.",
                     bg=PAPER, fg=MUTED, font=("Segoe UI", 10)).pack(pady=35)
        else:
            for item in items:
                self.food_row(card, item)

    def page_meals(self):
        self.section_title(self.content, "Meal planner", "Simple meal ideas based on the ingredients you have.")
        items = self.enriched()
        left = self.card(self.content, "Your ingredient-based ideas")
        left.pack(side="left", fill="both", expand=True, padx=(0, 7))
        right = self.card(self.content, "A practical plan")
        right.pack(side="left", fill="both", expand=True, padx=(7, 0))
        if items:
            for item in items[:8]:
                title, desc = MEALS.get(item.get("category", "Other"), MEALS["Other"])
                row = tk.Frame(left, bg=PAPER)
                row.pack(fill="x", padx=15, pady=9)
                tk.Label(row, text=ICONS.get(item.get("category", "Other"), "🥫"),
                         bg=PAPER, font=("Segoe UI Emoji", 20)).pack(side="left", padx=(0, 10))
                box = tk.Frame(row, bg=PAPER)
                box.pack(side="left", fill="x", expand=True)
                tk.Label(box, text=title, bg=PAPER, fg=INK,
                         font=("Segoe UI", 10, "bold")).pack(anchor="w")
                tk.Label(box, text=f"Use {item['name']}: {desc}", bg=PAPER, fg=MUTED,
                         font=("Segoe UI", 8), wraplength=350, justify="left").pack(anchor="w", pady=3)
                if days_left(item) <= 2:
                    tk.Label(box, text="PRIORITY INGREDIENT", bg=PAPER, fg=GREEN,
                             font=("Segoe UI", 7, "bold")).pack(anchor="w")
                tk.Frame(left, bg=LINE, height=1).pack(fill="x", padx=14)
        else:
            tk.Label(left, text="Add food to see meal ideas.", bg=PAPER, fg=MUTED).pack(pady=30)
        steps = ["1. Use ingredients with the shortest time left first.",
                 "2. Choose meals that use more than one ingredient.",
                 "3. Add only missing ingredients to your shopping list.",
                 "4. Update inventory after using food."]
        for step in steps:
            tk.Label(right, text=step, bg="#F6F9EC", fg="#51613C",
                     font=("Segoe UI", 10), wraplength=400, justify="left",
                     padx=12, pady=12).pack(fill="x", padx=15, pady=6)
        tk.Label(right, text="Safety note: these are suggestions, not a food-safety check. Follow storage guidance and discard food when in doubt.",
                 bg=PAPER, fg=MUTED, font=("Segoe UI", 8), wraplength=380,
                 justify="left").pack(anchor="w", padx=15, pady=12)

    def page_shopping(self):
        self.section_title(self.content, "Shopping list", "Remember what you need and check for duplicates before buying.")
        card = self.card(self.content, "Items to buy")
        card.pack(fill="both", expand=True)
        form = tk.Frame(card, bg=PAPER)
        form.pack(fill="x", padx=15, pady=(0, 12))
        self.shop_var = tk.StringVar()
        ent = ttk.Entry(form, textvariable=self.shop_var)
        ent.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.button(form, "＋ Add item", self.add_shopping).pack(side="left")
        ent.bind("<Return>", lambda _e: self.add_shopping())
        if not self.data["shopping"]:
            tk.Label(card, text="Your shopping list is empty.", bg=PAPER, fg=MUTED).pack(pady=20)
        for item in self.data["shopping"]:
            row = tk.Frame(card, bg=PAPER)
            row.pack(fill="x", padx=16, pady=5)
            var = tk.BooleanVar(value=bool(item.get("done")))
            cb = tk.Checkbutton(row, variable=var, bg=PAPER, activebackground=PAPER,
                                command=lambda i=item["id"], v=var: self.toggle_shopping(i, v.get()))
            cb.pack(side="left")
            tk.Label(row, text=item["name"], bg=PAPER,
                     fg=MUTED if item.get("done") else INK,
                     font=("Segoe UI", 10, "overstrike" if item.get("done") else "normal")).pack(side="left", fill="x", expand=True)
            self.button(row, "Remove", lambda i=item["id"]: self.delete_shopping(i), primary=False).pack(side="right")
            tk.Frame(card, bg=LINE, height=1).pack(fill="x", padx=15, pady=(3, 0))
        inventory_names = {i.get("name", "").strip().casefold() for i in self.data["items"]}
        duplicates = [s["name"] for s in self.data["shopping"] if not s.get("done") and s["name"].strip().casefold() in inventory_names]
        msg = ("Already in inventory: " + ", ".join(duplicates) + ". Check before buying." if duplicates
               else "FoodWise checks exact-name matches against your inventory to help prevent duplicate purchases.")
        tk.Label(card, text="💡 " + msg, bg="#F6F9EC", fg="#51613C",
                 font=("Segoe UI", 9), wraplength=800, justify="left",
                 padx=10, pady=10).pack(fill="x", padx=15, pady=12)
        self.button(card, "Remove checked items", self.clear_checked, primary=False).pack(anchor="w", padx=15, pady=(0, 15))

    def add_shopping(self):
        name = self.shop_var.get().strip()
        if not name:
            return
        self.data["shopping"].append({"id": uuid.uuid4().hex[:12], "name": name[:60], "done": False, "price": 0})
        save_data(self.data)
        self.status_var.set(f"Added {name} to shopping list.")
        self.show_page("Shopping list")

    def toggle_shopping(self, item_id, done):
        for item in self.data["shopping"]:
            if item.get("id") == item_id:
                item["done"] = done
                break
        save_data(self.data)
        self.show_page("Shopping list")

    def delete_shopping(self, item_id):
        self.data["shopping"] = [s for s in self.data["shopping"] if s.get("id") != item_id]
        save_data(self.data)
        self.show_page("Shopping list")

    def clear_checked(self):
        self.data["shopping"] = [s for s in self.data["shopping"] if not s.get("done")]
        save_data(self.data)
        self.show_page("Shopping list")

    def page_budget(self):
        self.section_title(self.content, "Budget & impact", "Understand the value of food you have and what needs attention.")
        body = tk.Frame(self.content, bg=BG)
        body.pack(fill="both", expand=True)
        left = self.card(body, "Budget snapshot")
        left.pack(side="left", fill="both", expand=True, padx=(0, 7))
        right = self.card(body, "Waste-reduction snapshot")
        right.pack(side="left", fill="both", expand=True, padx=(7, 0))
        shopping_value = sum(float(s.get("price") or 0) for s in self.data["shopping"] if not s.get("done"))
        for label, value in [("Inventory value", money(self.total_value())), ("Shopping estimate", money(shopping_value))]:
            row = tk.Frame(left, bg=PAPER)
            row.pack(fill="x", padx=16, pady=10)
            tk.Label(row, text=label, bg=PAPER, fg=MUTED, font=("Segoe UI", 10)).pack(side="left")
            tk.Label(row, text=value, bg=PAPER, fg=INK, font=("Segoe UI", 11, "bold")).pack(side="right")
        tk.Label(left, text="Monthly food budget (AED)", bg=PAPER, fg=INK,
                 font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(15, 5))
        self.budget_var = tk.StringVar(value=str(self.data.get("budget") or ""))
        ttk.Entry(left, textvariable=self.budget_var).pack(fill="x", padx=16)
        self.button(left, "Save budget", self.save_budget).pack(anchor="w", padx=16, pady=10)
        budget = float(self.data.get("budget") or 0)
        budget_message = (f"Your target is {money(budget)}. Compare your shopping estimate before buying."
                          if budget else "Set a monthly target to help plan your spending.")
        tk.Label(left, text=budget_message, bg="#F6F9EC", fg="#51613C",
                 wraplength=420, justify="left", font=("Segoe UI", 9),
                 padx=10, pady=10).pack(fill="x", padx=16, pady=(3, 16))
        items = self.enriched()
        soon = [i for i in items if days_left(i) <= 3]
        soon_value = sum(float(i.get("price") or 0) for i in soon)
        self.metric_row(right, "Items tracked", str(len(items)))
        self.metric_row(right, "Items with 3 days or less", str(len(soon)))
        self.metric_row(right, "Value needing attention", money(soon_value))
        tk.Label(right, text="This is an estimate of tracked food value needing attention, not proof that food was saved or an exact carbon calculation.",
                 bg=PAPER, fg=MUTED, wraplength=400, justify="left",
                 font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=18)

    def metric_row(self, parent, label, value):
        row = tk.Frame(parent, bg=PAPER)
        row.pack(fill="x", padx=16, pady=12)
        tk.Label(row, text=label, bg=PAPER, fg=MUTED, font=("Segoe UI", 10)).pack(side="left")
        tk.Label(row, text=value, bg=PAPER, fg=INK, font=("Segoe UI", 11, "bold")).pack(side="right")
        tk.Frame(parent, bg=LINE, height=1).pack(fill="x", padx=16)

    def save_budget(self):
        try:
            value = max(0.0, float(self.budget_var.get() or 0))
        except ValueError:
            messagebox.showwarning("Invalid budget", "Enter a valid number for the monthly budget.")
            return
        self.data["budget"] = value
        save_data(self.data)
        self.status_var.set("Budget saved.")
        self.show_page("Budget & impact")

    def load_demo(self):
        today = date.today()
        self.data["items"] = [
            {"id": "demo-a", "name": "Strawberries", "category": "Fruit", "expiry": (today + timedelta(days=1)).isoformat(), "price": 12, "quantity": "1 box"},
            {"id": "demo-b", "name": "Spinach", "category": "Vegetable", "expiry": (today + timedelta(days=2)).isoformat(), "price": 8, "quantity": "1 bag"},
            {"id": "demo-c", "name": "Milk", "category": "Dairy", "expiry": (today + timedelta(days=5)).isoformat(), "price": 7, "quantity": "1 carton"},
            {"id": "demo-d", "name": "Bread", "category": "Bakery", "expiry": (today + timedelta(days=4)).isoformat(), "price": 6, "quantity": "1 loaf"}
        ]
        self.data["shopping"] = [{"id": "shop-demo", "name": "Oats", "done": False, "price": 8}]
        save_data(self.data)
        self.status_var.set("Demo data loaded. Explore the tabs.")
        self.show_page("Overview")

def main():
    root = tk.Tk()
    FoodWiseApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
