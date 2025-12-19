#!/usr/bin/env python3
"""
GUI interface for Password Strength Analyzer using tkinter.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import List
import logging

from password_analyzer import PasswordAnalyzer, WordlistGenerator
from password_analyzer.eula import EULAManager

logger = logging.getLogger(__name__)


class PasswordAnalyzerGUI:
    """
    Tkinter-based GUI for password analysis.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Password Strength Analyzer")
        self.root.geometry("900x700")
        
        self.analyzer = PasswordAnalyzer()
        self.generator = WordlistGenerator()
        self.eula = EULAManager()
        
        # Check EULA on startup
        if not self.eula.check_eula_accepted():
            self.show_eula_dialog()
        
        self.create_widgets()
    
    def show_eula_dialog(self):
        """Show EULA acceptance dialog."""
        eula_window = tk.Toplevel(self.root)
        eula_window.title("End User License Agreement")
        eula_window.geometry("700x600")
        eula_window.transient(self.root)
        eula_window.grab_set()
        
        # EULA text
        eula_text = scrolledtext.ScrolledText(
            eula_window,
            wrap=tk.WORD,
            width=80,
            height=30,
            font=("Courier", 9)
        )
        eula_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        eula_text.insert(1.0, self.eula.get_eula_text())
        eula_text.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(eula_window)
        button_frame.pack(pady=10)
        
        def accept():
            if self.eula.accept_eula():
                eula_window.destroy()
            else:
                messagebox.showerror("Error", "Failed to record EULA acceptance.")
        
        def decline():
            messagebox.showwarning(
                "EULA Required",
                "You must accept the EULA to use this software."
            )
            self.root.quit()
        
        ttk.Button(button_frame, text="Accept", command=accept).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Decline", command=decline).pack(side=tk.LEFT, padx=5)
        
        # Wait for window to close
        self.root.wait_window(eula_window)
    
    def create_widgets(self):
        """Create all GUI widgets."""
        # Create notebook (tabbed interface)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tab 1: Single Password Analysis
        self.single_tab = ttk.Frame(notebook)
        notebook.add(self.single_tab, text="Analyze Password")
        self.create_single_password_tab()
        
        # Tab 2: Batch Analysis
        self.batch_tab = ttk.Frame(notebook)
        notebook.add(self.batch_tab, text="Batch Analysis")
        self.create_batch_analysis_tab()
        
        # Tab 3: Wordlist Generator
        self.wordlist_tab = ttk.Frame(notebook)
        notebook.add(self.wordlist_tab, text="Educational Wordlist")
        self.create_wordlist_tab()
        
        # Status bar
        self.status_bar = ttk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_single_password_tab(self):
        """Create single password analysis tab."""
        # Input frame
        input_frame = ttk.LabelFrame(self.single_tab, text="Password Input", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="Password:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.password_entry = ttk.Entry(input_frame, width=50, show="*")
        self.password_entry.grid(row=0, column=1, pady=5, padx=5)
        
        self.show_password_var = tk.BooleanVar()
        ttk.Checkbutton(
            input_frame,
            text="Show Password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        ).grid(row=0, column=2, pady=5)
        
        # User inputs frame
        user_input_frame = ttk.LabelFrame(
            self.single_tab,
            text="Contextual Information (Optional)",
            padding=10
        )
        user_input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            user_input_frame,
            text="Enter personal info to check if password contains it (comma-separated):"
        ).pack(anchor=tk.W)
        
        self.user_inputs_entry = ttk.Entry(user_input_frame, width=70)
        self.user_inputs_entry.pack(fill=tk.X, pady=5)
        
        ttk.Label(
            user_input_frame,
            text="Examples: john, smith, john@email.com, 1990, mydog",
            font=("Arial", 8, "italic")
        ).pack(anchor=tk.W)
        
        # Analyze button
        button_frame = ttk.Frame(self.single_tab)
        button_frame.pack(pady=10)
        
        ttk.Button(
            button_frame,
            text="Analyze Password",
            command=self.analyze_single_password,
            style="Accent.TButton"
        ).pack()
        
        # Results frame
        results_frame = ttk.LabelFrame(self.single_tab, text="Analysis Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Courier", 9)
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Configure text tags for colored output
        self.results_text.tag_config("critical", foreground="red", font=("Courier", 9, "bold"))
        self.results_text.tag_config("warning", foreground="orange")
        self.results_text.tag_config("good", foreground="green")
        self.results_text.tag_config("info", foreground="blue")
        self.results_text.tag_config("header", font=("Courier", 10, "bold"))
    
    def create_batch_analysis_tab(self):
        """Create batch analysis tab."""
        # Input frame
        input_frame = ttk.LabelFrame(self.batch_tab, text="Input File", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(input_frame, text="Password File:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.batch_file_entry = ttk.Entry(input_frame, width=50)
        self.batch_file_entry.grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Button(
            input_frame,
            text="Browse",
            command=self.browse_batch_file
        ).grid(row=0, column=2, pady=5)
        
        ttk.Label(
            input_frame,
            text="File should contain one password per line",
            font=("Arial", 8, "italic")
        ).grid(row=1, column=0, columnspan=3, sticky=tk.W)
        
        # User inputs
        user_input_frame = ttk.LabelFrame(self.batch_tab, text="Contextual Information", padding=10)
        user_input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(user_input_frame, text="User Inputs (comma-separated):").pack(anchor=tk.W)
        self.batch_user_inputs = ttk.Entry(user_input_frame, width=70)
        self.batch_user_inputs.pack(fill=tk.X, pady=5)
        
        # Analyze button
        ttk.Button(
            self.batch_tab,
            text="Analyze Batch",
            command=self.analyze_batch
        ).pack(pady=10)
        
        # Results
        results_frame = ttk.LabelFrame(self.batch_tab, text="Batch Results", padding=10)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.batch_results_text = scrolledtext.ScrolledText(
            results_frame,
            wrap=tk.WORD,
            font=("Courier", 9)
        )
        self.batch_results_text.pack(fill=tk.BOTH, expand=True)
    
    def create_wordlist_tab(self):
        """Create educational wordlist generator tab."""
        # Warning frame
        warning_frame = ttk.Frame(self.wordlist_tab)
        warning_frame.pack(fill=tk.X, padx=10, pady=10)
        
        warning_text = (
            "⚠️  EDUCATIONAL USE ONLY ⚠️\n\n"
            "This generates a small wordlist for password awareness.\n"
            "Use ONLY for authorized security testing and education."
        )
        
        warning_label = ttk.Label(
            warning_frame,
            text=warning_text,
            background="lightyellow",
            relief=tk.RIDGE,
            padding=10,
            font=("Arial", 9, "bold")
        )
        warning_label.pack(fill=tk.X)
        
        # Input frame
        input_frame = ttk.LabelFrame(self.wordlist_tab, text="User Contextual Items", padding=10)
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(
            input_frame,
            text="Enter items to include (one per line):"
        ).pack(anchor=tk.W)
        
        self.wordlist_inputs = scrolledtext.ScrolledText(
            input_frame,
            wrap=tk.WORD,
            width=60,
            height=8,
            font=("Arial", 10)
        )
        self.wordlist_inputs.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Label(
            input_frame,
            text="Examples: john, smith, company_name, pet_name",
            font=("Arial", 8, "italic")
        ).pack(anchor=tk.W)
        
        # Output frame
        output_frame = ttk.LabelFrame(self.wordlist_tab, text="Output File", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(output_frame, text="Output Path:").grid(row=0, column=0, sticky=tk.W)
        self.wordlist_output_entry = ttk.Entry(output_frame, width=50)
        self.wordlist_output_entry.insert(0, "educational_wordlist.txt")
        self.wordlist_output_entry.grid(row=0, column=1, padx=5)
        
        ttk.Button(
            output_frame,
            text="Browse",
            command=self.browse_wordlist_output
        ).grid(row=0, column=2)
        
        # Generate button
        button_frame = ttk.Frame(self.wordlist_tab)
        button_frame.pack(pady=10)
        
        self.authorize_var = tk.BooleanVar()
        ttk.Checkbutton(
            button_frame,
            text="I confirm this is for AUTHORIZED use only",
            variable=self.authorize_var
        ).pack()
        
        ttk.Button(
            button_frame,
            text="Generate Educational Wordlist",
            command=self.generate_wordlist
        ).pack(pady=10)
        
        # Status
        self.wordlist_status = ttk.Label(self.wordlist_tab, text="", font=("Arial", 9))
        self.wordlist_status.pack()
    
    def toggle_password_visibility(self):
        """Toggle password visibility."""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")
    
    def analyze_single_password(self):
        """Analyze a single password."""
        password = self.password_entry.get()
        
        if not password:
            messagebox.showwarning("Input Required", "Please enter a password to analyze.")
            return
        
        # Get user inputs
        user_inputs_str = self.user_inputs_entry.get()
        user_inputs = [item.strip() for item in user_inputs_str.split(',') if item.strip()]
        
        # Log action
        self.eula.log_action("GUI: Single password analysis", f"Length: {len(password)}")
        
        # Analyze
        self.status_bar.config(text="Analyzing...")
        self.root.update()
        
        result = self.analyzer.analyze(password, user_inputs=user_inputs)
        
        # Display results
        self.display_analysis_result(result)
        
        self.status_bar.config(text="Analysis complete")
    
    def display_analysis_result(self, result):
        """Display analysis results in the text widget."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete(1.0, tk.END)
        
        # Header
        self.results_text.insert(tk.END, "="*80 + "\n", "header")
        self.results_text.insert(tk.END, "PASSWORD ANALYSIS REPORT\n", "header")
        self.results_text.insert(tk.END, "="*80 + "\n\n", "header")
        
        # Overall risk
        risk = result['overall_risk']
        risk_tag = "critical" if risk in ["CRITICAL", "VERY_HIGH"] else "warning" if risk in ["HIGH", "MEDIUM"] else "good"
        self.results_text.insert(tk.END, f"Overall Risk Level: ", "info")
        self.results_text.insert(tk.END, f"{risk}\n", risk_tag)
        
        # Basic info
        self.results_text.insert(tk.END, f"Password Length: {result['password_length']} characters\n")
        self.results_text.insert(tk.END, f"zxcvbn Score: {result['zxcvbn_score']}/4\n\n")
        
        # Critical warnings
        if result['has_contextual_risk']:
            self.results_text.insert(tk.END, "🚨 CRITICAL WARNING:\n", "critical")
            self.results_text.insert(
                tk.END,
                f"Password contains personal information: {', '.join(result['contextual_matches'])}\n\n",
                "critical"
            )
        
        # Crack times
        self.results_text.insert(tk.END, "Estimated Crack Times:\n", "info")
        crack_times = result['crack_times_display']
        self.results_text.insert(tk.END, f"  Online (throttled): {crack_times.get('online_throttling', 'N/A')}\n")
        self.results_text.insert(tk.END, f"  Online (no throttle): {crack_times.get('online_no_throttling', 'N/A')}\n")
        self.results_text.insert(tk.END, f"  Offline (slow): {crack_times.get('offline_slow_hashing_1e4_per_second', 'N/A')}\n")
        self.results_text.insert(tk.END, f"  Offline (fast): {crack_times.get('offline_fast_hashing_1e10_per_second', 'N/A')}\n\n")
        
        # Entropy
        if result['entropy']:
            self.results_text.insert(tk.END, "Entropy Analysis:\n", "info")
            self.results_text.insert(tk.END, f"  Entropy: {result['entropy']['entropy_bits']:.1f} bits\n")
            self.results_text.insert(tk.END, f"  Strength: {result['entropy']['strength_rating']}\n\n")
        
        # Recommendations
        self.results_text.insert(tk.END, "Recommendations:\n", "info")
        for rec in result['recommendations']:
            self.results_text.insert(tk.END, f"  {rec}\n")
        
        self.results_text.config(state=tk.DISABLED)
    
    def browse_batch_file(self):
        """Browse for batch input file."""
        filename = filedialog.askopenfilename(
            title="Select Password File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filename:
            self.batch_file_entry.delete(0, tk.END)
            self.batch_file_entry.insert(0, filename)
    
    def analyze_batch(self):
        """Analyze batch of passwords."""
        filepath = self.batch_file_entry.get()
        
        if not filepath:
            messagebox.showwarning("Input Required", "Please select a password file.")
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                passwords = [line.strip() for line in f if line.strip()]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file: {e}")
            return
        
        if not passwords:
            messagebox.showwarning("Empty File", "No passwords found in file.")
            return
        
        # Get user inputs
        user_inputs_str = self.batch_user_inputs.get()
        user_inputs = [item.strip() for item in user_inputs_str.split(',') if item.strip()]
        
        # Log action
        self.eula.log_action("GUI: Batch analysis", f"File: {filepath}, Count: {len(passwords)}")
        
        # Analyze
        self.status_bar.config(text=f"Analyzing {len(passwords)} passwords...")
        self.root.update()
        
        results = self.analyzer.batch_analyze(passwords, user_inputs=user_inputs)
        
        # Display summary
        self.batch_results_text.config(state=tk.NORMAL)
        self.batch_results_text.delete(1.0, tk.END)
        
        self.batch_results_text.insert(tk.END, "="*80 + "\n")
        self.batch_results_text.insert(tk.END, "BATCH ANALYSIS SUMMARY\n")
        self.batch_results_text.insert(tk.END, "="*80 + "\n\n")
        self.batch_results_text.insert(tk.END, f"Total passwords analyzed: {len(results)}\n\n")
        
        # Risk distribution
        risk_counts = {}
        for result in results:
            risk = result['overall_risk']
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        self.batch_results_text.insert(tk.END, "Risk Distribution:\n")
        for risk, count in sorted(risk_counts.items()):
            percentage = count / len(results) * 100
            self.batch_results_text.insert(tk.END, f"  {risk}: {count} ({percentage:.1f}%)\n")
        
        self.batch_results_text.insert(tk.END, "\n" + "="*80 + "\n")
        self.batch_results_text.insert(tk.END, "INDIVIDUAL RESULTS\n")
        self.batch_results_text.insert(tk.END, "="*80 + "\n\n")
        
        for i, result in enumerate(results, 1):
            self.batch_results_text.insert(tk.END, f"Password #{i}:\n")
            self.batch_results_text.insert(tk.END, f"  Score: {result['zxcvbn_score']}/4\n")
            self.batch_results_text.insert(tk.END, f"  Risk: {result['overall_risk']}\n")
            if result['has_contextual_risk']:
                self.batch_results_text.insert(tk.END, f"  ⚠️  Contains: {result['contextual_matches']}\n")
            self.batch_results_text.insert(tk.END, "\n")
        
        self.batch_results_text.config(state=tk.DISABLED)
        self.status_bar.config(text="Batch analysis complete")
    
    def browse_wordlist_output(self):
        """Browse for wordlist output location."""
        filename = filedialog.asksaveasfilename(
            title="Save Educational Wordlist",
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filename:
            self.wordlist_output_entry.delete(0, tk.END)
            self.wordlist_output_entry.insert(0, filename)
    
    def generate_wordlist(self):
        """Generate educational wordlist."""
        if not self.authorize_var.get():
            messagebox.showwarning(
                "Authorization Required",
                "You must confirm authorized use by checking the checkbox."
            )
            return
        
        # Show confirmation dialog
        response = messagebox.askyesno(
            "Confirm Authorization",
            self.eula.get_export_warning() + "\n\nProceed with export?"
        )
        
        if not response:
            return
        
        # Get inputs
        inputs_text = self.wordlist_inputs.get(1.0, tk.END)
        user_inputs = [line.strip() for line in inputs_text.split('\n') if line.strip()]
        
        if not user_inputs:
            messagebox.showwarning("Input Required", "Please enter at least one contextual item.")
            return
        
        output_path = self.wordlist_output_entry.get()
        
        # Log action
        self.eula.log_action("GUI: Wordlist export", f"Items: {len(user_inputs)}")
        
        # Generate
        self.status_bar.config(text="Generating wordlist...")
        self.root.update()
        
        result = self.generator.generate_educational_wordlist(user_inputs, output_path)
        
        if result['success']:
            self.wordlist_status.config(
                text=f"✅ Generated: {result['total_entries']} entries saved to {output_path}",
                foreground="green"
            )
            messagebox.showinfo(
                "Success",
                f"Educational wordlist generated!\n\n"
                f"Path: {result['path']}\n"
                f"Total entries: {result['total_entries']}\n\n"
                f"Remember: Use ONLY for authorized purposes!"
            )
        else:
            self.wordlist_status.config(
                text=f"❌ Error: {result.get('error', 'Unknown error')}",
                foreground="red"
            )
            messagebox.showerror("Error", f"Failed to generate wordlist: {result.get('error')}")
        
        self.status_bar.config(text="Ready")


def main():
    """Launch the GUI application."""
    root = tk.Tk()
    
    # Set theme
    style = ttk.Style()
    try:
        style.theme_use('clam')
    except:
        pass
    
    app = PasswordAnalyzerGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
