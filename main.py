import sqlite3
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox

DB_PATH = Path(__file__).parent / "colaboradores.db"

COLS = ("Nome", "Val. Passaporte", "Tel. Pessoal", "Contato Emergencia", "Tel. Emergencia")
FIELDS = [
    ("Nome do colaborador:", "nome"),
    ("Validade do Passaporte:", "val_passaporte"),
    ("Telefone pessoal:", "tel_pessoal"),
    ("Contato de emergencia:", "contato_emergencia"),
    ("Telefone do contato de emergencia:", "tel_emergencia"),
]

SKILL_COLS = ("Nome", "C#", "C++", "WinUI", "Python")
SKILL_KEYS = ("csharp", "cpp", "winui", "python")


def _init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS colaboradores (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            nome             TEXT NOT NULL,
            val_passaporte   TEXT DEFAULT '',
            tel_pessoal      TEXT DEFAULT '',
            contato_emergencia TEXT DEFAULT '',
            tel_emergencia   TEXT DEFAULT ''
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            colaborador_id INTEGER PRIMARY KEY,
            csharp  INTEGER DEFAULT 0,
            cpp     INTEGER DEFAULT 0,
            winui   INTEGER DEFAULT 0,
            python  INTEGER DEFAULT 0,
            FOREIGN KEY (colaborador_id) REFERENCES colaboradores(id) ON DELETE CASCADE
        )
    """)
    conn.commit()
    return conn


class ExibirDadosWindow(tk.Toplevel):
    def __init__(self, parent, colaborador: dict):
        super().__init__(parent)
        self.title("Dados do Colaborador")
        self.geometry("420x480")
        self.resizable(False, False)
        self.grab_set()

        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        for label, key in FIELDS:
            ttk.Label(frame, text=label, font=("Segoe UI", 9, "bold")).pack(anchor="w")
            ttk.Label(
                frame,
                text=colaborador[key] or "—",
                font=("Segoe UI", 10),
                foreground="#2c3e50",
            ).pack(anchor="w", pady=(2, 12))

        ttk.Button(frame, text="Fechar", command=self.destroy).pack(anchor="e")
        self._center(parent)

    def _center(self, parent):
        self.update_idletasks()
        px = parent.winfo_x() + parent.winfo_width() // 2
        py = parent.winfo_y() + parent.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px - w // 2}+{py - h // 2}")


class AdicionarColaboradorWindow(tk.Toplevel):
    def __init__(self, parent, colaborador=None, index=None):
        super().__init__(parent)
        self.colaborador = colaborador
        self.index = index
        self.title("Editar Colaborador" if colaborador else "Adicionar Novo Colaborador")
        self.geometry("420x520")
        self.resizable(False, False)
        self.grab_set()

        self._build_ui()
        self._center(parent)

    def _build_ui(self):
        frame = ttk.Frame(self, padding=20)
        frame.pack(fill="both", expand=True)

        self.vars = {}
        for label, key in FIELDS:
            ttk.Label(frame, text=label).pack(anchor="w")
            var = tk.StringVar(value=self.colaborador[key] if self.colaborador else "")
            ttk.Entry(frame, textvariable=var, width=44).pack(fill="x", pady=(4, 12))
            self.vars[key] = var

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(anchor="e", pady=(4, 0))
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="right", padx=(8, 0))
        ttk.Button(btn_frame, text="Salvar", command=self._salvar).pack(side="right")

    def _salvar(self):
        nome = self.vars["nome"].get().strip()
        if not nome:
            messagebox.showwarning("Campo obrigatorio", "O nome do colaborador e obrigatorio.", parent=self)
            return
        colaborador = {key: self.vars[key].get().strip() for _, key in FIELDS}
        if self.index is not None:
            self.master.editar_colaborador(self.index, colaborador)
        else:
            self.master.adicionar_colaborador(colaborador)
        self.destroy()

    def _center(self, parent):
        self.update_idletasks()
        px = parent.winfo_x() + parent.winfo_width() // 2
        py = parent.winfo_y() + parent.winfo_height() // 2
        w, h = self.winfo_width(), self.winfo_height()
        self.geometry(f"+{px - w // 2}+{py - h // 2}")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Colab Management Tool")
        self.geometry("900x450")
        self.minsize(600, 350)

        self.conn = _init_db()
        self.colaboradores = []
        self._build_ui()
        self._carregar_colaboradores()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _carregar_colaboradores(self):
        rows = self.conn.execute(
            "SELECT id, nome, val_passaporte, tel_pessoal, contato_emergencia, tel_emergencia FROM colaboradores"
        ).fetchall()
        for row in rows:
            c = dict(row)
            self.colaboradores.append(c)
            self.tree.insert("", "end", values=self._row_values(c))
        self._atualizar_status()

    def _on_close(self):
        self.conn.close()
        self.destroy()

    def _build_ui(self):
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True)

        # Sidebar
        sidebar = tk.Frame(main_frame, bg="#2c3e50", width=160)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar, text="Menu", bg="#2c3e50", fg="white",
            font=("Segoe UI", 12, "bold"), pady=16,
        ).pack(fill="x")

        ttk.Separator(sidebar, orient="horizontal").pack(fill="x")

        btn_cfg = dict(
            bg="#2c3e50", fg="white",
            activebackground="#34495e", activeforeground="white",
            relief="flat", bd=0,
            font=("Segoe UI", 10), anchor="w",
            padx=16, pady=10, cursor="hand2",
        )
        sub_cfg = dict(
            bg="#243342", fg="#bdc3c7",
            activebackground="#2c3e50", activeforeground="white",
            relief="flat", bd=0,
            font=("Segoe UI", 9), anchor="w",
            padx=28, pady=8, cursor="hand2",
        )

        self._menu_aberto = False
        self._submenu_frame = tk.Frame(sidebar, bg="#243342")

        tk.Button(self._submenu_frame, text="  Exibir Dados", command=self._exibir_dados, **sub_cfg).pack(fill="x")
        tk.Button(self._submenu_frame, text="+ Adicionar",    command=self._abrir_adicionar, **sub_cfg).pack(fill="x")
        tk.Button(self._submenu_frame, text="  Editar",       command=self._abrir_editar, **sub_cfg).pack(fill="x")
        tk.Button(self._submenu_frame, text="x Remover",      command=self._remover, **sub_cfg).pack(fill="x")

        self._hamburger_btn = tk.Button(
            sidebar, text="☰  Dados pessoais",
            command=self._toggle_menu, **btn_cfg,
        )
        self._hamburger_btn.pack(fill="x")

        self._skills_menu_aberto = False
        self._submenu_skills_frame = tk.Frame(sidebar, bg="#243342")

        tk.Button(self._submenu_skills_frame, text="  Gerenciar Skills", command=self._show_skills_view, **sub_cfg).pack(fill="x")

        self._skills_btn = tk.Button(
            sidebar, text="⊞  Skills",
            command=self._toggle_skills_menu, **btn_cfg,
        )
        self._skills_btn.pack(fill="x")

        # Content area — two frames, only one visible at a time
        self._content_wrapper = ttk.Frame(main_frame)
        self._content_wrapper.pack(side="left", fill="both", expand=True)

        # --- Colaboradores view ---
        self._view_colaboradores = ttk.Frame(self._content_wrapper, padding=16)
        self._view_colaboradores.pack(fill="both", expand=True)

        ttk.Label(self._view_colaboradores, text="Colaboradores cadastrados", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))

        tree_frame = ttk.Frame(self._view_colaboradores)
        tree_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(tree_frame, columns=COLS, show="headings", selectmode="browse")
        col_widths = [160, 120, 120, 160, 140]
        for col, w in zip(COLS, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, minwidth=80)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="Nenhum colaborador cadastrado.")
        ttk.Label(self._view_colaboradores, textvariable=self.status_var, foreground="gray").pack(anchor="w", pady=(8, 0))

        # --- Skills view ---
        self._view_skills = ttk.Frame(self._content_wrapper, padding=16)

        ttk.Label(self._view_skills, text="Skills dos Colaboradores", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))

        skills_tree_frame = ttk.Frame(self._view_skills)
        skills_tree_frame.pack(fill="both", expand=True)

        self.skills_tree = ttk.Treeview(skills_tree_frame, columns=SKILL_COLS, show="headings", selectmode="browse")
        skill_col_widths = [200, 80, 80, 80, 80]
        for col, w in zip(SKILL_COLS, skill_col_widths):
            self.skills_tree.heading(col, text=col)
            self.skills_tree.column(col, width=w, minwidth=60, anchor="center")
        self.skills_tree.column("Nome", anchor="w")

        vsb2 = ttk.Scrollbar(skills_tree_frame, orient="vertical", command=self.skills_tree.yview)
        self.skills_tree.configure(yscrollcommand=vsb2.set)

        self.skills_tree.grid(row=0, column=0, sticky="nsew")
        vsb2.grid(row=0, column=1, sticky="ns")
        skills_tree_frame.rowconfigure(0, weight=1)
        skills_tree_frame.columnconfigure(0, weight=1)

        self.skills_tree.bind("<ButtonRelease-1>", self._toggle_skill)

        ttk.Label(self._view_skills, text="Clique em uma celula para marcar/desmarcar a skill.", foreground="gray").pack(anchor="w", pady=(8, 0))

    def _toggle_menu(self):
        self._show_colaboradores_view()
        if self._menu_aberto:
            self._submenu_frame.pack_forget()
            self._hamburger_btn.config(text="☰  Dados pessoais")
        else:
            self._submenu_frame.pack(fill="x", after=self._hamburger_btn)
            self._hamburger_btn.config(text="☰  Dados pessoais  ▲")
        self._menu_aberto = not self._menu_aberto

    def _toggle_skills_menu(self):
        self._show_skills_view()
        if self._skills_menu_aberto:
            self._submenu_skills_frame.pack_forget()
            self._skills_btn.config(text="⊞  Skills")
        else:
            self._submenu_skills_frame.pack(fill="x", after=self._skills_btn)
            self._skills_btn.config(text="⊞  Skills  ▲")
        self._skills_menu_aberto = not self._skills_menu_aberto

    def _show_colaboradores_view(self):
        self._view_skills.pack_forget()
        self._view_colaboradores.pack(fill="both", expand=True)

    def _show_skills_view(self):
        self._view_colaboradores.pack_forget()
        self._view_skills.pack(fill="both", expand=True)
        self._carregar_skills()

    def _carregar_skills(self):
        self.skills_tree.delete(*self.skills_tree.get_children())
        existing = {
            row["colaborador_id"]: dict(row)
            for row in self.conn.execute("SELECT * FROM skills").fetchall()
        }
        for c in self.colaboradores:
            cid = c["id"]
            s = existing.get(cid, {k: 0 for k in SKILL_KEYS})
            values = (c["nome"],) + tuple("✓" if s.get(k, 0) else "✗" for k in SKILL_KEYS)
            self.skills_tree.insert("", "end", iid=str(cid), values=values)

    def _toggle_skill(self, event):
        region = self.skills_tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        col_id = self.skills_tree.identify_column(event.x)
        col_index = int(col_id[1:]) - 1  # #1=0, #2=1, ...
        if col_index == 0:
            return
        item = self.skills_tree.identify_row(event.y)
        if not item:
            return
        skill_key = SKILL_KEYS[col_index - 1]
        collab_id = int(item)
        current_values = list(self.skills_tree.item(item, "values"))
        new_val = 0 if current_values[col_index] == "✓" else 1
        self.conn.execute(
            f"INSERT INTO skills (colaborador_id, {skill_key}) VALUES (?, ?) "
            f"ON CONFLICT(colaborador_id) DO UPDATE SET {skill_key}=excluded.{skill_key}",
            (collab_id, new_val),
        )
        self.conn.commit()
        current_values[col_index] = "✓" if new_val else "✗"
        self.skills_tree.item(item, values=current_values)

    def _exibir_dados(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showinfo("Selecione um colaborador", "Selecione um colaborador na lista para exibir.")
            return
        index = self.tree.index(selecionado[0])
        ExibirDadosWindow(self, self.colaboradores[index])

    def _abrir_adicionar(self):
        AdicionarColaboradorWindow(self)

    def _abrir_editar(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showinfo("Selecione um colaborador", "Selecione um colaborador na lista para editar.")
            return
        index = self.tree.index(selecionado[0])
        AdicionarColaboradorWindow(self, colaborador=self.colaboradores[index], index=index)

    def _remover(self):
        selecionado = self.tree.selection()
        if not selecionado:
            messagebox.showinfo("Selecione um colaborador", "Selecione um colaborador na lista para remover.")
            return
        index = self.tree.index(selecionado[0])
        nome = self.colaboradores[index]["nome"]
        if messagebox.askyesno("Confirmar remocao", f"Deseja remover '{nome}'?"):
            self.conn.execute("DELETE FROM colaboradores WHERE id = ?", (self.colaboradores[index]["id"],))
            self.conn.commit()
            self.colaboradores.pop(index)
            self.tree.delete(selecionado[0])
            self._atualizar_status()

    def _row_values(self, c: dict) -> tuple:
        return (c["nome"], c["val_passaporte"],
                c["tel_pessoal"], c["contato_emergencia"], c["tel_emergencia"])

    def adicionar_colaborador(self, colaborador: dict):
        cur = self.conn.execute(
            "INSERT INTO colaboradores (nome, val_passaporte, tel_pessoal, contato_emergencia, tel_emergencia) VALUES (?, ?, ?, ?, ?)",
            (colaborador["nome"], colaborador["val_passaporte"], colaborador["tel_pessoal"],
             colaborador["contato_emergencia"], colaborador["tel_emergencia"]),
        )
        self.conn.commit()
        colaborador["id"] = cur.lastrowid
        self.colaboradores.append(colaborador)
        self.tree.insert("", "end", values=self._row_values(colaborador))
        self._atualizar_status()

    def editar_colaborador(self, index: int, colaborador: dict):
        colaborador["id"] = self.colaboradores[index]["id"]
        self.conn.execute(
            "UPDATE colaboradores SET nome=?, val_passaporte=?, tel_pessoal=?, contato_emergencia=?, tel_emergencia=? WHERE id=?",
            (colaborador["nome"], colaborador["val_passaporte"], colaborador["tel_pessoal"],
             colaborador["contato_emergencia"], colaborador["tel_emergencia"], colaborador["id"]),
        )
        self.conn.commit()
        self.colaboradores[index] = colaborador
        item = self.tree.get_children()[index]
        self.tree.item(item, values=self._row_values(colaborador))

    def _atualizar_status(self):
        total = len(self.colaboradores)
        if total == 0:
            self.status_var.set("Nenhum colaborador cadastrado.")
        else:
            self.status_var.set(f"{total} colaborador{'es' if total > 1 else ''} cadastrado{'s' if total > 1 else ''}.")


if __name__ == "__main__":
    app = App()
    app.mainloop()
