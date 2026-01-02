import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
import io
import contextlib
import tkinter.font as tkfont
import difflib
import datetime
import queue

# ---------------------------------------------------------------
# Auto-install required third-party modules on first run
# ---------------------------------------------------------------
def ensure_dependencies():
    import importlib
    import subprocess

    required = {
        "requests": "requests",
        "google.generativeai": "google-generativeai",
        "dotenv": "python-dotenv",
    }

    missing = []
    for import_name, pip_name in required.items():
        try:
            importlib.import_module(import_name)
        except ImportError:
            missing.append(pip_name)

    if not missing:
        return

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
    except Exception as e:
        print(f"[ERROR] Failed to auto-install packages {missing}: {e}", file=sys.stderr)


ensure_dependencies()

# Now safe to import
from dotenv import load_dotenv
import google.generativeai as genai  # reserved for possible direct Gemini usage later

# ---------------------------------------------------------------
# Try to import backend in flexible ways
# ---------------------------------------------------------------
backend_set_api_key = None

try:
    from gemini_terminal_bridge import (
        GeminiBridgeSession,
        MODEL_NAME,
        set_api_key as backend_set_api_key,
    )
    BACKEND_NAME = "gemini_terminal_bridge (single-file)"
except (ImportError, AttributeError):
    try:
        from gemini_terminal_bridge.bridge import (
            GeminiBridgeSession,
            MODEL_NAME,
            set_api_key as backend_set_api_key,
        )
        BACKEND_NAME = "gemini_terminal_bridge.bridge (package)"
    except (ImportError, AttributeError):
        # Fallback if something is very wrong, but we expect the above to work
        GeminiBridgeSession = None
        BACKEND_NAME = "gemini_terminal_bridge (ERROR: Session not found)"


MAX_CHARS = 25000


# ---------------------------------------------------------------
# Paths, API key helpers
# ---------------------------------------------------------------
def get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def load_api_key_from_env_file():
    env_path = os.path.join(get_base_dir(), ".env")
    if os.path.exists(env_path):
        try:
            with open(env_path, "r") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        return line.split("=", 1)[1].strip()
        except Exception:
            pass
    return os.environ.get("GEMINI_API_KEY", "")


def save_api_key_to_env_file(new_key: str):
    new_key = (new_key or "").strip()
    if not new_key:
        raise ValueError("API key cannot be empty.")

    env_path = os.path.join(get_base_dir(), ".env")

    lines = []
    if os.path.exists(env_path):
        try:
            with open(env_path, "r") as f:
                lines = f.readlines()
        except Exception:
            pass

    updated = False
    out_lines = []
    for line in lines:
        if line.strip().startswith("GEMINI_API_KEY="):
            out_lines.append(f"GEMINI_API_KEY={new_key}\n")
            updated = True
        else:
            out_lines.append(line)

    if not updated:
        out_lines.append(f"GEMINI_API_KEY={new_key}\n")

    with open(env_path, "w", encoding="utf-8") as f:
        f.writelines(out_lines)


# ---------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------
def extract_last_summary(output: str) -> str:
    marker = "=== SUMMARY FROM GEMINI ==="
    idx = output.rfind(marker)
    if idx == -1:
        tail = output.strip().splitlines()[-15:]
        return "\n".join(tail).strip()

    part = output[idx + len(marker):]
    lines = part.splitlines()

    if lines and not lines[0].strip():
        lines = lines[1:]

    summary_lines = []
    for line in lines:
        if line.strip().startswith("==="):
            break
        summary_lines.append(line)

    summary = "\n".join(summary_lines).strip()
    return summary or "(no summary)"


def extract_commands(output: str) -> str:
    commands = []
    for line in output.splitlines():
        s = line.strip()
        if s.startswith("→ Running:"):
            commands.append(s[len("→ Running:"):].strip())
        elif s.startswith("Command:"):
            commands.append(s[len("Command:"):].strip())

    if not commands:
        return "(no commands found)"
    return "\n".join(commands)


def classify_command_risk(cmd: str):
    c = cmd.strip().lower()
    red_patterns = [
        "rm -rf /",
        "rm -rf / ",
        "mkfs",
        ":(){ :|:& };:",
    ]
    for p in red_patterns:
        if p in c:
            return "RED", "Potentially destructive / system-wiping command"

    if "rm -rf" in c:
        return "RED", "Recursive delete (rm -rf) detected"

    warn_patterns = [
        "sudo ",
        "chmod -r",
        "chown -r",
        "git reset --hard",
        "drop database",
        "truncate table",
        "format ",
    ]
    for p in warn_patterns:
        if p in c:
            return "YELLOW", f"Potentially risky operation ({p.strip()})"

    return "GREEN", "Normal-looking command"


# ---------------------------------------------------------------
# File editor window
# ---------------------------------------------------------------
class FileEditorWindow(tk.Toplevel):
    def __init__(self, master, filepath: str, api_key_provider):
        super().__init__(master)
        self.title(f"File Editor — {os.path.basename(filepath)}")
        self.geometry("900x700")
        self.filepath = filepath
        self.api_key_provider = api_key_provider
        self.base_font = master.base_font

        self.original_content = ""
        self.current_content = ""

        self._build_ui()
        self._load_file()

    def _build_ui(self):
        top_bar = ttk.Frame(self, padding=1)
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text=f"Editing: {self.filepath}").pack(side=tk.LEFT, anchor="w")

        self.btn_save = ttk.Button(top_bar, text="Save", command=self.on_save)
        self.btn_save.pack(side=tk.RIGHT, padx=(2, 0))

        self.btn_show_diff = ttk.Button(top_bar, text="Show Diff", command=self.on_show_diff)
        self.btn_show_diff.pack(side=tk.RIGHT, padx=(2, 0))

        self.btn_ask_gemini = ttk.Button(
            top_bar, text="Ask Gemini to Edit...", command=self.on_ask_gemini
        )
        self.btn_ask_gemini.pack(side=tk.RIGHT, padx=(2, 0))

        editor_frame = ttk.Frame(self, padding=1)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        self.text = tk.Text(
            editor_frame,
            wrap=tk.NONE,
            font=self.base_font,
            undo=True,
        )
        self.text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, pady=0)

        vscroll = ttk.Scrollbar(editor_frame, orient=tk.VERTICAL, command=self.text.yview)
        hscroll = ttk.Scrollbar(editor_frame, orient=tk.HORIZONTAL, command=self.text.xview)
        self.text.config(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)

        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)

    def _load_file(self):
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                self.original_content = f.read()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file:\n{e}")
            self.destroy()
            return

        self.text.delete("1.0", tk.END)
        self.text.insert("1.0", self.original_content)
        self.current_content = self.original_content

    def _update_current_content(self):
        self.current_content = self.text.get("1.0", tk.END).rstrip("\n")

    def on_save(self):
        self._update_current_content()
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                f.write(self.current_content)
            self.original_content = self.current_content
            messagebox.showinfo("Saved", f"File saved:\n{self.filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file:\n{e}")

    def on_show_diff(self):
        self._update_current_content()
        old = self.original_content.splitlines(keepends=True)
        new = self.current_content.splitlines(keepends=True)

        diff = difflib.unified_diff(
            old,
            new,
            fromfile="original",
            tofile="current",
            lineterm=""
        )
        diff_text = "".join(diff) or "(No changes)"

        DiffWindow(self, diff_text, base_font=self.base_font)

    def on_ask_gemini(self):
        self._update_current_content()

        dialog = InstructionDialog(self, base_font=self.base_font)
        self.wait_window(dialog)
        instruction = dialog.result
        if not instruction:
            return

        messagebox.showinfo(
            "Gemini edit (stub)",
            "This is where a Gemini file-edit call would be made.\n\n"
            "You now have:\n"
            f"- File: {self.filepath}\n"
            f"- Length: {len(self.current_content)} characters\n"
            f"- Instruction: {instruction}\n\n"
            "When you are ready to wire in Gemini 3 Pro editing, this is the hook."
        )


class DiffWindow(tk.Toplevel):
    def __init__(self, master, diff_text: str, base_font):
        super().__init__(master)
        self.title("Diff Viewer")
        self.geometry("900x600")

        frame = ttk.Frame(self, padding=1)
        frame.pack(fill=tk.BOTH, expand=True)

        text = tk.Text(frame, wrap=tk.NONE, font=base_font)
        text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT, pady=0)

        vscroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=text.yview)
        hscroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=text.xview)
        text.config(yscrollcommand=vscroll.set, xscrollcommand=hscroll.set)

        vscroll.pack(side=tk.RIGHT, fill=tk.Y)
        hscroll.pack(side=tk.BOTTOM, fill=tk.X)

        text.tag_configure("add", foreground="#10b981")
        text.tag_configure("del", foreground="#ef4444")
        text.tag_configure("meta", foreground="#6b7280")

        for line in diff_text.splitlines():
            tag = None
            if line.startswith("+") and not line.startswith("+++"):
                tag = "add"
            elif line.startswith("-") and not line.startswith("---"):
                tag = "del"
            elif line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
                tag = "meta"

            if tag:
                text.insert(tk.END, line + "\n", tag)
            else:
                text.insert(tk.END, line + "\n")


class InstructionDialog(tk.Toplevel):
    def __init__(self, master, base_font):
        super().__init__(master)
        self.title("Gemini Edit Instruction")
        self.geometry("500x300")
        self.result = None
        self.base_font = base_font

        frame = ttk.Frame(self, padding=6)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Describe how Gemini should edit this file:").pack(anchor="w")

        self.text = tk.Text(frame, wrap=tk.WORD, height=8, font=base_font)
        self.text.pack(fill=tk.BOTH, expand=True, pady=0)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=(4, 0))

        ttk.Button(btn_frame, text="Cancel", command=self.on_cancel).pack(side=tk.RIGHT, padx=(4, 0))
        ttk.Button(btn_frame, text="OK", command=self.on_ok).pack(side=tk.RIGHT, padx=(4, 0))

        self.text.focus_set()

    def on_ok(self):
        self.result = self.text.get("1.0", tk.END).strip()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()


class TeeWriter(io.StringIO):
    def __init__(self, queue_ref: queue.Queue):
        super().__init__()
        self.queue_ref = queue_ref

    def write(self, s):
        if s:
            try:
                self.queue_ref.put(s)
            except Exception:
                pass
        return super().write(s)


class GeminiBridgeGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Gemini ↔ Terminal Bridge GUI (Extended)")
        self.geometry("1500x900")

        self.base_font = tkfont.Font(family="Menlo", size=10)

        self.history = []
        self._current_worker = None
        self._current_label = None

        self.workdir_var = tk.StringVar(value=get_base_dir())
        self.current_workdir = self.workdir_var.get()

        self.narrate_var = tk.BooleanVar(value=True)
        self.plan_first_var = tk.BooleanVar(value=True)
        self.safe_mode_var = tk.BooleanVar(value=True)

        self.show_left_var = tk.BooleanVar(value=True)
        self.show_summary_var = tk.BooleanVar(value=True)
        self.show_commands_var = tk.BooleanVar(value=True)
        self.show_live_var = tk.BooleanVar(value=True)
        self.show_output_var = tk.BooleanVar(value=True)
        self.show_input_var = tk.BooleanVar(value=True)

        self.file_tree = None

        self.stream_queue = queue.Queue()
        self._live_buffer = ""
        
        # Initialize persistent session
        if GeminiBridgeSession:
            self.session = GeminiBridgeSession()
        else:
            self.session = None

        load_dotenv()
        api_key = load_api_key_from_env_file()
        if api_key:
            os.environ["GEMINI_API_KEY"] = api_key
            try:
                genai.configure(api_key=api_key)
            except Exception:
                pass

        self._build_menubar()
        self._build_ui()

        self.status_label.config(
            text=f"Idle — connected to {BACKEND_NAME}",
            foreground="gray"
        )

        self.after(50, self._poll_stream_queue)

        self._last_dir_snapshot = set()
        self.after(2000, self._poll_workdir_changes)

    # ---------------- Menubar ----------------
    def _build_menubar(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)

        panels_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Panels", menu=panels_menu)

        panels_menu.add_checkbutton(
            label="Left sidebar (History & Files)",
            variable=self.show_left_var,
            command=self.update_panel_visibility,
        )
        panels_menu.add_separator()
        panels_menu.add_checkbutton(
            label="Summary",
            variable=self.show_summary_var,
            command=self.update_panel_visibility,
        )
        panels_menu.add_checkbutton(
            label="Commands",
            variable=self.show_commands_var,
            command=self.update_panel_visibility,
        )
        panels_menu.add_checkbutton(
            label="Live Summary Stream",
            variable=self.show_live_var,
            command=self.update_panel_visibility,
        )
        panels_menu.add_checkbutton(
            label="Full Output",
            variable=self.show_output_var,
            command=self.update_panel_visibility,
        )
        panels_menu.add_checkbutton(
            label="Input",
            variable=self.show_input_var,
            command=self.update_panel_visibility,
        )

    # ---------------- Layout ----------------
    def _build_ui(self):

        top_bar = ttk.Frame(self, padding=(10, 5))
        top_bar.pack(fill=tk.X)

        ttk.Label(top_bar, text="API key:").pack(side=tk.LEFT)

        self.api_key_var = tk.StringVar(value=load_api_key_from_env_file())
        self.api_key_entry = ttk.Entry(top_bar, textvariable=self.api_key_var)
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))

        apply_btn = ttk.Button(top_bar, text="Apply API Key", command=self.on_apply_api_key)
        apply_btn.pack(side=tk.LEFT)

        workdir_bar = ttk.Frame(self, padding=(6, 0))
        workdir_bar.pack(fill=tk.X)

        ttk.Label(workdir_bar, text="Working directory:").pack(side=tk.LEFT)

        self.workdir_entry = ttk.Entry(workdir_bar, textvariable=self.workdir_var)
        self.workdir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(4, 4))

        browse_btn = ttk.Button(workdir_bar, text="Browse…", command=self.on_browse_workdir)
        browse_btn.pack(side=tk.LEFT)

        self.main_paned = tk.PanedWindow(
            self,
            orient=tk.HORIZONTAL,
            sashwidth=3,         # thin but grabbable
            sashrelief="flat",
            bd=0,
            bg="#111111",        # dark line between left & right
        )
        self.main_paned.pack(fill=tk.BOTH, expand=True)

        # LEFT
        self.left_frame = ttk.Frame(self.main_paned, padding=1)
        self.main_paned.add(self.left_frame, stretch="always")

        self.left_notebook = ttk.Notebook(self.left_frame)
        self.left_notebook.pack(fill=tk.BOTH, expand=True)

        history_tab = ttk.Frame(self.left_notebook, padding=1)
        self.left_notebook.add(history_tab, text="History")

        ttk.Label(history_tab, text="History (ascending)").pack(anchor="w")

        self.history_list = tk.Listbox(history_tab, height=20, font=self.base_font)
        self.history_list.pack(fill=tk.BOTH, expand=True, pady=0)

        hscroll = ttk.Scrollbar(history_tab, orient=tk.VERTICAL, command=self.history_list.yview)
        self.history_list.config(yscrollcommand=hscroll.set)
        hscroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_list.bind("<<ListboxSelect>>", self.on_history_select)
        self.history_list.bind("<Delete>", self.on_history_delete)

        files_tab = ttk.Frame(self.left_notebook, padding=1)
        self.left_notebook.add(files_tab, text="Project Files")

        ttk.Label(files_tab, text="Files in working directory").pack(anchor="w")

        self.file_tree = ttk.Treeview(
            files_tab,
            columns=("fullpath", "type"),
            displaycolumns=(),
        )
        self.file_tree.heading("#0", text="Name", anchor="w")
        self.file_tree.pack(fill=tk.BOTH, expand=True, pady=0)

        fscroll = ttk.Scrollbar(files_tab, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.config(yscrollcommand=fscroll.set)
        fscroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_tree.bind("<<TreeviewOpen>>", self.on_tree_expand)
        self.file_tree.bind("<Double-1>", self.on_tree_double_click)

        self._populate_file_tree(self.workdir_var.get())

        # RIGHT
        self.right_paned = tk.PanedWindow(
            self.main_paned,
            orient=tk.VERTICAL,
            sashwidth=3,
            sashrelief="flat",
            bd=0,
            bg="#111111",
        )
        self.main_paned.add(self.right_paned, stretch="always")

        # Summary
        self.summary_frame = ttk.Frame(self.right_paned, padding=1)
        self.right_paned.add(self.summary_frame, stretch="always")

        ttk.Label(self.summary_frame, text="Gemini Summary:").pack(anchor="w")

        self.summary_text = tk.Text(
            self.summary_frame,
            wrap=tk.WORD,
            height=6,
            state=tk.DISABLED,
            font=self.base_font,
        )
        self.summary_text.pack(fill=tk.BOTH, expand=True, pady=0)

        sscroll = ttk.Scrollbar(self.summary_frame, orient=tk.VERTICAL, command=self.summary_text.yview)
        self.summary_text.config(yscrollcommand=sscroll.set)
        sscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Commands
        self.commands_frame = ttk.Frame(self.right_paned, padding=1)
        self.right_paned.add(self.commands_frame, stretch="always")

        ttk.Label(self.commands_frame, text="Commands run / Tool activity:").pack(anchor="w")

        self.commands_text = tk.Text(
            self.commands_frame,
            wrap=tk.WORD,
            height=6,
            state=tk.DISABLED,
            font=self.base_font,
        )
        self.commands_text.pack(fill=tk.BOTH, expand=True, pady=0)

        cscroll = ttk.Scrollbar(self.commands_frame, orient=tk.VERTICAL, command=self.commands_text.yview)
        self.commands_text.config(yscrollcommand=cscroll.set)
        cscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Live summary
        self.live_frame = ttk.Frame(self.right_paned, padding=1)
        self.right_paned.add(self.live_frame, stretch="always")

        ttk.Label(self.live_frame, text="Live Summary Stream (filtered from stdout):").pack(anchor="w")

        self.live_text = tk.Text(
            self.live_frame,
            wrap=tk.WORD,
            height=8,
            state=tk.DISABLED,
            font=self.base_font,
        )
        self.live_text.pack(fill=tk.BOTH, expand=True, pady=0)

        lscroll = ttk.Scrollbar(self.live_frame, orient=tk.VERTICAL, command=self.live_text.yview)
        self.live_text.config(yscrollcommand=lscroll.set)
        lscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Full output
        self.response_frame = ttk.Frame(self.right_paned, padding=1)
        self.right_paned.add(self.response_frame, stretch="always")

        ttk.Label(self.response_frame, text="Gemini / Bridge Output (final captured):").pack(anchor="w")

        self.response_text = tk.Text(
            self.response_frame,
            wrap=tk.WORD,
            height=16,
            state=tk.DISABLED,
            font=self.base_font,
        )
        self.response_text.pack(fill=tk.BOTH, expand=True, pady=0)

        rscroll = ttk.Scrollbar(self.response_frame, orient=tk.VERTICAL, command=self.response_text.yview)
        self.response_text.config(yscrollcommand=rscroll.set)
        rscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Input
        self.input_frame = ttk.Frame(self.right_paned, padding=1)
        self.right_paned.add(self.input_frame, stretch="always")

        top_input_bar = ttk.Frame(self.input_frame)
        top_input_bar.pack(fill=tk.X)

        ttk.Label(top_input_bar, text="Your request:").pack(side=tk.LEFT)

        self.char_count_label = ttk.Label(top_input_bar, text=f"0 / {MAX_CHARS}")
        self.char_count_label.pack(side=tk.RIGHT)

        self.input_text = tk.Text(
            self.input_frame,
            wrap=tk.WORD,
            height=8,
            font=self.base_font,
        )
        self.input_text.pack(fill=tk.BOTH, expand=True, pady=0)
        self.input_text.bind("<<Modified>>", self.on_input_modified)
        self.input_text.bind("<Return>", self.on_enter_key)
        self.input_text.bind("<Shift-Return>", self.on_shift_enter_key)

        bottom_buttons = ttk.Frame(self.input_frame)
        bottom_buttons.pack(fill=tk.X)

        self.status_label = ttk.Label(bottom_buttons, text="Idle", foreground="gray")
        self.status_label.pack(side=tk.LEFT)

        self.safe_mode_check = ttk.Checkbutton(
            bottom_buttons,
            text="Safe mode",
            variable=self.safe_mode_var
        )
        self.safe_mode_check.pack(side=tk.RIGHT, padx=(4, 0))

        self.plan_first_check = ttk.Checkbutton(
            bottom_buttons,
            text="Plan first",
            variable=self.plan_first_var
        )
        self.plan_first_check.pack(side=tk.RIGHT, padx=(4, 0))

        self.narrate_check = ttk.Checkbutton(
            bottom_buttons,
            text="Explain steps",
            variable=self.narrate_var
        )
        self.narrate_check.pack(side=tk.RIGHT, padx=(4, 0))

        self.font_smaller_button = ttk.Button(bottom_buttons, text="A-", width=3, command=self.decrease_font_size)
        self.font_smaller_button.pack(side=tk.RIGHT, padx=(4, 0))

        self.font_bigger_button = ttk.Button(bottom_buttons, text="A+", width=3, command=self.increase_font_size)
        self.font_bigger_button.pack(side=tk.RIGHT, padx=(4, 0))

        self.auto_fix_button = ttk.Button(
            bottom_buttons,
            text="Auto-fix last error",
            command=self.on_auto_fix_clicked,
        )
        self.auto_fix_button.pack(side=tk.RIGHT, padx=(4, 0))

        self.send_button = ttk.Button(bottom_buttons, text="Send", command=self.on_send_clicked)
        self.send_button.pack(side=tk.RIGHT, padx=(4, 8))

    # --------------- Panel visibility ---------------
    def update_panel_visibility(self):
        if self.show_left_var.get():
            if self.left_frame not in self.main_paned.panes():
                self.main_paned.add(self.left_frame, before=self.right_paned, stretch="always")
        else:
            if self.left_frame in self.main_paned.panes():
                self.main_paned.forget(self.left_frame)

        for pane in list(self.right_paned.panes()):
            self.right_paned.forget(pane)

        if self.show_summary_var.get():
            self.right_paned.add(self.summary_frame, stretch="always")
        if self.show_commands_var.get():
            self.right_paned.add(self.commands_frame, stretch="always")
        if self.show_live_var.get():
            self.right_paned.add(self.live_frame, stretch="always")
        if self.show_output_var.get():
            self.right_paned.add(self.response_frame, stretch="always")
        if self.show_input_var.get():
            self.right_paned.add(self.input_frame, stretch="always")

    # --------------- File tree + auto-refresh ---------------
    def _populate_file_tree(self, root_path):
        if not self.file_tree:
            return
        self.file_tree.delete(*self.file_tree.get_children())
        if not root_path or not os.path.isdir(root_path):
            return

        root_node = self.file_tree.insert("", "end", text=os.path.basename(root_path) or root_path,
                                          values=(root_path, "dir"), open=True)
        self._populate_file_tree_node(root_node, root_path)

    def _populate_file_tree_node(self, parent_id, parent_path):
        try:
            entries = sorted(os.listdir(parent_path))
        except Exception:
            return

        for name in entries:
            full = os.path.join(parent_path, name)
            if os.path.isdir(full):
                node_id = self.file_tree.insert(parent_id, "end", text=name, values=(full, "dir"))
                self.file_tree.insert(node_id, "end", text="(loading...)", values=("", "dummy"))
            else:
                self.file_tree.insert(parent_id, "end", text=name, values=(full, "file"))

    def on_tree_expand(self, event):
        item_id = self.file_tree.focus()
        if not item_id:
            return

        values = self.file_tree.item(item_id, "values")
        if not values:
            return
        path, kind = values
        if kind != "dir":
            return

        children = self.file_tree.get_children(item_id)
        for cid in children:
            cvals = self.file_tree.item(cid, "values")
            if cvals and len(cvals) > 1 and cvals[1] == "dummy":
                self.file_tree.delete(cid)

        self._populate_file_tree_node(item_id, path)

    def on_tree_double_click(self, event):
        item_id = self.file_tree.focus()
        if not item_id:
            return
        values = self.file_tree.item(item_id, "values")
        if not values:
            return
        path, kind = values
        if kind == "file" and os.path.isfile(path):
            FileEditorWindow(self, path, api_key_provider=self.get_current_api_key)

    def get_current_api_key(self):
        return self.api_key_var.get().strip()

    def _snapshot_directory(self, root_path):
        snapshot = set()
        for root, dirs, files in os.walk(root_path):
            for d in dirs:
                rel = os.path.relpath(os.path.join(root, d), root_path)
                snapshot.add(f"D:{rel}")
            for f in files:
                full = os.path.join(root, f)
                rel = os.path.relpath(full, root_path)
                try:
                    mtime = int(os.path.getmtime(full))
                except Exception:
                    mtime = 0
                snapshot.add(f"F:{rel}:{mtime}")
        return snapshot

    def _poll_workdir_changes(self):
        root = self.workdir_var.get().strip()
        if root and os.path.isdir(root):
            try:
                snapshot = self._snapshot_directory(root)
                if snapshot != self._last_dir_snapshot:
                    self._last_dir_snapshot = snapshot
                    self._populate_file_tree(root)
            except Exception:
                pass

        self.after(2000, self._poll_workdir_changes)

    # --------------- Font size ---------------
    def increase_font_size(self):
        size = self.base_font.cget("size")
        if size < 42:
            self.base_font.config(size=size + 1)

    def decrease_font_size(self):
        size = self.base_font.cget("size")
        if size > 6:
            self.base_font.config(size=size - 1)

    # --------------- Workdir ---------------
    def on_browse_workdir(self):
        current = self.workdir_var.get() or get_base_dir()
        path = filedialog.askdirectory(initialdir=current)
        if path:
            self.workdir_var.set(path)
            self.current_workdir = path
            self._populate_file_tree(path)
            try:
                self._last_dir_snapshot = self._snapshot_directory(path)
            except Exception:
                self._last_dir_snapshot = set()

    # --------------- API key ---------------
    def on_apply_api_key(self):
        new_key = self.api_key_var.get().strip()
        if not new_key:
            messagebox.showwarning("Empty key", "Please enter a non-empty API key.")
            return

        try:
            save_api_key_to_env_file(new_key)
        except Exception as e:
            messagebox.showerror("Error writing .env", f"{e}")
            return

        os.environ["GEMINI_API_KEY"] = new_key

        try:
            genai.configure(api_key=new_key)
        except Exception:
            pass

        if backend_set_api_key is not None:
            try:
                backend_set_api_key(new_key)
            except Exception as e:
                messagebox.showerror("Backend error", f"{e}")
                return

        messagebox.showinfo("API key updated", "API key updated successfully.")

    # --------------- History ---------------
    def add_history_entry(self, prompt, output, summary, commands, label):
        entry = {
            "prompt": prompt,
            "output": output,
            "summary": summary,
            "commands": commands,
            "label": label,
        }
        self.history.append(entry)
        idx = len(self.history) - 1

        first_line = summary.splitlines()[0] if summary.strip() else "(no summary)"
        display = f"{idx+1}: [{label}] {first_line[:80]}"
        self.history_list.insert(tk.END, display)

        self.history_list.select_clear(0, tk.END)
        self.history_list.select_set(idx)
        self.history_list.see(idx)

    def on_history_select(self, event):
        sel = self.history_list.curselection()
        if not sel:
            return
        idx = sel[0]
        entry = self.history[idx]
        self._set_summary_text(entry["summary"])
        self._set_commands_text(entry["commands"])
        self._set_response_text(entry["output"])

    def on_history_delete(self, event):
        sel = list(self.history_list.curselection())
        if not sel:
            return

        sel.sort(reverse=True)
        for idx in sel:
            del self.history[idx]
            self.history_list.delete(idx)

        if self.history:
            last = len(self.history) - 1
            self.history_list.select_set(last)
            entry = self.history[last]
            self._set_summary_text(entry["summary"])
            self._set_commands_text(entry["commands"])
            self._set_response_text(entry["output"])
        else:
            self._set_summary_text("")
            self._set_commands_text("")
            self._set_response_text("")
            self._clear_live_stream()

    # --------------- Input ---------------
    def on_input_modified(self, event):
        self.input_text.edit_modified(False)

        content = self.input_text.get("1.0", tk.END)
        length = len(content.rstrip("\n"))

        if length > MAX_CHARS:
            trimmed = content.rstrip("\n")[:MAX_CHARS]
            self.input_text.delete("1.0", tk.END)
            self.input_text.insert("1.0", trimmed)
            length = MAX_CHARS

        self.char_count_label.config(text=f"{length} / {MAX_CHARS}")

    def on_enter_key(self, event):
        self.on_send_clicked()
        return "break"

    def on_shift_enter_key(self, event):
        self.input_text.insert(tk.INSERT, "\n")
        return "break"

    # --------------- Meta-prompt ---------------
    def _apply_meta_prompt(self, base_prompt: str, is_auto_fix: bool) -> str:
        meta_lines = []

        meta_lines.append(
            "You are an AI developer assistant connected to a real terminal through a bridge."
        )

        if self.narrate_var.get():
            meta_lines.append(
                "Before running each significant command, briefly explain why you are doing it."
            )

        if self.plan_first_var.get():
            meta_lines.append(
                "First outline a step-by-step plan. Then execute the plan step by step, clearly indicating which step you are on."
            )

        if self.safe_mode_var.get():
            meta_lines.append(
                "Avoid destructive or unrelated commands. Do NOT run rm -rf, mkfs, fork bombs, or modify critical system files. Prefer minimal, targeted changes."
            )

        if is_auto_fix:
            meta_lines.append(
                "You are in auto-fix mode, focusing on diagnosing and fixing the previously encountered error."
            )

        meta_text = "\n".join(meta_lines).strip()
        if not meta_text:
            return base_prompt

        return meta_text + "\n\nUSER REQUEST / CONTEXT:\n" + base_prompt

    # --------------- Live stream handling ---------------
    def _clear_live_stream(self):
        self.live_text.config(state=tk.NORMAL)
        self.live_text.delete("1.0", tk.END)
        self.live_text.config(state=tk.DISABLED)
        self._live_buffer = ""

    def _append_live_text(self, chunk: str):
        if not chunk:
            return

        lines = (self._live_buffer + chunk).splitlines(keepends=True)
        if lines and not lines[-1].endswith(("\n", "\r")):
            self._live_buffer = lines[-1]
            lines = lines[:-1]
        else:
            self._live_buffer = ""

        filtered = []
        for line in lines:
            s = line.strip()
            if not s:
                filtered.append(line)
                continue
            if s.startswith("→ Running:") or s.startswith("Command:"):
                continue
            if s.startswith("[WARNING] Could not change directory"):
                continue
            if s.startswith("=== SUMMARY FROM GEMINI ==="):
                continue
            filtered.append(line)

        text = "".join(filtered)
        if not text:
            return

        self.live_text.config(state=tk.NORMAL)
        self.live_text.insert(tk.END, text)
        self.live_text.see(tk.END)
        self.live_text.config(state=tk.DISABLED)

    def _poll_stream_queue(self):
        try:
            while True:
                chunk = self.stream_queue.get_nowait()
                self._append_live_text(chunk)
        except queue.Empty:
            pass
        self.after(50, self._poll_stream_queue)

    # --------------- Request flow ---------------
    def _start_request(self, composed_prompt: str, label: str):
        if self._current_worker and self._current_worker.is_alive():
            messagebox.showinfo("Busy", "Please wait — a request is already running.")
            return False

        self.current_workdir = self.workdir_var.get().strip() or get_base_dir()
        self._current_label = label

        self._clear_live_stream()

        status_text = f"Running: {label}"
        self.status_label.config(text=status_text, foreground="orange")
        self.send_button.config(state=tk.DISABLED)
        self.auto_fix_button.config(state=tk.DISABLED)

        t = threading.Thread(
            target=self._run_bridge_request,
            args=(composed_prompt,),
            daemon=True
        )
        self._current_worker = t
        t.start()
        return True

    def on_send_clicked(self):
        base_prompt = self.input_text.get("1.0", tk.END).strip()
        if not base_prompt:
            messagebox.showwarning("Empty", "Request cannot be empty.")
            return
        full_prompt = self._apply_meta_prompt(base_prompt, is_auto_fix=False)
        self._start_request(full_prompt, label="User request")

    def on_auto_fix_clicked(self):
        if not self.history:
            messagebox.showwarning(
                "No history",
                "There is no previous run to auto-fix. Run something first."
            )
            return

        last = self.history[-1]
        prev_prompt = last["prompt"]
        prev_output = last["output"]

        auto_fix_prompt = (
            "The user previously asked:\n"
            f"{prev_prompt}\n\n"
            "The terminal session produced this output (including any errors):\n"
            f"{prev_output}\n\n"
            "Analyze the failure. Propose and execute a minimal set of safe commands "
            "to fix the problem. Focus only on relevant files and dependencies.\n"
        )

        full_prompt = self._apply_meta_prompt(auto_fix_prompt, is_auto_fix=True)
        self._start_request(full_prompt, label="Auto-fix last error")

    def _run_bridge_request(self, prompt):
        buf = TeeWriter(self.stream_queue)

        workdir = self.current_workdir or get_base_dir()
        if workdir:
            try:
                os.chdir(workdir)
            except Exception as e:
                buf.write(f"[WARNING] Could not change directory to {workdir}: {e}\n")

        try:
            with contextlib.redirect_stdout(buf):
                if self.session:
                    self.session.chat(prompt)
                else:
                    print("[ERROR] No backend session available.")
        except Exception as e:
            output = f"[ERROR] {e}\n\n" + buf.getvalue()
            summary = f"ERROR: {e}"
            commands = ""
        else:
            output = buf.getvalue()
            summary = extract_last_summary(output)
            commands = extract_commands(output)

        self.after(0, self._on_request_done, prompt, output, summary, commands, self._current_label)

    def _log_session(self, label: str, prompt: str, summary: str, commands: str, output: str):
        try:
            base = get_base_dir()
            logs_dir = os.path.join(base, "logs")
            os.makedirs(logs_dir, exist_ok=True)
            ts = datetime.datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
            fname = os.path.join(logs_dir, f"session-{ts}-{label.replace(' ', '_')}.txt")
            with open(fname, "w", encoding="utf-8") as f:
                f.write(f"Label: {label}\n")
                f.write(f"Timestamp: {ts}\n")
                f.write("\n=== PROMPT ===\n")
                f.write(prompt)
                f.write("\n\n=== SUMMARY ===\n")
                f.write(summary)
                f.write("\n\n=== COMMANDS ===\n")
                f.write(commands)
                f.write("\n\n=== FULL OUTPUT ===\n")
                f.write(output)
        except Exception:
            pass

    def _on_request_done(self, prompt, output, summary, commands, label):
        self._set_summary_text(summary)
        self._set_commands_text(commands)
        self._set_response_text(output)
        self.add_history_entry(prompt, output, summary, commands, label or "Unknown")

        self._log_session(label or "Unknown", prompt, summary, commands, output)

        self.status_label.config(text="Idle", foreground="gray")
        self.send_button.config(state=tk.NORMAL)
        self.auto_fix_button.config(state=tk.NORMAL)
        self._current_label = None

    # --------------- Text setters ---------------
    def _set_summary_text(self, txt):
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert("1.0", txt)
        self.summary_text.config(state=tk.DISABLED)
        self.summary_text.see("1.0")

    def _set_commands_text(self, txt):
        self.commands_text.config(state=tk.NORMAL)
        self.commands_text.delete("1.0", tk.END)

        lines = txt.splitlines()
        if not lines:
            self.commands_text.insert("1.0", "(no commands found)")
        else:
            for line in lines:
                clean = line.strip()
                if not clean:
                    self.commands_text.insert(tk.END, "\n")
                    continue
                risk_level, reason = classify_command_risk(clean)
                if risk_level == "RED":
                    prefix = "[BLOCK?] "
                elif risk_level == "YELLOW":
                    prefix = "[WARN]   "
                else:
                    prefix = "[OK]     "
                self.commands_text.insert(tk.END, f"{prefix}{clean}  ({reason})\n")

        self.commands_text.config(state=tk.DISABLED)
        self.commands_text.see("1.0")

    def _set_response_text(self, txt):
        self.response_text.config(state=tk.NORMAL)
        self.response_text.delete("1.0", tk.END)
        self.response_text.insert("1.0", txt)
        self.response_text.config(state=tk.DISABLED)
        self.response_text.see("1.0")


if __name__ == "__main__":
    app = GeminiBridgeGUI()
    app.mainloop()
