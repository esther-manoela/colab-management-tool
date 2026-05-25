# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```powershell
python main.py
```

No install step is needed beyond a standard Python 3 environment with tkinter (bundled with CPython on Windows).

## Architecture

Single-file Python desktop app (`main.py`) using **tkinter** for the GUI and **SQLite** (`colaboradores.db`, created on first run) for persistence.

### Key classes

| Class | Role |
|---|---|
| `App(tk.Tk)` | Main window. Owns the DB connection (`self.conn`) and the in-memory list `self.colaboradores` (list of dicts). All CRUD methods live here. |
| `AdicionarColaboradorWindow(tk.Toplevel)` | Modal dialog for both adding and editing a collaborator. Calls back into `App.adicionar_colaborador` or `App.editar_colaborador`. |
| `ExibirDadosWindow(tk.Toplevel)` | Read-only modal that displays all fields for a selected collaborator. |

### Data flow

`self.colaboradores` (list of dicts) is the in-memory source of truth. It must stay in sync with both the SQLite table and the `ttk.Treeview` widget. Every CRUD operation updates all three together: run the SQL, commit, mutate `self.colaboradores`, then update the tree item.

The Treeview uses positional indexing (`self.tree.index(item)`) to map a selected row back to its entry in `self.colaboradores` — the two must always stay in the same order.

### Schema

Table `colaboradores`: `id` (PK), `nome` (required), `val_passaporte`, `tel_pessoal`, `contato_emergencia`, `tel_emergencia` (all TEXT, default `''`).

### UI language

All UI text and field names are in Brazilian Portuguese.
