import customtkinter as ctk
from tkinter import messagebox, ttk, filedialog
import psutil
import threading
import time
from datetime import datetime
import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

class SystemMonitorGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("System Resource Monitor")
        self.root.geometry("1100x700")
        self.root.minsize(1000, 650)
        
        self.monitoring = False
        self.alert_shown_cpu = False
        self.alert_shown_ram = False
        self.alert_shown_disk = False
        
        # Email alert settings
        self.email_alerts_enabled = False
        
        # Default thresholds
        self.cpu_threshold = 80
        self.ram_threshold = 80
        self.disk_threshold = 90
        
        # Log file
        self.log_file = "system_logs.csv"
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "CPU (%)", "RAM (%)", "Disk (%)", "Alert"])
        
        self.setup_ui()
        self.root.mainloop()
    
    def setup_ui(self):
        # Main container
        main = ctk.CTkFrame(self.root, fg_color="#f0f2f5")
        main.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = ctk.CTkFrame(main, corner_radius=12, height=80, fg_color="#4f46e5")
        header.pack(fill="x", pady=(0, 20))
        header.pack_propagate(False)
        
        ctk.CTkLabel(header, text="System Resource Monitor", font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack(pady=(20, 5))
        ctk.CTkLabel(header, text="Real-time CPU, RAM, Disk Monitoring with Email Alerts", font=ctk.CTkFont(size=12), text_color="#c7d2fe").pack()
        
        # Two columns
        columns = ctk.CTkFrame(main, fg_color="transparent")
        columns.pack(fill="both", expand=True)
        
        # LEFT PANEL - Scrollable
        left = ctk.CTkFrame(columns, corner_radius=12, fg_color="white", width=500)
        left.pack(side="left", fill="both", padx=(0, 10))
        left.pack_propagate(False)
        
        # Make left panel scrollable
        left_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent")
        left_scroll.pack(fill="both", expand=True, padx=5, pady=5)
        
        left_inner = ctk.CTkFrame(left_scroll, fg_color="transparent")
        left_inner.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Control Buttons
        ctk.CTkLabel(left_inner, text="Controls", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1e293b").pack(anchor="w", pady=(0, 10))
        
        self.start_btn = ctk.CTkButton(left_inner, text="Start Monitoring", height=40, fg_color="#10b981", hover_color="#059669", command=self.start_monitoring)
        self.start_btn.pack(fill="x", pady=(0, 10))
        
        self.stop_btn = ctk.CTkButton(left_inner, text="Stop Monitoring", height=40, fg_color="#ef4444", hover_color="#dc2626", command=self.stop_monitoring, state="disabled")
        self.stop_btn.pack(fill="x", pady=(0, 15))
        
        # Email Alert Section
        email_section = ctk.CTkFrame(left_inner, corner_radius=10, fg_color="#f8fafc", border_width=1, border_color="#e2e8f0")
        email_section.pack(fill="x", pady=(0, 15))
        
        email_inner = ctk.CTkFrame(email_section, fg_color="transparent")
        email_inner.pack(padx=15, pady=15)
        
        ctk.CTkLabel(email_inner, text="Email Alert (Bonus)", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1e293b").pack(anchor="w", pady=(0, 10))
        
        self.email_enabled = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(email_inner, text="Enable Email Alerts", variable=self.email_enabled, command=self.toggle_email_settings).pack(anchor="w")
        
        self.email_frame = ctk.CTkFrame(email_inner, fg_color="transparent")
        
        ctk.CTkLabel(self.email_frame, text="From Email:", font=ctk.CTkFont(size=11)).grid(row=0, column=0, sticky="w", pady=5)
        self.email_from_entry = ctk.CTkEntry(self.email_frame, width=160, height=30)
        self.email_from_entry.grid(row=0, column=1, padx=(10, 0), pady=5)
        
        ctk.CTkLabel(self.email_frame, text="App Password:", font=ctk.CTkFont(size=11)).grid(row=1, column=0, sticky="w", pady=5)
        self.email_pass_entry = ctk.CTkEntry(self.email_frame, width=160, height=30, show="*")
        self.email_pass_entry.grid(row=1, column=1, padx=(10, 0), pady=5)
        
        ctk.CTkLabel(self.email_frame, text="To Email:", font=ctk.CTkFont(size=11)).grid(row=2, column=0, sticky="w", pady=5)
        self.email_to_entry = ctk.CTkEntry(self.email_frame, width=160, height=30)
        self.email_to_entry.grid(row=2, column=1, padx=(10, 0), pady=5)
        
        ctk.CTkButton(self.email_frame, text="Test Email", height=30, width=100, fg_color="#64748b", command=self.send_test_email).grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # Threshold Settings
        ctk.CTkLabel(left_inner, text="Threshold Settings", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1e293b").pack(anchor="w", pady=(15, 10))
        
        # CPU Threshold
        cpu_frame = ctk.CTkFrame(left_inner, fg_color="transparent")
        cpu_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(cpu_frame, text="CPU Threshold:", width=100, text_color="#1e293b").pack(side="left")
        self.cpu_entry = ctk.CTkEntry(cpu_frame, width=70)
        self.cpu_entry.insert(0, "80")
        self.cpu_entry.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(cpu_frame, text="%", text_color="#1e293b").pack(side="left", padx=(5, 0))
        
        # RAM Threshold
        ram_frame = ctk.CTkFrame(left_inner, fg_color="transparent")
        ram_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(ram_frame, text="RAM Threshold:", width=100, text_color="#1e293b").pack(side="left")
        self.ram_entry = ctk.CTkEntry(ram_frame, width=70)
        self.ram_entry.insert(0, "80")
        self.ram_entry.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(ram_frame, text="%", text_color="#1e293b").pack(side="left", padx=(5, 0))
        
        # Disk Threshold
        disk_frame = ctk.CTkFrame(left_inner, fg_color="transparent")
        disk_frame.pack(fill="x", pady=(0, 15))
        
        ctk.CTkLabel(disk_frame, text="Disk Threshold:", width=100, text_color="#1e293b").pack(side="left")
        self.disk_entry = ctk.CTkEntry(disk_frame, width=70)
        self.disk_entry.insert(0, "90")
        self.disk_entry.pack(side="left", padx=(10, 0))
        ctk.CTkLabel(disk_frame, text="%", text_color="#1e293b").pack(side="left", padx=(5, 0))
        
        # Update Thresholds Button
        self.update_btn = ctk.CTkButton(left_inner, text="Update Thresholds", height=35, fg_color="#64748b", hover_color="#4a5568", command=self.update_thresholds)
        self.update_btn.pack(fill="x", pady=(0, 20))
        
        # Log Options
        ctk.CTkLabel(left_inner, text="Log Options", font=ctk.CTkFont(size=16, weight="bold"), text_color="#1e293b").pack(anchor="w", pady=(0, 10))
        
        ctk.CTkButton(left_inner, text="View Logs", height=40, command=self.view_logs).pack(fill="x", pady=(0, 10))
        
        save_frame = ctk.CTkFrame(left_inner, fg_color="transparent")
        save_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkButton(save_frame, text="Save Logs as CSV", height=40, fg_color="#4f46e5", command=self.save_logs_csv).pack(side="left", padx=(0, 8), fill="x", expand=True)
        ctk.CTkButton(save_frame, text="Clear Logs", height=40, fg_color="#ef4444", hover_color="#dc2626", command=self.clear_logs).pack(side="left", fill="x", expand=True)
        
        # RIGHT PANEL - Stats Display
        right = ctk.CTkFrame(columns, corner_radius=12, fg_color="white")
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        right_inner = ctk.CTkFrame(right, fg_color="transparent")
        right_inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Status
        self.status_label = ctk.CTkLabel(right_inner, text=" Monitoring Stopped", font=ctk.CTkFont(size=14), text_color="#64748b")
        self.status_label.pack(anchor="w", pady=(0, 15))
        
        # CPU Meter
        cpu_container = ctk.CTkFrame(right_inner, corner_radius=10, fg_color="#f8fafc")
        cpu_container.pack(fill="x", pady=(0, 15))
        
        cpu_inner = ctk.CTkFrame(cpu_container, fg_color="transparent")
        cpu_inner.pack(padx=15, pady=15)
        
        ctk.CTkLabel(cpu_inner, text="CPU Usage", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1e293b").pack(anchor="w")
        self.cpu_progress = ctk.CTkProgressBar(cpu_inner, height=20, corner_radius=10, progress_color="#4f46e5")
        self.cpu_progress.pack(fill="x", pady=(8, 5))
        self.cpu_label = ctk.CTkLabel(cpu_inner, text="0%", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1e293b")
        self.cpu_label.pack(anchor="center")
        
        # RAM Meter
        ram_container = ctk.CTkFrame(right_inner, corner_radius=10, fg_color="#f8fafc")
        ram_container.pack(fill="x", pady=(0, 15))
        
        ram_inner = ctk.CTkFrame(ram_container, fg_color="transparent")
        ram_inner.pack(padx=15, pady=15)
        
        ctk.CTkLabel(ram_inner, text="RAM Usage", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1e293b").pack(anchor="w")
        self.ram_progress = ctk.CTkProgressBar(ram_inner, height=20, corner_radius=10, progress_color="#4f46e5")
        self.ram_progress.pack(fill="x", pady=(8, 5))
        self.ram_label = ctk.CTkLabel(ram_inner, text="0%", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1e293b")
        self.ram_label.pack(anchor="center")
        
        # Disk Meter
        disk_container = ctk.CTkFrame(right_inner, corner_radius=10, fg_color="#f8fafc")
        disk_container.pack(fill="x", pady=(0, 15))
        
        disk_inner = ctk.CTkFrame(disk_container, fg_color="transparent")
        disk_inner.pack(padx=15, pady=15)
        
        ctk.CTkLabel(disk_inner, text="Disk Usage", font=ctk.CTkFont(size=14, weight="bold"), text_color="#1e293b").pack(anchor="w")
        self.disk_progress = ctk.CTkProgressBar(disk_inner, height=20, corner_radius=10, progress_color="#4f46e5")
        self.disk_progress.pack(fill="x", pady=(8, 5))
        self.disk_label = ctk.CTkLabel(disk_inner, text="0%", font=ctk.CTkFont(size=24, weight="bold"), text_color="#1e293b")
        self.disk_label.pack(anchor="center")
        
        # Alert area
        alert_container = ctk.CTkFrame(right_inner, corner_radius=10, fg_color="#fef2f2", border_width=1, border_color="#fecaca")
        alert_container.pack(fill="x")
        
        alert_inner = ctk.CTkFrame(alert_container, fg_color="transparent")
        alert_inner.pack(padx=15, pady=12)
        
        ctk.CTkLabel(alert_inner, text="Alerts", font=ctk.CTkFont(size=12, weight="bold"), text_color="#dc2626").pack(anchor="w")
        self.alert_label = ctk.CTkLabel(alert_inner, text="No alerts", font=ctk.CTkFont(size=11), text_color="#64748b")
        self.alert_label.pack(anchor="w", pady=(5, 0))
    
    def toggle_email_settings(self):
        if self.email_enabled.get():
            self.email_frame.pack(fill="x", pady=(10, 0))
        else:
            self.email_frame.pack_forget()
    
    def send_email_alert(self, subject, message):
        if not self.email_enabled.get():
            return
        
        try:
            sender = self.email_from_entry.get().strip()
            password = self.email_pass_entry.get().strip()
            receiver = self.email_to_entry.get().strip()
            
            if not sender or not password or not receiver:
                return
            
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = subject
            
            body = f"""
            System Resource Alert!
            
            {message}
            
            Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            
            Please check your system immediately.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            print(f"Email error: {e}")
    
    def send_test_email(self):
        if not self.email_enabled.get():
            messagebox.showwarning("Warning", "Please enable email alerts first")
            return
        
        sender = self.email_from_entry.get().strip()
        password = self.email_pass_entry.get().strip()
        receiver = self.email_to_entry.get().strip()
        
        if not sender or not password or not receiver:
            messagebox.showwarning("Warning", "Please fill all email fields")
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = sender
            msg['To'] = receiver
            msg['Subject'] = "Test Email from System Monitor"
            
            body = "This is a test email from your System Resource Monitor. Email alerts are working properly!"
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sender, password)
            server.send_message(msg)
            server.quit()
            
            messagebox.showinfo("Success", "Test email sent successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send email: {e}")
    
    def show_alert_popup(self, title, message):
        alert_window = ctk.CTkToplevel(self.root)
        alert_window.title("Alert!")
        alert_window.geometry("350x150")
        alert_window.resizable(False, False)
        
        alert_window.transient(self.root)
        alert_window.grab_set()
        alert_window.focus_force()
        alert_window.lift()
        
        frame = ctk.CTkFrame(alert_window, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame, text="!!!", font=ctk.CTkFont(size=40)).pack()
        ctk.CTkLabel(frame, text=title, font=ctk.CTkFont(size=14, weight="bold"), text_color="#dc2626").pack(pady=(10, 5))
        ctk.CTkLabel(frame, text=message, font=ctk.CTkFont(size=12), text_color="#1e293b").pack()
        
        ctk.CTkButton(frame, text="OK", width=80, command=alert_window.destroy).pack(pady=(15, 0))
        
        print('\a')
    
    def update_thresholds(self):
        try:
            self.cpu_threshold = int(self.cpu_entry.get())
            self.ram_threshold = int(self.ram_entry.get())
            self.disk_threshold = int(self.disk_entry.get())
            self.alert_shown_cpu = False
            self.alert_shown_ram = False
            self.alert_shown_disk = False
            messagebox.showinfo("Success", "Thresholds updated successfully!")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers!")
    
    def get_cpu_usage(self):
        return psutil.cpu_percent(interval=0.5)
    
    def get_ram_usage(self):
        return psutil.virtual_memory().percent
    
    def get_disk_usage(self):
        return psutil.disk_usage('/').percent
    
    def log_data(self, cpu, ram, disk, alerts):
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                cpu,
                ram,
                disk,
                ", ".join(alerts) if alerts else "Normal"
            ])
    
    def update_display(self):
        if not self.monitoring:
            return
        
        cpu = self.get_cpu_usage()
        ram = self.get_ram_usage()
        disk = self.get_disk_usage()
        
        # Update progress bars
        self.cpu_progress.set(cpu / 100)
        self.ram_progress.set(ram / 100)
        self.disk_progress.set(disk / 100)
        
        # Update labels
        self.cpu_label.configure(text=f"{cpu:.1f}%")
        self.ram_label.configure(text=f"{ram:.1f}%")
        self.disk_label.configure(text="{:.1f}%".format(disk))
        
        # Change colors based on usage
        cpu_color = "#10b981" if cpu < 70 else ("#f59e0b" if cpu < 85 else "#ef4444")
        ram_color = "#10b981" if ram < 70 else ("#f59e0b" if ram < 85 else "#ef4444")
        disk_color = "#10b981" if disk < 80 else ("#f59e0b" if disk < 90 else "#ef4444")
        
        self.cpu_progress.configure(progress_color=cpu_color)
        self.ram_progress.configure(progress_color=ram_color)
        self.disk_progress.configure(progress_color=disk_color)
        
        # Check alerts
        alerts = []
        
        if cpu > self.cpu_threshold:
            alert_msg = f"CPU: {cpu:.1f}% > {self.cpu_threshold}%"
            alerts.append(alert_msg)
            if not self.alert_shown_cpu:
                self.alert_shown_cpu = True
                self.show_alert_popup("CPU Alert!", f"CPU usage is {cpu:.1f}% which exceeds threshold of {self.cpu_threshold}%")
                self.send_email_alert("CPU Alert!", alert_msg)
        else:
            self.alert_shown_cpu = False
        
        if ram > self.ram_threshold:
            alert_msg = f"RAM: {ram:.1f}% > {self.ram_threshold}%"
            alerts.append(alert_msg)
            if not self.alert_shown_ram:
                self.alert_shown_ram = True
                self.show_alert_popup("RAM Alert!", f"RAM usage is {ram:.1f}% which exceeds threshold of {self.ram_threshold}%")
                self.send_email_alert("RAM Alert!", alert_msg)
        else:
            self.alert_shown_ram = False
        
        if disk > self.disk_threshold:
            alert_msg = f"Disk: {disk:.1f}% > {self.disk_threshold}%"
            alerts.append(alert_msg)
            if not self.alert_shown_disk:
                self.alert_shown_disk = True
                self.show_alert_popup("Disk Alert!", f"Disk usage is {disk:.1f}% which exceeds threshold of {self.disk_threshold}%")
                self.send_email_alert("Disk Alert!", alert_msg)
        else:
            self.alert_shown_disk = False
        
        # Update alert label
        if alerts:
            self.alert_label.configure(text=" | ".join(alerts), text_color="#dc2626")
        else:
            self.alert_label.configure(text="All systems normal", text_color="#10b981")
        
        # Log data
        self.log_data(cpu, ram, disk, alerts)
        
        # Schedule next update
        self.root.after(2000, self.update_display)
    
    def start_monitoring(self):
        try:
            self.cpu_threshold = int(self.cpu_entry.get())
            self.ram_threshold = int(self.ram_entry.get())
            self.disk_threshold = int(self.disk_entry.get())
        except:
            pass
        
        self.monitoring = True
        self.alert_shown_cpu = False
        self.alert_shown_ram = False
        self.alert_shown_disk = False
        
        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.status_label.configure(text=" Monitoring Active", text_color="#10b981")
        self.alert_label.configure(text="Monitoring in progress...", text_color="#64748b")
        
        self.update_display()
    
    def stop_monitoring(self):
        self.monitoring = False
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.status_label.configure(text=" Monitoring Stopped", text_color="#64748b")
        self.alert_label.configure(text="No alerts", text_color="#64748b")
    
    def save_logs_csv(self):
        if not os.path.exists(self.log_file) or os.path.getsize(self.log_file) == 0:
            messagebox.showwarning("Warning", "No logs to save")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"system_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        if filename:
            import shutil
            shutil.copy(self.log_file, filename)
            messagebox.showinfo("Success", f"Logs saved to {filename}")
    
    def view_logs(self):
        log_window = ctk.CTkToplevel(self.root)
        log_window.title("System Logs")
        log_window.geometry("850x550")
        
        log_window.transient(self.root)
        log_window.grab_set()
        log_window.focus_force()
        log_window.lift()
        
        tree_frame = ctk.CTkFrame(log_window, fg_color="white", corner_radius=8)
        tree_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        tree = ttk.Treeview(tree_frame, show="headings", height=20)
        tree.pack(fill="both", expand=True, padx=10, pady=10)
        
        columns = ["Timestamp", "CPU (%)", "RAM (%)", "Disk (%)", "Alert"]
        tree["columns"] = columns
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
        tree.column("Alert", width=250)
        
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if i == 0:
                        continue
                    tree.insert("", "end", values=row)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        vsb.pack(side="right", fill="y")
        tree.configure(yscrollcommand=vsb.set)
        
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        hsb.pack(side="bottom", fill="x")
        tree.configure(xscrollcommand=hsb.set)
    
    def clear_logs(self):
        if messagebox.askyesno("Confirm", "Clear all logs?"):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "CPU (%)", "RAM (%)", "Disk (%)", "Alert"])
            messagebox.showinfo("Success", "Logs cleared successfully!")

if __name__ == "__main__":
    app = SystemMonitorGUI()
