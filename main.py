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


def _init_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
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

        # Content area
        content = ttk.Frame(main_frame, padding=16)
        content.pack(side="left", fill="both", expand=True)

        ttk.Label(content, text="Colaboradores cadastrados", font=("Segoe UI", 11, "bold")).pack(anchor="w", pady=(0, 8))

        tree_frame = ttk.Frame(content)
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
        ttk.Label(content, textvariable=self.status_var, foreground="gray").pack(anchor="w", pady=(8, 0))

    def _toggle_menu(self):
        if self._menu_aberto:
            self._submenu_frame.pack_forget()
            self._hamburger_btn.config(text="☰  Dados pessoais")
        else:
            self._submenu_frame.pack(fill="x", after=self._hamburger_btn)
            self._hamburger_btn.config(text="☰  Dados pessoais  ▲")
        self._menu_aberto = not self._menu_aberto

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
