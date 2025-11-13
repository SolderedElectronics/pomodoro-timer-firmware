#!/usr/bin/env python3
"""
RP2040 Production Programmer (Tkinter GUI)
------------------------------------------
Automatically flashes a UF2 file (auto-detected in script folder) to an RP2040 board in BOOTSEL mode,
waits for reboot, uploads only .py files via mpremote, and resets the board.

Dependencies: psutil, pyserial, mpremote
(Tkinter is built-in with normal Python)
"""

import os
import time
import shutil
import threading
import subprocess
from pathlib import Path
import psutil
from serial.tools import list_ports
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

# -------------------------------
# Helper functions
# -------------------------------

def find_rpi_rp2_mountpoint():
    """Find the RPI-RP2 mass-storage drive (BOOTSEL mode)."""
    for part in psutil.disk_partitions(all=False):
        mp = part.mountpoint
        try:
            info = Path(mp) / "INFO_UF2.TXT"
            index = Path(mp) / "INDEX.HTM"
            if info.exists() or index.exists():
                return mp
        except Exception:
            pass
    return None

def list_serial_ports():
    return list(list_ports.comports())

def pick_new_port(before_set):
    after = set(p.device for p in list_serial_ports())
    new = list(after - before_set)
    return new[0] if new else None

def run_cmd(args):
    """Run a subprocess and yield its output line by line."""
    try:
        proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            yield line.strip()
        proc.wait()
    except FileNotFoundError:
        yield f"❌ Command not found: {args[0]}"

def ensure_mpremote():
    try:
        subprocess.run(["mpremote", "version"], check=False, stdout=subprocess.DEVNULL)
        return True
    except Exception:
        return False

# -------------------------------
# Core logic
# -------------------------------

def flash_and_upload(log, uf2_path: Path, project_dir: Path, reboot_wait=3, drive_timeout=60, port_timeout=60, stop_flag=[False]):
    def log_print(msg):
        log.insert(tk.END, msg + "\n")
        log.see(tk.END)
        log.update()

    try:
        if not uf2_path.exists():
            log_print(f"❌ UF2 not found: {uf2_path}")
            return

        if not ensure_mpremote():
            log_print("❌ mpremote not found. Install it with: pip install mpremote")
            return

        log_print(f"UF2 file: {uf2_path}")
        log_print(f"Project folder: {project_dir}")

        before_ports = set(p.device for p in list_serial_ports())

        # --- Wait for BOOTSEL drive ---
        log_print("Waiting for RP2040 in BOOTSEL mode...")
        t0 = time.time()
        while not stop_flag[0]:
            mp = find_rpi_rp2_mountpoint()
            if mp:
                log_print(f"Found RPI-RP2 drive at {mp}")
                try:
                    shutil.copy2(uf2_path, Path(mp) / uf2_path.name)
                    log_print("✅ UF2 copied successfully. Board will reboot...")
                    break
                except Exception as e:
                    log_print(f"❌ Copy failed: {e}")
                    return
            if time.time() - t0 > drive_timeout:
                log_print("❌ Timeout waiting for BOOTSEL drive.")
                return
            time.sleep(0.5)

        # --- Wait for new COM port ---
        log_print("Waiting for MicroPython serial port...")
        time.sleep(reboot_wait)
        t0 = time.time()
        port = None
        while not stop_flag[0]:
            port = pick_new_port(before_ports)
            if port:
                log_print(f"Found new port: {port}")
                break
            if time.time() - t0 > port_timeout:
                ports = list_serial_ports()
                if len(ports) == 1:
                    port = ports[0].device
                    log_print(f"Timeout. Using only port: {port}")
                    break
                log_print("❌ Timeout waiting for serial port.")
                return
            time.sleep(0.5)

        if not port:
            log_print("❌ No serial port found after flashing.")
            return

        # --- Upload only .py files ---
        log_print(f"Uploading .py files from {project_dir}...")
        total_files = 0
        success_files = 0

        for root, _, files in os.walk(project_dir):
            rel = Path(root).relative_to(project_dir)
            py_files = [f for f in files if f.endswith(".py")]
            if not py_files:
                continue

            # Create directory structure on the board
            if str(rel) != ".":
                dest_dir = f":/{rel.as_posix()}"
                subprocess.run(["mpremote", "connect", port, "fs", "mkdir", dest_dir], check=False)

            for f in py_files:
                src = Path(root) / f
                dest = f":/{(rel / f).as_posix()}"
                total_files += 1
                log_print(f"📁 Transferring file {total_files}: {src.name} → {dest}")

                result = subprocess.run(
                    ["mpremote", "connect", port, "cp", str(src), dest],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    success_files += 1
                    log_print(f"✅ {src.name} copied successfully.")
                else:
                    log_print(f"❌ Failed to copy {src.name}: {result.stderr.strip()}")

        if total_files == 0:
            log_print("⚠️ No .py files found in project folder.")
        else:
            log_print(f"✅ {success_files}/{total_files} .py files copied successfully.")

        # --- Reset and verify ---
        subprocess.run(["mpremote", "connect", port, "reset"], check=False)
        log_print("🔄 Board reset.")
        subprocess.run(["mpremote", "connect", port, "exec", "print('ok')"], check=False)
        log_print("🎉 DONE: Board programmed successfully!")

    except Exception as e:
        log_print(f"💥 Error: {e}")

# -------------------------------
# Tkinter GUI
# -------------------------------

class ProgrammerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RP2040 Production Programmer")
        self.root.geometry("750x550")

        self.stop_flag = [False]

        # Auto-detect UF2 file and default project folder (same as script dir)
        script_dir = Path(__file__).parent
        uf2_files = list(script_dir.glob("*.uf2"))
        self.uf2_path = uf2_files[0] if uf2_files else None
        self.project_dir = tk.StringVar(value=str(script_dir))

        frame = ttk.Frame(root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Detected UF2 file:").pack(anchor="w")
        self.uf2_label = ttk.Label(frame, text=str(self.uf2_path) if self.uf2_path else "❌ None found")
        self.uf2_label.pack(anchor="w", pady=(0, 10))

        ttk.Label(frame, text="Project folder (default = this folder):").pack(anchor="w")
        proj_frame = ttk.Frame(frame)
        proj_frame.pack(fill="x", pady=(0, 10))
        ttk.Entry(proj_frame, textvariable=self.project_dir).pack(side="left", fill="x", expand=True)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=(5, 5))
        self.start_btn = ttk.Button(btn_frame, text="Program Board", command=self.start)
        self.start_btn.pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Stop", command=self.stop).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Exit", command=root.destroy).pack(side="left", padx=5)

        ttk.Label(frame, text="Log:").pack(anchor="w")
        self.log = scrolledtext.ScrolledText(frame, width=90, height=25, state="normal")
        self.log.pack(fill="both", expand=True)

    def start(self):
        if not self.uf2_path:
            messagebox.showerror("Error", "No UF2 file found in script folder!")
            return
        self.stop_flag[0] = False
        self.log.delete("1.0", tk.END)
        self.start_btn.config(state="disabled")
        thread = threading.Thread(
            target=flash_and_upload,
            args=(self.log, self.uf2_path, Path(self.project_dir.get())),
            daemon=True
        )
        thread.start()
        self.root.after(100, self.check_thread, thread)

    def check_thread(self, thread):
        if thread.is_alive():
            self.root.after(200, self.check_thread, thread)
        else:
            self.start_btn.config(state="normal")

    def stop(self):
        self.stop_flag[0] = True
        self.log.insert(tk.END, "⏹️ Stop requested.\n")
        self.log.see(tk.END)

# -------------------------------
# Main
# -------------------------------

if __name__ == "__main__":
    root = tk.Tk()
    app = ProgrammerApp(root)
    root.mainloop()
