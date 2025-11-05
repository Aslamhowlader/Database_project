import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext
from auth_functions import AuthManager
import json
from datetime import datetime

class Dashboard:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.auth = AuthManager()
        
        self.COLORS = {
            'primary': '#2c3e50',
            'secondary': '#3498db',
            'success': '#27ae60',
            'warning': '#f39c12',
            'danger': '#e74c3c',
            'info': '#17a2b8',
            'light_bg': '#ecf0f1',
            'white': '#ffffff',
            'text_dark': '#2c3e50',
            'text_light': '#7f8c8d'
        }
        
        self.FONTS = {
            'title': ('Arial', 20, 'bold'),
            'header': ('Arial', 16, 'bold'),
            'subheader': ('Arial', 14, 'bold'),
            'body': ('Arial', 10),
            'small': ('Arial', 9)
        }
        
        self.setup_ui()

    def setup_ui(self):
        """Setup the main dashboard interface"""
        self.root.title(f"Smart Citizen Portal - {self.user_data['name']} ({self.user_data['role']})")
        self.root.geometry("1200x700")
        self.root.configure(bg=self.COLORS['light_bg'])
        
        # Create main container
        main_container = tk.Frame(self.root, bg=self.COLORS['light_bg'])
        main_container.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Header
        self.create_header(main_container)
        
        # Content area
        self.content_frame = tk.Frame(main_container, bg=self.COLORS['white'])
        self.content_frame.pack(fill='both', expand=True, pady=10)
        
        # Show appropriate dashboard based on role
        if self.user_data['role'] == 'Administrator':
            self.show_admin_dashboard()
        elif self.user_data['role'] == 'Government Officer':
            self.show_officer_dashboard()
        else:
            self.show_citizen_dashboard()

    def create_header(self, parent):
        """Create dashboard header"""
        header_frame = tk.Frame(parent, bg=self.COLORS['primary'], height=80)
        header_frame.pack(fill='x', pady=(0, 10))
        header_frame.pack_propagate(False)
        
        # Left side - Welcome message
        welcome_frame = tk.Frame(header_frame, bg=self.COLORS['primary'])
        welcome_frame.pack(side='left', padx=20, pady=10)
        
        tk.Label(welcome_frame, text=f"Welcome, {self.user_data['name']}", 
                font=self.FONTS['header'], bg=self.COLORS['primary'], fg='white').pack(anchor='w')
        
        role_text = f"Role: {self.user_data['role']}"
        if self.user_data.get('department'):
            role_text += f" | Department: {self.user_data['department']}"
        
        tk.Label(welcome_frame, text=role_text, 
                font=self.FONTS['body'], bg=self.COLORS['primary'], fg=self.COLORS['light_bg']).pack(anchor='w')
        
        # Right side - Navigation and logout
        nav_frame = tk.Frame(header_frame, bg=self.COLORS['primary'])
        nav_frame.pack(side='right', padx=20, pady=10)
        
        # Role-specific navigation - ADMIN ONLY
        if self.user_data['role'] == 'Administrator':
            menus = ['Dashboard', 'User Management', 'Services', 'Applications', 'Report Management', 'System Reports']
        elif self.user_data['role'] == 'Government Officer':
            menus = ['Dashboard', 'Services', 'Applications', 'Department Reports', 'Profile']
        else:
            menus = ['Dashboard', 'My Applications', 'Available Services', 'Submit Report', 'My Reports', 'Profile']
        
        for menu in menus:
            tk.Button(nav_frame, text=menu, font=self.FONTS['body'], 
                     bg=self.COLORS['secondary'], fg='white', relief='flat',
                     command=lambda m=menu: self.handle_navigation(m)).pack(side='left', padx=5)
        
        # Logout button
        tk.Button(nav_frame, text="Logout", font=self.FONTS['body'], 
                 bg=self.COLORS['danger'], fg='white', relief='flat',
                 command=self.logout).pack(side='left', padx=10)

    def handle_navigation(self, menu):
        """Handle navigation menu clicks"""
        # Clear current content
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # Show selected section
        if menu == 'Dashboard':
            if self.user_data['role'] == 'Administrator':
                self.show_admin_dashboard()
            elif self.user_data['role'] == 'Government Officer':
                self.show_officer_dashboard()
            else:
                self.show_citizen_dashboard()
        elif menu == 'User Management' and self.user_data['role'] == 'Administrator':
            self.show_user_management()
        elif menu == 'Services':
            self.show_services()
        elif menu == 'Applications':
            self.show_applications()
        elif menu == 'Report Management' and self.user_data['role'] == 'Administrator':
            self.show_report_management()
        elif menu == 'My Applications':
            self.show_my_applications()
        elif menu == 'Available Services':
            self.show_available_services()
        elif menu == 'Submit Report':
            self.show_submit_report()
        elif menu == 'My Reports':
            self.show_my_reports()
        elif menu == 'Department Reports':
            self.show_department_reports()
        elif menu == 'Profile':
            self.show_profile()
        elif menu == 'System Reports' and self.user_data['role'] == 'Administrator':
            self.show_system_reports()

    # Admin Features
    def show_admin_dashboard(self):
        """Show admin dashboard with statistics"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="Admin Dashboard", font=self.FONTS['title'], 
                bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        # Get statistics
        success, stats = self.auth.get_user_stats()
        report_success, report_stats = self.auth.get_report_stats()
        
        if success and report_success:
            # Statistics cards
            stats_frame = tk.Frame(container, bg=self.COLORS['white'])
            stats_frame.pack(fill='x', pady=20)
            
            # Total Users Card
            total_card = self.create_stat_card(stats_frame, "Total Users", 
                                             stats['total_users'], self.COLORS['primary'])
            total_card.pack(side='left', padx=10, fill='x', expand=True)
            
            # Recent Registrations Card
            recent_card = self.create_stat_card(stats_frame, "Recent Users (7 days)", 
                                              stats['recent_registrations'], self.COLORS['success'])
            recent_card.pack(side='left', padx=10, fill='x', expand=True)
            
            # Total Reports Card
            reports_card = self.create_stat_card(stats_frame, "Total Reports", 
                                               report_stats['total_reports'], self.COLORS['warning'])
            reports_card.pack(side='left', padx=10, fill='x', expand=True)
            
            # Recent Reports Card
            recent_reports_card = self.create_stat_card(stats_frame, "Recent Reports (7 days)", 
                                                      report_stats['recent_reports'], self.COLORS['danger'])
            recent_reports_card.pack(side='left', padx=10, fill='x', expand=True)
            
            # Quick actions
            actions_frame = tk.Frame(container, bg=self.COLORS['white'])
            actions_frame.pack(fill='x', pady=20)
            
            tk.Button(actions_frame, text="Manage Users", font=self.FONTS['body'],
                     bg=self.COLORS['secondary'], fg='white', relief='raised',
                     command=lambda: self.handle_navigation('User Management')).pack(side='left', padx=5)
            
            tk.Button(actions_frame, text="View Applications", font=self.FONTS['body'],
                     bg=self.COLORS['success'], fg='white', relief='raised',
                     command=lambda: self.handle_navigation('Applications')).pack(side='left', padx=5)
            
            tk.Button(actions_frame, text="Report Management", font=self.FONTS['body'],
                     bg=self.COLORS['warning'], fg='white', relief='raised',
                     command=lambda: self.handle_navigation('Report Management')).pack(side='left', padx=5)
            
            tk.Button(actions_frame, text="System Reports", font=self.FONTS['body'],
                     bg=self.COLORS['info'], fg='white', relief='raised',
                     command=lambda: self.handle_navigation('System Reports')).pack(side='left', padx=5)
        else:
            tk.Label(container, text="Could not load statistics", 
                    font=self.FONTS['body'], bg=self.COLORS['white']).pack(pady=20)

    def show_report_management(self):
        """Show admin report management interface"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="Report Management - All Reports", font=self.FONTS['title'], 
                bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        # Get all reports
        success, reports = self.auth.get_all_reports()
        
        if success:
            # Create treeview for reports
            tree_frame = tk.Frame(container, bg=self.COLORS['white'])
            tree_frame.pack(fill='both', expand=True, pady=10)
            
            # Treeview scrollbar
            scrollbar = ttk.Scrollbar(tree_frame)
            scrollbar.pack(side='right', fill='y')
            
            # Treeview
            tree = ttk.Treeview(tree_frame, columns=('ID', 'Title', 'Reporter', 'Category', 'Priority', 'Status', 'Assigned To', 'Created Date'), 
                               show='headings', yscrollcommand=scrollbar.set, height=15)
            
            # Define headings
            tree.heading('ID', text='ID')
            tree.heading('Title', text='Report Title')
            tree.heading('Reporter', text='Reporter')
            tree.heading('Category', text='Category')
            tree.heading('Priority', text='Priority')
            tree.heading('Status', text='Status')
            tree.heading('Assigned To', text='Assigned To')
            tree.heading('Created Date', text='Created Date')
            
            # Configure columns
            tree.column('ID', width=50)
            tree.column('Title', width=200)
            tree.column('Reporter', width=150)
            tree.column('Category', width=120)
            tree.column('Priority', width=80)
            tree.column('Status', width=100)
            tree.column('Assigned To', width=120)
            tree.column('Created Date', width=120)
            
            # Add reports to treeview
            for report in reports:
                created_date = report['created_at'].strftime('%Y-%m-%d') if report['created_at'] else 'N/A'
                tree.insert('', 'end', values=(
                    report['id'], 
                    report['title'], 
                    report['reporter_name'],
                    report['category'],
                    report['priority'],
                    report['status'],
                    report['assigned_officer'] or 'Not Assigned',
                    created_date
                ))
            
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=tree.yview)
            
            # Action buttons frame
            action_frame = tk.Frame(container, bg=self.COLORS['white'])
            action_frame.pack(fill='x', pady=10)
            
            tk.Button(action_frame, text="Refresh", font=self.FONTS['body'],
                     bg=self.COLORS['secondary'], fg='white', relief='raised',
                     command=self.show_report_management).pack(side='left', padx=5)
            
            tk.Button(action_frame, text="View Details", font=self.FONTS['body'],
                     bg=self.COLORS['primary'], fg='white', relief='raised',
                     command=lambda: self.view_report_details(tree)).pack(side='left', padx=5)
            
            tk.Button(action_frame, text="Edit Report", font=self.FONTS['body'],
                     bg=self.COLORS['warning'], fg='white', relief='raised',
                     command=lambda: self.edit_report(tree)).pack(side='left', padx=5)
            
            tk.Button(action_frame, text="Update Status", font=self.FONTS['body'],
                     bg=self.COLORS['success'], fg='white', relief='raised',
                     command=lambda: self.update_report_status_dialog(tree)).pack(side='left', padx=5)
            
            tk.Button(action_frame, text="Assign Officer", font=self.FONTS['body'],
                     bg=self.COLORS['info'], fg='white', relief='raised',
                     command=lambda: self.assign_report_dialog(tree)).pack(side='left', padx=5)
            
            tk.Button(action_frame, text="Delete Report", font=self.FONTS['body'],
                     bg=self.COLORS['danger'], fg='white', relief='raised',
                     command=lambda: self.delete_report(tree)).pack(side='left', padx=5)
            
        else:
            tk.Label(container, text="No reports found.", 
                    font=self.FONTS['body'], bg=self.COLORS['white']).pack(pady=20)

    def view_report_details(self, tree):
        """View detailed information about selected report"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a report first")
            return
        
        report_id = tree.item(selected[0])['values'][0]
        success, report = self.auth.get_report_by_id(report_id)
        
        if success:
            # Create details dialog
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Report Details - ID: {report_id}")
            dialog.geometry("600x500")
            dialog.configure(bg=self.COLORS['white'])
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Main container
            main_frame = tk.Frame(dialog, bg=self.COLORS['white'])
            main_frame.pack(fill='both', expand=True, padx=20, pady=20)
            
            tk.Label(main_frame, text=f"Report Details - ID: {report_id}", 
                    font=self.FONTS['header'], bg=self.COLORS['white']).pack(pady=10)
            
            # Create scrollable frame
            canvas = tk.Canvas(main_frame, bg=self.COLORS['white'], highlightthickness=0)
            scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
            scrollable_frame = tk.Frame(canvas, bg=self.COLORS['white'])
            
            scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=scrollbar.set)
            
            # Report details
            details_text = f"""
Report Information:
─────────────────
ID: {report['id']}
Title: {report['title']}
Description: {report['description']}
Category: {report['category']}
Priority: {report['priority']}
Status: {report['status']}
Location: {report['location'] or 'Not specified'}

Reporter Information:
───────────────────
Name: {report['reporter_name']}
Username: {report['reporter_username']}
Phone: {report['reporter_phone']}
Email: {report['reporter_email'] or 'Not provided'}

Assignment Information:
─────────────────────
Assigned Officer: {report['assigned_officer'] or 'Not assigned'}
Created Date: {report['created_at'].strftime('%Y-%m-%d %H:%M') if report['created_at'] else 'N/A'}
Resolved Date: {report['resolved_at'].strftime('%Y-%m-%d %H:%M') if report['resolved_at'] else 'Not resolved'}

Feedback: {report['feedback'] or 'No feedback provided'}
            """
            
            details_display = scrolledtext.ScrolledText(scrollable_frame, width=70, height=20, font=self.FONTS['body'])
            details_display.pack(fill='both', expand=True, padx=10, pady=10)
            details_display.insert('1.0', details_text)
            details_display.config(state='disabled')
            
            canvas.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Close button
            tk.Button(main_frame, text="Close", font=self.FONTS['body'],
                     bg=self.COLORS['secondary'], fg='white', relief='raised',
                     command=dialog.destroy).pack(pady=10)
        else:
            messagebox.showerror("Error", report)

    def edit_report(self, tree):
        """Edit report details"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a report first")
            return
        
        report_id = tree.item(selected[0])['values'][0]
        success, report = self.auth.get_report_by_id(report_id)
        
        if success:
            # Create edit dialog
            dialog = tk.Toplevel(self.root)
            dialog.title(f"Edit Report - ID: {report_id}")
            dialog.geometry("500x600")
            dialog.configure(bg=self.COLORS['white'])
            dialog.transient(self.root)
            dialog.grab_set()
            
            tk.Label(dialog, text=f"Edit Report - ID: {report_id}", 
                    font=self.FONTS['header'], bg=self.COLORS['white']).pack(pady=10)
            
            form_frame = tk.Frame(dialog, bg=self.COLORS['white'])
            form_frame.pack(fill='both', expand=True, padx=20, pady=10)
            
            # Title
            tk.Label(form_frame, text="Title *", font=self.FONTS['body'], 
                    bg=self.COLORS['white']).pack(anchor='w', pady=5)
            title_entry = tk.Entry(form_frame, width=50, font=self.FONTS['body'])
            title_entry.insert(0, report['title'])
            title_entry.pack(fill='x', pady=5)
            
            # Category
            tk.Label(form_frame, text="Category *", font=self.FONTS['body'], 
                    bg=self.COLORS['white']).pack(anchor='w', pady=5)
            category_var = tk.StringVar(value=report['category'])
            category_combo = ttk.Combobox(form_frame, textvariable=category_var,
                                         values=["Infrastructure", "Health", "Education", "Utility", "Environment", "Other"],
                                         state="readonly", width=50)
            category_combo.pack(fill='x', pady=5)
            
            # Priority
            tk.Label(form_frame, text="Priority", font=self.FONTS['body'], 
                    bg=self.COLORS['white']).pack(anchor='w', pady=5)
            priority_var = tk.StringVar(value=report['priority'])
            priority_combo = ttk.Combobox(form_frame, textvariable=priority_var,
                                         values=["Low", "Medium", "High", "Emergency"],
                                         state="readonly", width=50)
            priority_combo.pack(fill='x', pady=5)
            
            # Location
            tk.Label(form_frame, text="Location", font=self.FONTS['body'], 
                    bg=self.COLORS['white']).pack(anchor='w', pady=5)
            location_entry = tk.Entry(form_frame, width=50, font=self.FONTS['body'])
            location_entry.insert(0, report['location'] or '')
            location_entry.pack(fill='x', pady=5)
            
            # Description
            tk.Label(form_frame, text="Description *", font=self.FONTS['body'], 
                    bg=self.COLORS['white']).pack(anchor='w', pady=5)
            desc_text = scrolledtext.ScrolledText(form_frame, width=50, height=10, font=self.FONTS['body'])
            desc_text.pack(fill='both', expand=True, pady=5)
            desc_text.insert('1.0', report['description'])
            
            def save_changes():
                title = title_entry.get().strip()
                description = desc_text.get('1.0', tk.END).strip()
                location = location_entry.get().strip()
                
                if not title or not description:
                    messagebox.showwarning("Warning", "Please fill in all required fields")
                    return
                
                success, message = self.auth.update_report_details(
                    report_id, title, description, category_var.get(), priority_var.get()
                )
                
                if success:
                    messagebox.showinfo("Success", message)
                    dialog.destroy()
                    self.show_report_management()
                else:
                    messagebox.showerror("Error", message)
            
            # Buttons frame
            button_frame = tk.Frame(form_frame, bg=self.COLORS['white'])
            button_frame.pack(fill='x', pady=10)
            
            tk.Button(button_frame, text="Save Changes", font=self.FONTS['body'],
                     bg=self.COLORS['success'], fg='white', relief='raised',
                     command=save_changes).pack(side='left', padx=5)
            
            tk.Button(button_frame, text="Cancel", font=self.FONTS['body'],
                     bg=self.COLORS['secondary'], fg='white', relief='raised',
                     command=dialog.destroy).pack(side='left', padx=5)
        else:
            messagebox.showerror("Error", report)

    def update_report_status_dialog(self, tree):
        """Update report status dialog"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a report first")
            return
        
        report_id = tree.item(selected[0])['values'][0]
        
        # Create status update dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Update Report Status")
        dialog.geometry("400x300")
        dialog.configure(bg=self.COLORS['white'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Update Report Status", 
                font=self.FONTS['header'], bg=self.COLORS['white']).pack(pady=10)
        
        form_frame = tk.Frame(dialog, bg=self.COLORS['white'])
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Status
        tk.Label(form_frame, text="Status *", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        status_var = tk.StringVar(value="Pending")
        status_combo = ttk.Combobox(form_frame, textvariable=status_var,
                                   values=["Pending", "In Progress", "Resolved", "Rejected"],
                                   state="readonly", width=40)
        status_combo.pack(fill='x', pady=5)
        
        # Feedback
        tk.Label(form_frame, text="Feedback/Notes", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        feedback_text = scrolledtext.ScrolledText(form_frame, width=40, height=6, font=self.FONTS['body'])
        feedback_text.pack(fill='both', expand=True, pady=5)
        
        def update_status():
            feedback = feedback_text.get('1.0', tk.END).strip()
            
            success, message = self.auth.update_report_status(
                report_id, status_var.get(), None, feedback
            )
            
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
                self.show_report_management()
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(form_frame, text="Update Status", font=self.FONTS['body'],
                 bg=self.COLORS['success'], fg='white', relief='raised',
                 command=update_status).pack(pady=10)

    def assign_report_dialog(self, tree):
        """Assign report to officer dialog"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a report first")
            return
        
        report_id = tree.item(selected[0])['values'][0]
        
        # Get available officers
        success, users = self.auth.get_all_users(self.user_data['id'])
        officers = [user for user in users if user['role'] == 'Government Officer' and user['status'] == 'Active'] if success else []
        
        if not officers:
            messagebox.showwarning("Warning", "No active government officers available")
            return
        
        # Create assignment dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Assign Report to Officer")
        dialog.geometry("400x200")
        dialog.configure(bg=self.COLORS['white'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Assign Report to Officer", 
                font=self.FONTS['header'], bg=self.COLORS['white']).pack(pady=10)
        
        form_frame = tk.Frame(dialog, bg=self.COLORS['white'])
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Officer selection
        tk.Label(form_frame, text="Select Officer *", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        
        officer_var = tk.StringVar()
        officer_combo = ttk.Combobox(form_frame, textvariable=officer_var, width=40)
        officer_combo['values'] = [f"{officer['full_name']} ({officer['department']})" for officer in officers]
        officer_combo.pack(fill='x', pady=5)
        
        def assign_officer():
            selected_officer = officer_var.get()
            if not selected_officer:
                messagebox.showwarning("Warning", "Please select an officer")
                return
            
            # Extract officer ID from selection
            officer_name = selected_officer.split(' (')[0]
            officer = next((o for o in officers if o['full_name'] == officer_name), None)
            
            if officer:
                success, message = self.auth.assign_report_to_officer(report_id, officer['id'])
                
                if success:
                    messagebox.showinfo("Success", message)
                    dialog.destroy()
                    self.show_report_management()
                else:
                    messagebox.showerror("Error", message)
            else:
                messagebox.showerror("Error", "Selected officer not found")
        
        tk.Button(form_frame, text="Assign Officer", font=self.FONTS['body'],
                 bg=self.COLORS['success'], fg='white', relief='raised',
                 command=assign_officer).pack(pady=10)

    def delete_report(self, tree):
        """Delete selected report"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a report first")
            return
        
        report_id = tree.item(selected[0])['values'][0]
        report_title = tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete report:\n'{report_title}'?"):
            success, message = self.auth.delete_report(report_id)
            
            if success:
                messagebox.showinfo("Success", message)
                self.show_report_management()
            else:
                messagebox.showerror("Error", message)

    def create_stat_card(self, parent, title, value, color):
        """Create a statistics card"""
        card = tk.Frame(parent, bg=color, relief='raised', bd=1, width=150, height=80)
        card.pack_propagate(False)
        
        tk.Label(card, text=title, font=self.FONTS['small'], bg=color, fg='white').pack(pady=5)
        tk.Label(card, text=str(value), font=('Arial', 18, 'bold'), bg=color, fg='white').pack(pady=5)
        
        return card

    def show_user_management(self):
        """Show user management interface"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="User Management", font=self.FONTS['title'], 
                bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        # Get all users
        success, users = self.auth.get_all_users(self.user_data['id'])
        
        if success:
            # Create treeview for users
            tree_frame = tk.Frame(container, bg=self.COLORS['white'])
            tree_frame.pack(fill='both', expand=True, pady=10)
            
            # Treeview scrollbar
            scrollbar = ttk.Scrollbar(tree_frame)
            scrollbar.pack(side='right', fill='y')
            
            # Treeview
            tree = ttk.Treeview(tree_frame, columns=('ID', 'Name', 'Username', 'Email', 'Phone', 'Role', 'Department', 'Status'), 
                               show='headings', yscrollcommand=scrollbar.set)
            
            # Define headings
            tree.heading('ID', text='ID')
            tree.heading('Name', text='Full Name')
            tree.heading('Username', text='Username')
            tree.heading('Email', text='Email')
            tree.heading('Phone', text='Phone')
            tree.heading('Role', text='Role')
            tree.heading('Department', text='Department')
            tree.heading('Status', text='Status')
            
            # Configure columns
            tree.column('ID', width=50)
            tree.column('Name', width=150)
            tree.column('Username', width=100)
            tree.column('Email', width=150)
            tree.column('Phone', width=100)
            tree.column('Role', width=120)
            tree.column('Department', width=120)
            tree.column('Status', width=80)
            
            # Add users to treeview
            for user in users:
                tree.insert('', 'end', values=(
                    user['id'], user['full_name'], user['username'], 
                    user['email'] or 'N/A', user['phone'], user['role'], 
                    user['department'] or 'N/A', user['status']
                ))
            
            tree.pack(side='left', fill='both', expand=True)
            scrollbar.config(command=tree.yview)
            
            # Action buttons frame
            action_frame = tk.Frame(container, bg=self.COLORS['white'])
            action_frame.pack(fill='x', pady=10)
            
            tk.Button(action_frame, text="Refresh", font=self.FONTS['body'],
                     bg=self.COLORS['secondary'], fg='white', relief='raised',
                     command=self.show_user_management).pack(side='left', padx=5)
            
            tk.Button(action_frame, text="Activate User", font=self.FONTS['body'],
                     bg=self.COLORS['success'], fg='white', relief='raised',
                     command=lambda: self.update_user_status(tree, 'Active')).pack(side='left', padx=5)
            
            tk.Button(action_frame, text="Suspend User", font=self.FONTS['body'],
                     bg=self.COLORS['warning'], fg='white', relief='raised',
                     command=lambda: self.update_user_status(tree, 'Suspended')).pack(side='left', padx=5)
            
            tk.Button(action_frame, text="Delete User", font=self.FONTS['body'],
                     bg=self.COLORS['danger'], fg='white', relief='raised',
                     command=lambda: self.delete_user(tree)).pack(side='left', padx=5)
            
            # Role update
            role_frame = tk.Frame(action_frame, bg=self.COLORS['white'])
            role_frame.pack(side='left', padx=20)
            
            tk.Label(role_frame, text="Change Role:", font=self.FONTS['body'], 
                    bg=self.COLORS['white']).pack(side='left')
            
            role_var = tk.StringVar(value="Citizen")
            role_combo = ttk.Combobox(role_frame, textvariable=role_var, 
                                     values=["Citizen", "Government Officer", "Administrator"],
                                     state="readonly", width=15)
            role_combo.pack(side='left', padx=5)
            
            tk.Button(role_frame, text="Update Role", font=self.FONTS['body'],
                     bg=self.COLORS['secondary'], fg='white', relief='raised',
                     command=lambda: self.update_user_role(tree, role_var.get())).pack(side='left', padx=5)

    def update_user_status(self, tree, status):
        """Update selected user status"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user first")
            return
        
        user_id = tree.item(selected[0])['values'][0]
        success, message = self.auth.update_user_status(user_id, status)
        
        if success:
            messagebox.showinfo("Success", message)
            self.show_user_management()
        else:
            messagebox.showerror("Error", message)

    def delete_user(self, tree):
        """Delete selected user"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user first")
            return
        
        user_id = tree.item(selected[0])['values'][0]
        user_name = tree.item(selected[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user: {user_name}?"):
            success, message = self.auth.delete_user(user_id)
            
            if success:
                messagebox.showinfo("Success", message)
                self.show_user_management()
            else:
                messagebox.showerror("Error", message)

    def update_user_role(self, tree, new_role):
        """Update selected user role"""
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a user first")
            return
        
        user_id = tree.item(selected[0])['values'][0]
        success, message = self.auth.update_user_role(user_id, new_role)
        
        if success:
            messagebox.showinfo("Success", message)
            self.show_user_management()
        else:
            messagebox.showerror("Error", message)

    # Citizen Features
    def show_citizen_dashboard(self):
        """Show citizen dashboard"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="Citizen Dashboard", font=self.FONTS['title'], 
                bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        # Get user stats
        success, applications = self.auth.get_user_applications(self.user_data['id'])
        report_success, reports = self.auth.get_user_reports(self.user_data['id'])
        
        # Welcome message with stats
        welcome_text = f"Welcome, {self.user_data['name']}!\n\n"
        welcome_text += f"Your Statistics:\n"
        welcome_text += f"• Applications Submitted: {len(applications) if success else 0}\n"
        welcome_text += f"• Reports Submitted: {len(reports) if report_success else 0}\n"
        welcome_text += f"• Pending Items: {len([app for app in applications if app['status'] == 'Pending']) if success else 0}"
        
        tk.Label(container, text=welcome_text, font=self.FONTS['body'], 
                bg=self.COLORS['white'], justify='left').pack(pady=20)
        
        # Quick actions
        actions_frame = tk.Frame(container, bg=self.COLORS['white'])
        actions_frame.pack(pady=20)
        
        tk.Button(actions_frame, text="View Available Services", font=self.FONTS['body'],
                 bg=self.COLORS['secondary'], fg='white', relief='raised', width=20,
                 command=lambda: self.handle_navigation('Available Services')).pack(pady=5)
        
        tk.Button(actions_frame, text="Submit Report/Complaint", font=self.FONTS['body'],
                 bg=self.COLORS['warning'], fg='white', relief='raised', width=20,
                 command=lambda: self.handle_navigation('Submit Report')).pack(pady=5)
        
        tk.Button(actions_frame, text="My Applications", font=self.FONTS['body'],
                 bg=self.COLORS['success'], fg='white', relief='raised', width=20,
                 command=lambda: self.handle_navigation('My Applications')).pack(pady=5)
        
        tk.Button(actions_frame, text="My Reports", font=self.FONTS['body'],
                 bg=self.COLORS['danger'], fg='white', relief='raised', width=20,
                 command=lambda: self.handle_navigation('My Reports')).pack(pady=5)

    def show_available_services(self):
        """Show available services for citizens"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="Available Services", font=self.FONTS['title'], 
                bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        success, services = self.auth.get_all_services()
        
        if success and services:
            for service in services:
                service_frame = tk.Frame(container, bg=self.COLORS['light_bg'], relief='raised', bd=1)
                service_frame.pack(fill='x', pady=5, padx=10)
                
                tk.Label(service_frame, text=service['name'], font=self.FONTS['subheader'], 
                        bg=self.COLORS['light_bg']).pack(anchor='w', padx=10, pady=5)
                
                tk.Label(service_frame, text=service['description'], font=self.FONTS['body'], 
                        bg=self.COLORS['light_bg'], wraplength=800, justify='left').pack(anchor='w', padx=10, pady=2)
                
                info_text = f"Category: {service['category']}"
                if service.get('department'):
                    info_text += f" | Department: {service['department']}"
                if service.get('processing_time'):
                    info_text += f" | Processing Time: {service['processing_time']}"
                if service.get('fee') and service['fee'] > 0:
                    info_text += f" | Fee: ৳{service['fee']}"
                
                tk.Label(service_frame, text=info_text, font=self.FONTS['small'], 
                        bg=self.COLORS['light_bg']).pack(anchor='w', padx=10, pady=2)
                
                tk.Button(service_frame, text="Apply Now", font=self.FONTS['body'],
                         bg=self.COLORS['success'], fg='white', relief='raised',
                         command=lambda s=service: self.apply_for_service(s)).pack(anchor='e', padx=10, pady=5)
        else:
            tk.Label(container, text="No services available at the moment.", 
                    font=self.FONTS['body'], bg=self.COLORS['white']).pack(pady=20)

    def apply_for_service(self, service):
        """Apply for a service"""
        # Create application dialog
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Apply for {service['name']}")
        dialog.geometry("500x400")
        dialog.configure(bg=self.COLORS['white'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text=f"Application for {service['name']}", 
                font=self.FONTS['header'], bg=self.COLORS['white']).pack(pady=10)
        
        # Application form
        form_frame = tk.Frame(dialog, bg=self.COLORS['white'])
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        tk.Label(form_frame, text="Additional Information:", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w')
        
        info_text = scrolledtext.ScrolledText(form_frame, width=50, height=10, font=self.FONTS['body'])
        info_text.pack(fill='both', expand=True, pady=5)
        
        def submit_application():
            additional_info = info_text.get('1.0', tk.END).strip()
            
            application_data = {
                'user_id': self.user_data['id'],
                'service_id': service['id'],
                'application_data': json.dumps({
                    'additional_info': additional_info,
                    'applied_date': datetime.now().isoformat(),
                    'service_name': service['name']
                })
            }
            
            success, message = self.auth.create_application(application_data)
            
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(form_frame, text="Submit Application", font=self.FONTS['body'],
                 bg=self.COLORS['success'], fg='white', relief='raised',
                 command=submit_application).pack(pady=10)

    def show_my_applications(self):
        """Show citizen's applications"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="My Applications", font=self.FONTS['title'], 
                bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        success, applications = self.auth.get_user_applications(self.user_data['id'])
        
        if success and applications:
            for app in applications:
                status_color = self.COLORS['warning']  # Default for pending
                if app['status'] == 'Approved':
                    status_color = self.COLORS['success']
                elif app['status'] == 'Rejected':
                    status_color = self.COLORS['danger']
                elif app['status'] == 'In Review':
                    status_color = self.COLORS['secondary']
                
                app_frame = tk.Frame(container, bg=self.COLORS['light_bg'], relief='raised', bd=1)
                app_frame.pack(fill='x', pady=5, padx=10)
                
                # Application header
                header_frame = tk.Frame(app_frame, bg=self.COLORS['light_bg'])
                header_frame.pack(fill='x', padx=10, pady=5)
                
                tk.Label(header_frame, text=app['service_name'], font=self.FONTS['subheader'], 
                        bg=self.COLORS['light_bg']).pack(side='left')
                
                tk.Label(header_frame, text=app['status'], font=self.FONTS['body'], 
                        bg=status_color, fg='white', relief='raised', bd=1).pack(side='right', padx=5)
                
                # Application details
                details_frame = tk.Frame(app_frame, bg=self.COLORS['light_bg'])
                details_frame.pack(fill='x', padx=10, pady=2)
                
                applied_date = app['applied_date'].strftime('%Y-%m-%d %H:%M') if app['applied_date'] else 'N/A'
                tk.Label(details_frame, text=f"Applied: {applied_date}", font=self.FONTS['small'], 
                        bg=self.COLORS['light_bg']).pack(anchor='w')
                
                if app['processed_date']:
                    processed_date = app['processed_date'].strftime('%Y-%m-%d %H:%M')
                    tk.Label(details_frame, text=f"Processed: {processed_date}", font=self.FONTS['small'], 
                            bg=self.COLORS['light_bg']).pack(anchor='w')
                
                if app['notes']:
                    tk.Label(details_frame, text=f"Notes: {app['notes']}", font=self.FONTS['small'], 
                            bg=self.COLORS['light_bg'], wraplength=600, justify='left').pack(anchor='w')
        else:
            tk.Label(container, text="You haven't submitted any applications yet.", 
                    font=self.FONTS['body'], bg=self.COLORS['white']).pack(pady=20)

    def show_submit_report(self):
        """Show report submission form"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="Submit Report/Complaint", font=self.FONTS['title'], 
                bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        form_frame = tk.Frame(container, bg=self.COLORS['white'])
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Report title
        tk.Label(form_frame, text="Title *", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        title_entry = tk.Entry(form_frame, width=50, font=self.FONTS['body'])
        title_entry.pack(fill='x', pady=5)
        
        # Category
        tk.Label(form_frame, text="Category *", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        category_var = tk.StringVar(value="Infrastructure")
        category_combo = ttk.Combobox(form_frame, textvariable=category_var,
                                     values=["Infrastructure", "Health", "Education", "Utility", "Environment", "Other"],
                                     state="readonly", width=50)
        category_combo.pack(fill='x', pady=5)
        
        # Priority
        tk.Label(form_frame, text="Priority", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(form_frame, textvariable=priority_var,
                                     values=["Low", "Medium", "High", "Emergency"],
                                     state="readonly", width=50)
        priority_combo.pack(fill='x', pady=5)
        
        # Location
        tk.Label(form_frame, text="Location", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        location_entry = tk.Entry(form_frame, width=50, font=self.FONTS['body'])
        location_entry.pack(fill='x', pady=5)
        
        # Description
        tk.Label(form_frame, text="Description *", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        desc_text = scrolledtext.ScrolledText(form_frame, width=50, height=8, font=self.FONTS['body'])
        desc_text.pack(fill='both', expand=True, pady=5)
        
        def submit_report():
            title = title_entry.get().strip()
            description = desc_text.get('1.0', tk.END).strip()
            location = location_entry.get().strip()
            
            if not title or not description:
                messagebox.showwarning("Warning", "Please fill in all required fields")
                return
            
            report_data = {
                'user_id': self.user_data['id'],
                'title': title,
                'description': description,
                'category': category_var.get(),
                'location': location,
                'priority': priority_var.get()
            }
            
            success, message = self.auth.submit_citizen_report(report_data)
            
            if success:
                messagebox.showinfo("Success", message)
                # Clear form
                title_entry.delete(0, tk.END)
                desc_text.delete('1.0', tk.END)
                location_entry.delete(0, tk.END)
                category_var.set("Infrastructure")
                priority_var.set("Medium")
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(form_frame, text="Submit Report", font=self.FONTS['body'],
                 bg=self.COLORS['success'], fg='white', relief='raised',
                 command=submit_report).pack(pady=10)

    def show_my_reports(self):
        """Show citizen's reports"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="My Reports", font=self.FONTS['title'], 
                bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        success, reports = self.auth.get_user_reports(self.user_data['id'])
        
        if success and reports:
            for report in reports:
                status_color = self.COLORS['warning']  # Default for pending
                if report['status'] == 'Resolved':
                    status_color = self.COLORS['success']
                elif report['status'] == 'Rejected':
                    status_color = self.COLORS['danger']
                elif report['status'] == 'In Progress':
                    status_color = self.COLORS['secondary']
                
                priority_color = self.COLORS['text_light']
                if report['priority'] == 'High':
                    priority_color = self.COLORS['warning']
                elif report['priority'] == 'Emergency':
                    priority_color = self.COLORS['danger']
                
                report_frame = tk.Frame(container, bg=self.COLORS['light_bg'], relief='raised', bd=1)
                report_frame.pack(fill='x', pady=5, padx=10)
                
                # Report header
                header_frame = tk.Frame(report_frame, bg=self.COLORS['light_bg'])
                header_frame.pack(fill='x', padx=10, pady=5)
                
                tk.Label(header_frame, text=report['title'], font=self.FONTS['subheader'], 
                        bg=self.COLORS['light_bg']).pack(side='left')
                
                status_frame = tk.Frame(header_frame, bg=self.COLORS['light_bg'])
                status_frame.pack(side='right')
                
                tk.Label(status_frame, text=report['priority'], font=self.FONTS['small'], 
                        bg=priority_color, fg='white', relief='raised', bd=1).pack(side='left', padx=2)
                tk.Label(status_frame, text=report['status'], font=self.FONTS['small'], 
                        bg=status_color, fg='white', relief='raised', bd=1).pack(side='left', padx=2)
                
                # Report details
                details_frame = tk.Frame(report_frame, bg=self.COLORS['light_bg'])
                details_frame.pack(fill='x', padx=10, pady=2)
                
                created_date = report['created_at'].strftime('%Y-%m-%d %H:%M') if report['created_at'] else 'N/A'
                tk.Label(details_frame, text=f"Category: {report['category']} | Created: {created_date}", 
                        font=self.FONTS['small'], bg=self.COLORS['light_bg']).pack(anchor='w')
                
                if report['location']:
                    tk.Label(details_frame, text=f"Location: {report['location']}", 
                            font=self.FONTS['small'], bg=self.COLORS['light_bg']).pack(anchor='w')
                
                tk.Label(details_frame, text=report['description'], font=self.FONTS['small'], 
                        bg=self.COLORS['light_bg'], wraplength=800, justify='left').pack(anchor='w')
                
                if report['assigned_officer']:
                    tk.Label(details_frame, text=f"Assigned Officer: {report['assigned_officer']}", 
                            font=self.FONTS['small'], bg=self.COLORS['light_bg']).pack(anchor='w')
                
                if report['resolved_at']:
                    resolved_date = report['resolved_at'].strftime('%Y-%m-%d %H:%M')
                    tk.Label(details_frame, text=f"Resolved: {resolved_date}", 
                            font=self.FONTS['small'], bg=self.COLORS['light_bg']).pack(anchor='w')
        else:
            tk.Label(container, text="You haven't submitted any reports yet.", 
                    font=self.FONTS['body'], bg=self.COLORS['white']).pack(pady=20)

    # Officer Features
    def show_officer_dashboard(self):
        """Show government officer dashboard"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="Government Officer Dashboard", font=self.FONTS['title'], 
                bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        # Get department reports
        success, reports = self.auth.get_department_reports(self.user_data['department'])
        report_success, report_stats = self.auth.get_report_stats()
        
        welcome_text = f"Welcome, Officer {self.user_data['name']}!\n"
        welcome_text += f"Department: {self.user_data['department']}\n\n"
        
        if report_success:
            welcome_text += f"Department Statistics:\n"
            welcome_text += f"• Total Reports: {report_stats['total_reports']}\n"
            welcome_text += f"• Pending Reports: {len([r for r in reports if r['status'] == 'Pending']) if success else 0}\n"
            welcome_text += f"• Reports In Progress: {len([r for r in reports if r['status'] == 'In Progress']) if success else 0}"
        
        tk.Label(container, text=welcome_text, font=self.FONTS['body'], 
                bg=self.COLORS['white'], justify='left').pack(pady=20)
        
        # Quick actions
        actions_frame = tk.Frame(container, bg=self.COLORS['white'])
        actions_frame.pack(pady=20)
        
        tk.Button(actions_frame, text="Department Reports", font=self.FONTS['body'],
                 bg=self.COLORS['secondary'], fg='white', relief='raised', width=20,
                 command=lambda: self.handle_navigation('Department Reports')).pack(pady=5)
        
        tk.Button(actions_frame, text="View Applications", font=self.FONTS['body'],
                 bg=self.COLORS['success'], fg='white', relief='raised', width=20,
                 command=lambda: self.handle_navigation('Applications')).pack(pady=5)

    def show_department_reports(self):
        """Show department-specific reports"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text=f"Department Reports - {self.user_data['department']}", 
                font=self.FONTS['title'], bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        success, reports = self.auth.get_department_reports(self.user_data['department'])
        
        if success and reports:
            for report in reports:
                status_color = self.COLORS['warning']
                if report['status'] == 'Resolved':
                    status_color = self.COLORS['success']
                elif report['status'] == 'Rejected':
                    status_color = self.COLORS['danger']
                elif report['status'] == 'In Progress':
                    status_color = self.COLORS['secondary']
                
                priority_color = self.COLORS['text_light']
                if report['priority'] == 'High':
                    priority_color = self.COLORS['warning']
                elif report['priority'] == 'Emergency':
                    priority_color = self.COLORS['danger']
                
                report_frame = tk.Frame(container, bg=self.COLORS['light_bg'], relief='raised', bd=1)
                report_frame.pack(fill='x', pady=5, padx=10)
                
                # Report header
                header_frame = tk.Frame(report_frame, bg=self.COLORS['light_bg'])
                header_frame.pack(fill='x', padx=10, pady=5)
                
                tk.Label(header_frame, text=f"{report['title']} - {report['reporter_name']}", 
                        font=self.FONTS['subheader'], bg=self.COLORS['light_bg']).pack(side='left')
                
                status_frame = tk.Frame(header_frame, bg=self.COLORS['light_bg'])
                status_frame.pack(side='right')
                
                tk.Label(status_frame, text=report['priority'], font=self.FONTS['small'], 
                        bg=priority_color, fg='white', relief='raised', bd=1).pack(side='left', padx=2)
                tk.Label(status_frame, text=report['status'], font=self.FONTS['small'], 
                        bg=status_color, fg='white', relief='raised', bd=1).pack(side='left', padx=2)
                
                # Report details and actions
                details_frame = tk.Frame(report_frame, bg=self.COLORS['light_bg'])
                details_frame.pack(fill='x', padx=10, pady=5)
                
                created_date = report['created_at'].strftime('%Y-%m-%d %H:%M') if report['created_at'] else 'N/A'
                tk.Label(details_frame, text=f"Reporter: {report['reporter_name']} | Created: {created_date}", 
                        font=self.FONTS['small'], bg=self.COLORS['light_bg']).pack(anchor='w')
                
                if report['location']:
                    tk.Label(details_frame, text=f"Location: {report['location']}", 
                            font=self.FONTS['small'], bg=self.COLORS['light_bg']).pack(anchor='w')
                
                tk.Label(details_frame, text=report['description'], font=self.FONTS['small'], 
                        bg=self.COLORS['light_bg'], wraplength=800, justify='left').pack(anchor='w')
                
                # Action buttons for pending reports
                if report['status'] == 'Pending':
                    action_frame = tk.Frame(details_frame, bg=self.COLORS['light_bg'])
                    action_frame.pack(fill='x', pady=5)
                    
                    tk.Button(action_frame, text="Take Action", font=self.FONTS['small'],
                             bg=self.COLORS['success'], fg='white', relief='raised',
                             command=lambda r=report: self.update_report_status(r['id'], 'In Progress')).pack(side='left', padx=2)
        else:
            tk.Label(container, text="No reports found for your department.", 
                    font=self.FONTS['body'], bg=self.COLORS['white']).pack(pady=20)

    def update_report_status(self, report_id, status):
        """Update report status"""
        success, message = self.auth.update_report_status(report_id, status, self.user_data['id'])
        
        if success:
            messagebox.showinfo("Success", message)
            if self.user_data['role'] == 'Government Officer':
                self.show_department_reports()
            else:
                self.show_applications()
        else:
            messagebox.showerror("Error", message)

    def show_applications(self):
        """Show applications for processing (officer/admin)"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="All Applications", font=self.FONTS['title'], 
                bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        success, applications = self.auth.get_all_applications()
        
        if success and applications:
            for app in applications:
                status_color = self.COLORS['warning']
                if app['status'] == 'Approved':
                    status_color = self.COLORS['success']
                elif app['status'] == 'Rejected':
                    status_color = self.COLORS['danger']
                elif app['status'] == 'In Review':
                    status_color = self.COLORS['secondary']
                
                app_frame = tk.Frame(container, bg=self.COLORS['light_bg'], relief='raised', bd=1)
                app_frame.pack(fill='x', pady=5, padx=10)
                
                # Application header
                header_frame = tk.Frame(app_frame, bg=self.COLORS['light_bg'])
                header_frame.pack(fill='x', padx=10, pady=5)
                
                tk.Label(header_frame, text=f"{app['service_name']} - {app['applicant_name']}", 
                        font=self.FONTS['subheader'], bg=self.COLORS['light_bg']).pack(side='left')
                
                tk.Label(header_frame, text=app['status'], font=self.FONTS['body'], 
                        bg=status_color, fg='white', relief='raised', bd=1).pack(side='right', padx=5)
                
                # Application details and actions
                details_frame = tk.Frame(app_frame, bg=self.COLORS['light_bg'])
                details_frame.pack(fill='x', padx=10, pady=5)
                
                applied_date = app['applied_date'].strftime('%Y-%m-%d %H:%M') if app['applied_date'] else 'N/A'
                tk.Label(details_frame, text=f"Applicant: {app['applicant_name']} ({app['applicant_username']})", 
                        font=self.FONTS['small'], bg=self.COLORS['light_bg']).pack(anchor='w')
                tk.Label(details_frame, text=f"Applied: {applied_date}", 
                        font=self.FONTS['small'], bg=self.COLORS['light_bg']).pack(anchor='w')
                
                # Action buttons for pending applications
                if app['status'] == 'Pending' and self.user_data['role'] in ['Government Officer', 'Administrator']:
                    action_frame = tk.Frame(details_frame, bg=self.COLORS['light_bg'])
                    action_frame.pack(fill='x', pady=5)
                    
                    tk.Button(action_frame, text="Approve", font=self.FONTS['small'],
                             bg=self.COLORS['success'], fg='white', relief='raised',
                             command=lambda a=app: self.update_app_status(a['id'], 'Approved')).pack(side='left', padx=2)
                    
                    tk.Button(action_frame, text="Reject", font=self.FONTS['small'],
                             bg=self.COLORS['danger'], fg='white', relief='raised',
                             command=lambda a=app: self.update_app_status(a['id'], 'Rejected')).pack(side='left', padx=2)
                    
                    tk.Button(action_frame, text="Mark In Review", font=self.FONTS['small'],
                             bg=self.COLORS['secondary'], fg='white', relief='raised',
                             command=lambda a=app: self.update_app_status(a['id'], 'In Review')).pack(side='left', padx=2)
        else:
            tk.Label(container, text="No applications found.", 
                    font=self.FONTS['body'], bg=self.COLORS['white']).pack(pady=20)

    def update_app_status(self, app_id, status):
        """Update application status"""
        success, message = self.auth.update_application_status(app_id, status, self.user_data['id'])
        
        if success:
            messagebox.showinfo("Success", message)
            self.show_applications()
        else:
            messagebox.showerror("Error", message)

    def show_services(self):
        """Show services management"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="Services Management", font=self.FONTS['title'], 
                bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        # Add service button for admin/officer
        if self.user_data['role'] in ['Administrator', 'Government Officer']:
            tk.Button(container, text="Add New Service", font=self.FONTS['body'],
                     bg=self.COLORS['success'], fg='white', relief='raised',
                     command=self.show_add_service_dialog).pack(anchor='e', pady=10)
        
        success, services = self.auth.get_all_services()
        
        if success and services:
            for service in services:
                service_frame = tk.Frame(container, bg=self.COLORS['light_bg'], relief='raised', bd=1)
                service_frame.pack(fill='x', pady=5, padx=10)
                
                tk.Label(service_frame, text=service['name'], font=self.FONTS['subheader'], 
                        bg=self.COLORS['light_bg']).pack(anchor='w', padx=10, pady=5)
                
                tk.Label(service_frame, text=service['description'], font=self.FONTS['body'], 
                        bg=self.COLORS['light_bg'], wraplength=800, justify='left').pack(anchor='w', padx=10, pady=2)
                
                info_text = f"Category: {service['category']}"
                if service.get('department'):
                    info_text += f" | Department: {service['department']}"
                if service.get('processing_time'):
                    info_text += f" | Processing Time: {service['processing_time']}"
                if service.get('fee') and service['fee'] > 0:
                    info_text += f" | Fee: ৳{service['fee']}"
                info_text += f" | Created by: {service['created_by_name']}"
                
                tk.Label(service_frame, text=info_text, 
                        font=self.FONTS['small'], bg=self.COLORS['light_bg']).pack(anchor='w', padx=10, pady=2)
        else:
            tk.Label(container, text="No services available.", 
                    font=self.FONTS['body'], bg=self.COLORS['white']).pack(pady=20)

    def show_add_service_dialog(self):
        """Show dialog to add new service"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Service")
        dialog.geometry("500x400")
        dialog.configure(bg=self.COLORS['white'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        tk.Label(dialog, text="Add New Service", font=self.FONTS['header'], 
                bg=self.COLORS['white']).pack(pady=10)
        
        form_frame = tk.Frame(dialog, bg=self.COLORS['white'])
        form_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Service name
        tk.Label(form_frame, text="Service Name:", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        name_entry = tk.Entry(form_frame, width=50, font=self.FONTS['body'])
        name_entry.pack(fill='x', pady=5)
        
        # Category
        tk.Label(form_frame, text="Category:", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        category_entry = tk.Entry(form_frame, width=50, font=self.FONTS['body'])
        category_entry.pack(fill='x', pady=5)
        
        # Department
        tk.Label(form_frame, text="Department:", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        department_var = tk.StringVar(value=self.user_data.get('department', ''))
        department_combo = ttk.Combobox(form_frame, textvariable=department_var,
                                       values=["City Corporation", "Health Department", "Water Supply", "Electricity", "Education", "Environment"],
                                       state="readonly", width=50)
        department_combo.pack(fill='x', pady=5)
        
        # Processing time
        tk.Label(form_frame, text="Processing Time:", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        processing_entry = tk.Entry(form_frame, width=50, font=self.FONTS['body'])
        processing_entry.pack(fill='x', pady=5)
        
        # Fee
        tk.Label(form_frame, text="Fee (৳):", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        fee_entry = tk.Entry(form_frame, width=50, font=self.FONTS['body'])
        fee_entry.pack(fill='x', pady=5)
        
        # Description
        tk.Label(form_frame, text="Description:", font=self.FONTS['body'], 
                bg=self.COLORS['white']).pack(anchor='w', pady=5)
        desc_text = scrolledtext.ScrolledText(form_frame, width=50, height=8, font=self.FONTS['body'])
        desc_text.pack(fill='both', expand=True, pady=5)
        
        def add_service():
            name = name_entry.get().strip()
            category = category_entry.get().strip()
            description = desc_text.get('1.0', tk.END).strip()
            department = department_var.get()
            processing_time = processing_entry.get().strip()
            fee_text = fee_entry.get().strip()
            
            if not name or not category:
                messagebox.showwarning("Warning", "Please fill in all required fields")
                return
            
            try:
                fee = float(fee_text) if fee_text else 0.00
            except ValueError:
                messagebox.showwarning("Warning", "Please enter a valid fee amount")
                return
            
            service_data = {
                'name': name,
                'description': description,
                'category': category,
                'department': department,
                'processing_time': processing_time,
                'fee': fee,
                'created_by': self.user_data['id']
            }
            
            success, message = self.auth.create_service(service_data)
            
            if success:
                messagebox.showinfo("Success", message)
                dialog.destroy()
                self.show_services()
            else:
                messagebox.showerror("Error", message)
        
        tk.Button(form_frame, text="Create Service", font=self.FONTS['body'],
                 bg=self.COLORS['success'], fg='white', relief='raised',
                 command=add_service).pack(pady=10)

    def show_profile(self):
        """Show user profile"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="My Profile", font=self.FONTS['title'], 
                bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        # Profile information
        profile_frame = tk.Frame(container, bg=self.COLORS['light_bg'], relief='raised', bd=1)
        profile_frame.pack(fill='x', pady=10, padx=10)
        
        info_text = f"""
        Full Name: {self.user_data['name']}
        Username: {self.user_data['username']}
        Email: {self.user_data['email'] or 'Not provided'}
        Role: {self.user_data['role']}
        Status: {self.user_data['status']}
        """
        
        if self.user_data.get('department'):
            info_text += f"Department: {self.user_data['department']}\n"
        
        info_text += """
        
        This is your profile information. 
        Contact administrator to update your personal details.
        """
        
        tk.Label(profile_frame, text=info_text, font=self.FONTS['body'], 
                bg=self.COLORS['light_bg'], justify='left').pack(padx=20, pady=20)

    def show_system_reports(self):
        """Show system reports (admin only)"""
        container = tk.Frame(self.content_frame, bg=self.COLORS['white'])
        container.pack(fill='both', expand=True, padx=20, pady=20)
        
        tk.Label(container, text="System Reports", font=self.FONTS['title'], 
                bg=self.COLORS['white'], fg=self.COLORS['primary']).pack(pady=10)
        
        # Get statistics
        success, stats = self.auth.get_user_stats()
        report_success, report_stats = self.auth.get_report_stats()
        
        if success and report_success:
            report_text = f"""
            SYSTEM REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M')}
            
            User Statistics:
            • Total Users: {stats['total_users']}
            • Recent Registrations (7 days): {stats['recent_registrations']}
            
            Users by Role:
            """
            
            for role_stat in stats['users_by_role']:
                report_text += f"• {role_stat['role']}: {role_stat['count']}\n"
            
            report_text += "\nUsers by Status:\n"
            for status_stat in stats['users_by_status']:
                report_text += f"• {status_stat['status']}: {status_stat['count']}\n"
            
            report_text += f"""
            
            Report Statistics:
            • Total Reports: {report_stats['total_reports']}
            • Recent Reports (7 days): {report_stats['recent_reports']}
            
            Reports by Status:
            """
            
            for status_stat in report_stats['reports_by_status']:
                report_text += f"• {status_stat['status']}: {status_stat['count']}\n"
            
            report_text += "\nReports by Category:\n"
            for category_stat in report_stats['reports_by_category']:
                report_text += f"• {category_stat['category']}: {category_stat['count']}\n"
            
            report_frame = tk.Frame(container, bg=self.COLORS['light_bg'], relief='raised', bd=1)
            report_frame.pack(fill='both', expand=True, pady=10, padx=10)
            
            report_display = scrolledtext.ScrolledText(report_frame, width=80, height=20, font=self.FONTS['body'])
            report_display.pack(fill='both', expand=True, padx=10, pady=10)
            report_display.insert('1.0', report_text)
            report_display.config(state='disabled')
        else:
            tk.Label(container, text="Could not generate reports.", 
                    font=self.FONTS['body'], bg=self.COLORS['white']).pack(pady=20)

    def logout(self):
        """Logout and return to login screen"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.root.destroy()
            # Restart the application
            import main
            main.start_application()

# Helper function to start dashboard
def start_dashboard(user_data):
    """Start the dashboard application"""
    root = tk.Tk()
    root.eval('tk::PlaceWindow . center')
    dashboard = Dashboard(root, user_data)
    root.mainloop()