import os
import tkinter as tk
from tkinter import filedialog, ttk, scrolledtext
"""
Color scheme: Lighter black (#2a2a2e), total black (#0a0a0a), white, emerald green (#10b981)
"""

def create_assembly_gui():
    step_files = []

    root = tk.Tk()
    root.title("AI-Assisted CAD Assembly System")
    root.geometry("1100x820")
    root.configure(bg="#0a0a0a")

    # Typography
    FT = ("Arial", 18, "bold")  # Title
    FN = ("Arial", 10)          # Normal
    FB = ("Arial", 10, "bold")  # Bold
    FM = ("Consolas", 9)        # Monospace

    # ──────────────────────────────────────────────────────────────
    # HEADER
    # ──────────────────────────────────────────────────────────────
    tk.Label(
        root, text="AI-Assisted CAD Assembly",
        font=FT, fg="#10b981", bg="#0a0a0a"
    ).pack(pady=(14, 2))

    tk.Label(
        root, text="Upload STEP files  •  Describe in plain language  •  AI-powered",
        font=("Arial", 9), fg="#888", bg="#0a0a0a"
    ).pack(pady=(0, 10))

    # ──────────────────────────────────────────────────────────────
    # MAIN LAYOUT: Split view (left + right)
    # ──────────────────────────────────────────────────────────────
    split = tk.Frame(root, bg="#0a0a0a")
    split.pack(fill="both", expand=True, padx=12, pady=6)

    left = tk.Frame(split, bg="#0a0a0a", width=540)
    right = tk.Frame(split, bg="#0a0a0a")
    left.pack(side="left", fill="both", expand=False, padx=(0, 8))
    left.pack_propagate(False)
    right.pack(side="right", fill="both", expand=True)

    # ──────────────────────────────────────────────────────────────
    # LEFT PANEL: File Management
    # ──────────────────────────────────────────────────────────────
    pf = tk.LabelFrame(
        left, text="  Loaded Parts  ",
        font=FB, fg="white", bg="#2a2a2e", bd=1, relief="groove",
        padx=8, pady=6
    )
    pf.pack(fill="x", pady=(0, 8))

    # File list
    lf = tk.Frame(pf, bg="#2a2a2e")
    lf.pack(fill="both")
    file_list = tk.Listbox(
        lf, width=65, height=5, font=FM,
        bg="#0a0a0a", fg="#e0e0e0", selectbackground="#10b981",
        bd=0, highlightthickness=0
    )
    file_list.pack(side="left", fill="both", expand=True)
    sb = tk.Scrollbar(lf, bg="#2a2a2e")
    sb.pack(side="right", fill="y")
    file_list.config(yscrollcommand=sb.set)
    sb.config(command=file_list.yview)

    count_var = tk.StringVar(value="No files loaded")
    tk.Label(
        pf, textvariable=count_var,
        font=("Arial", 8), fg="#666", bg="#2a2a2e", anchor="w"
    ).pack(fill="x", pady=(4, 0))

    # File action buttons
    def upload_files():
        files = filedialog.askopenfilenames(
            title="Select STEP Files",
            filetypes=[("STEP", "*.step *.stp"), ("All", "*.*")]
        )
        if files:
            added = 0
            for f in files:
                f = os.path.abspath(f)
                if f not in step_files:
                    step_files.append(f)
                    added += 1
            _refresh_list()
            _log(f"Added {added} file(s). Total: {len(step_files)}", "info")

    def clear_files():
        step_files.clear()
        file_list.delete(0, tk.END)
        count_var.set("No files loaded")

    def remove_selected():
        sel = file_list.curselection()
        if sel:
            step_files.pop(sel[0])
            _refresh_list()

    def _refresh_list():
        file_list.delete(0, tk.END)
        for i, f in enumerate(step_files, 1):
            name = os.path.basename(f)
            folder = os.path.dirname(f)
            if len(folder) > 40:
                folder = "…" + folder[-35:]
            file_list.insert(tk.END, f"  {i:2d}.  {name:<24} {folder}")
        n = len(step_files)
        count_var.set(
            f"{n} file(s)" + (" — need ≥2" if n < 2 else " — ready ✓")
        )

    br = tk.Frame(pf, bg="#2a2a2e")
    br.pack(fill="x", pady=(6, 0))
    for txt, cmd, col in [
        ("📂 Add STEP Files", upload_files, "#10b981"),
        ("✕ Remove", remove_selected, "#666"),
        ("🗑 Clear All", clear_files, "#444"),
    ]:
        tk.Button(
            br, text=txt, command=cmd, font=FN,
            bg=col, fg="white", relief="flat",
            padx=8, pady=3, cursor="hand2"
        ).pack(side="left", padx=(0, 4))

    # ──────────────────────────────────────────────────────────────
    # LEFT PANEL: Assembly Instructions
    # ──────────────────────────────────────────────────────────────
    promptf = tk.LabelFrame(
        left, text="  Assembly Instructions  ",
        font=FB, fg="white", bg="#2a2a2e", bd=1, relief="groove",
        padx=8, pady=6
    )
    promptf.pack(fill="x", pady=(0, 8))

    tk.Label(
        promptf, text="Describe the assembly in plain language:",
        font=("Arial", 9), fg="#aaa", bg="#2a2a2e"
    ).pack(anchor="w")

    prompt_var = tk.StringVar()
    prompt_entry = tk.Entry(
        promptf, textvariable=prompt_var, font=("Consolas", 11),
        bg="#0a0a0a", fg="#e0e0e0", insertbackground="#10b981",
        relief="flat", bd=4
    )
    prompt_entry.pack(fill="x", pady=(4, 6))

    tk.Label(
        promptf,
        text='Example: "Insert screw into hole, rotate part 90°"',
        font=("Arial", 8), fg="#555", bg="#2a2a2e"
    ).pack(anchor="w")

    api_status_var = tk.StringVar(value="")
    tk.Label(
        promptf, textvariable=api_status_var,
        font=("Arial", 8), fg="#10b981", bg="#2a2a2e"
    ).pack(anchor="w", pady=(2, 0))

    # Quick suggestions
    tk.Label(
        promptf, text="Quick suggestions:",
        font=("Arial", 8), fg="#555", bg="#2a2a2e"
    ).pack(anchor="w", pady=(4, 0))
    suggest_frame = tk.Frame(promptf, bg="#2a2a2e")
    suggest_frame.pack(fill="x", pady=(2, 0))

    def _use_suggestion(txt):
        prompt_var.set(txt)
        prompt_entry.focus()

    # Sample suggestions
    sample_suggestions = [
        "Insert Part B into Part A",
        "Align and fasten components",
        "Rotate 45° and insert",
        "Stack horizontally",
        "Screw fasteners into holes",
    ]
    for s in sample_suggestions[:4]:
        tk.Button(
            suggest_frame, text=s,
            command=lambda t=s: _use_suggestion(t),
            font=("Arial", 8), bg="#1a1a1a", fg="#888",
            relief="flat", padx=6, pady=2, cursor="hand2"
        ).pack(side="left", padx=(0, 4), pady=2)

    # ──────────────────────────────────────────────────────────────
    # LEFT PANEL: Progress & Results
    # ──────────────────────────────────────────────────────────────
    pgf = tk.Frame(left, bg="#0a0a0a")
    pgf.pack(fill="x", pady=(0, 6))

    progress_var = tk.IntVar(value=0)
    style = ttk.Style()
    style.theme_use("default")
    style.configure(
        "G.Horizontal.TProgressbar",
        troughcolor="#1a1a1a",
        background="#10b981",
        thickness=16
    )
    ttk.Progressbar(
        pgf, variable=progress_var, maximum=100,
        style="G.Horizontal.TProgressbar"
    ).pack(side="left", fill="x", expand=True)

    status_var = tk.StringVar(value="Waiting…")
    tk.Label(
        pgf, textvariable=status_var,
        font=("Arial", 9), fg="#10b981", bg="#0a0a0a",
        width=20, anchor="w"
    ).pack(side="left", padx=8)

    # Results tree
    mf = tk.LabelFrame(
        left, text="  Assembly Results  ",
        font=FB, fg="white", bg="#2a2a2e", bd=1, relief="groove",
        padx=6, pady=4
    )
    mf.pack(fill="both", expand=True, pady=(0, 8))

    cols = ("Pair", "Strategy", "Fit", "Conf", "Status")
    result_tree = ttk.Treeview(mf, columns=cols, show="headings", height=5)
    for c, w in zip(cols, [190, 90, 110, 55, 50]):
        result_tree.heading(c, text=c)
        result_tree.column(c, width=w, anchor="w")
    result_tree.pack(fill="both", expand=True)

    style.configure(
        "Treeview",
        background="#0a0a0a",
        foreground="#e0e0e0",
        fieldbackground="#0a0a0a",
        rowheight=22
    )
    style.configure(
        "Treeview.Heading",
        background="#1a1a1a",
        foreground="#10b981"
    )
    style.map("Treeview", background=[("selected", "#10b981")])

    # ──────────────────────────────────────────────────────────────
    # LEFT PANEL: Action Buttons
    # ──────────────────────────────────────────────────────────────
    act = tk.Frame(left, bg="#0a0a0a")
    act.pack(pady=8)

    assemble_btn = tk.Button(
        act, text="⚙  Run Assembly",
        font=("Arial", 12, "bold"), bg="#10b981", fg="white",
        relief="flat", padx=16, pady=8, cursor="hand2"
    )
    assemble_btn.pack(side="left", padx=4)

    viewer_btn = tk.Button(
        act, text="🔭  3D Viewer",
        font=FB, bg="#1a1a1a", fg="#888",
        relief="flat", padx=10, pady=8, state="disabled", cursor="hand2"
    )
    viewer_btn.pack(side="left", padx=4)

    report_btn = tk.Button(
        act, text="📄  Report",
        font=FN, bg="#1a1a1a", fg="#888",
        relief="flat", padx=10, pady=8, state="disabled", cursor="hand2"
    )
    report_btn.pack(side="left", padx=4)

    # ──────────────────────────────────────────────────────────────
    # RIGHT PANEL: Assembly Log
    # ──────────────────────────────────────────────────────────────
    lf2 = tk.LabelFrame(
        right, text="  Assembly Log  ",
        font=FB, fg="white", bg="#2a2a2e", bd=1, relief="groove",
        padx=8, pady=6
    )
    lf2.pack(fill="both", expand=True)

    log_box = scrolledtext.ScrolledText(
        lf2, font=FM, bg="#0a0a0a", fg="#e0e0e0",
        bd=0, highlightthickness=0, state="disabled", wrap="word"
    )
    log_box.pack(fill="both", expand=True)

    # Tag colors for log
    for tag, col in [
        ("ok", "#10b981"),          # Emerald
        ("err", "#ff6b6b"),         # Red
        ("info", "#64b5f6"),        # Blue
        ("warn", "#ffd93d"),        # Yellow
        ("sep", "#333"),            # Dark
        ("dim", "#666"),            # Gray
        ("ai", "#10b981"),          # Emerald
    ]:
        log_box.tag_config(tag, foreground=col)

    def _log(msg, tag=""):
        log_box.configure(state="normal")
        log_box.insert(tk.END, msg + "\n", tag)
        log_box.see(tk.END)
        log_box.configure(state="disabled")

    # ──────────────────────────────────────────────────────────────
    # ACTION HANDLERS (Placeholder callbacks)
    # ──────────────────────────────────────────────────────────────

    def assemble():
        if len(step_files) < 2:
            _log("⚠  Add at least 2 STEP files first.", "warn")
            return
        
        assemble_btn.config(state="disabled")
        progress_var.set(0)
        result_tree.delete(*result_tree.get_children())
        _log("─" * 52, "sep")
        _log(f"Assembling {len(step_files)} part(s)…", "info")
        
        prompt = prompt_var.get().strip()
        if prompt:
            _log(f'Prompt: "{prompt}"', "info")
            api_status_var.set("🤖 Processing with AI…")
        else:
            _log("No prompt — auto-detect mode", "dim")

        # Simulate progress
        for i in range(1, 101, 20):
            progress_var.set(i)
            status_var.set(f"Processing… {i}%")
            root.update()
            root.after(300)

        progress_var.set(100)
        status_var.set("Complete ✓")
        api_status_var.set("")
        
        _log("─" * 52, "sep")
        _log("✓  Assembly complete!", "ok")
        _log("  Part A ↔ Part B  [Insert]  Tight Fit  conf=85%  ✓", "ok")
        _log("  Part B ↔ Part C  [Rotate]  Normal Fit  conf=72%  ⚠", "warn")
        result_tree.insert("", "end", values=("Part A ↔ Part B", "Insert", "Tight", "85%", "✓"))
        result_tree.insert("", "end", values=("Part B ↔ Part C", "Rotate", "Normal", "72%", "⚠"))
        
        viewer_btn.config(state="normal")
        report_btn.config(state="normal")
        assemble_btn.config(state="normal")

    def open_viewer():
        if result_tree.get_children():
            _log("Opening 3D Viewer…", "info")
            root.update()
            _log("Viewer would display 3D model here", "dim")
        else:
            _log("Run assembly first.", "warn")

    def open_report():
        if result_tree.get_children():
            _log("Opening assembly report…", "info")
            root.update()
            _log("Report would open in default application", "dim")
        else:
            _log("Run assembly first.", "warn")

    assemble_btn.config(command=assemble)
    viewer_btn.config(command=open_viewer)
    report_btn.config(command=open_report)

    # ──────────────────────────────────────────────────────────────
    # FOOTER
    # ──────────────────────────────────────────────────────────────
    tk.Label(
        root,
        text="AI-Assisted CAD Assembly  •  PythonOCC  •  Ready for AI Integration",
        font=("Arial", 8), fg="#333", bg="#0a0a0a"
    ).pack(side="bottom", pady=6)

    root.mainloop()


if __name__ == "__main__":
    create_assembly_gui()