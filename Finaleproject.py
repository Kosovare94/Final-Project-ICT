import customtkinter as ctk
from tkinter import filedialog, messagebox
import pandas as pd
import re

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TimetableApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("University Timetable")
        self.geometry("850x570")

        self.selected_courses = []
        self.timetable_data = []
        self.df = None

        self.create_widgets()

    def create_widgets(self):
        self.file_entry = ctk.CTkEntry(self, placeholder_text="Enter CSV file path")
        self.file_entry.place(relx=0.05, rely=0.04, relwidth=0.4)

        self.browse_button = ctk.CTkButton(self, text="Browse", command=self.browse_file, fg_color="#7851A9")
        self.browse_button.place(relx=0.05, rely=0.12, relwidth=0.15)

        self.year_combo = ctk.CTkComboBox(self, values=["", "1", "2", "3", "4", "5"])
        self.year_combo.set("Select Year")
        self.year_combo.place(relx=0.78, rely=0.04, relwidth=0.17)

        self.code_combo = ctk.CTkComboBox(self, values=["", "CHI", "CS", "EE", "UNI", "ECE", "ECON", "EECS", "ENGR", "FRE", "GER", "IE", "ISE", "LIFE", "MATH", "MGT"])
        self.code_combo.set("Select Department")
        self.code_combo.place(relx=0.78, rely=0.12, relwidth=0.17)

        self.display_button = ctk.CTkButton(self, text="Display", command=self.display_courses, fg_color="Teal")
        self.display_button.place(relx=0.42, rely=0.22, relwidth=0.15)

        DepLbl = ctk.CTkLabel(self, text="Courses:", text_color="white", fg_color="#4682B4", width=90, height=25, font=("Helvetica", 13))
        DepLbl.place(relx=0.05, rely=0.36)

        self.course_listbox = ctk.CTkTextbox(self, fg_color="#1E1E1E", text_color="#FFFFFF", border_color="#4A4A4A", border_width=1)
        self.course_listbox.place(relx=0.2, rely=0.36, relwidth=0.7, relheight=0.26)
        self.course_listbox.bind("<Double-Button-1>", self.select_course)

        WarnLbl = ctk.CTkLabel(self, text="Warnings:", text_color="white", fg_color="#FF8C00", width=90, height=25, font=("Arial", 13))
        WarnLbl.place(relx=0.05, rely=0.7)

        self.selected_text = ctk.CTkTextbox(self, fg_color="#1E1E1E", text_color="#FFFFFF", border_color="#4A4A4A", border_width=1)
        self.selected_text.place(relx=0.2, rely=0.7, relwidth=0.7, relheight=0.2)

        self.clear_button = ctk.CTkButton(self, text="Clear", command=self.clear_selection, fg_color="#B22222")
        self.clear_button.place(relx=0.3, rely=0.93, relwidth=0.15)

        self.save_button = ctk.CTkButton(self, text="Save", command=self.save_timetable, fg_color="#2E8B57")
        self.save_button.place(relx=0.55, rely=0.93, relwidth=0.15)

    def browse_file(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, path)
            try:
                raw_df = pd.read_csv(path, encoding="latin1", header=None)

                columns = ["Course Code", "Course Name", "Days", "Times"]
                fixed_data = []

                for i, row in raw_df.iterrows():
                    values = row.dropna().tolist()
                    if len(values) >= 2:
                        course_code = values[0]
                        course_name = values[1]
                        days = values[2] if len(values) > 2 else ""
                        times = " ".join(values[3:]) if len(values) > 3 else ""
                        fixed_data.append([course_code, course_name, days, times])

                self.df = pd.DataFrame(fixed_data, columns=columns)
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def display_courses(self):
        if self.df is None:
            messagebox.showwarning("Warning", "Please load a CSV file first.")
            return

        if "Year" not in self.df.columns:
            def extract_year(code):
                match = re.search(r'(\d{3})', str(code))
                if match:
                    return int(str(match.group(1))[0])
                return None
            self.df["Year"] = self.df["Course Code"].apply(extract_year)

        year_filter = self.year_combo.get()
        code_filter = self.code_combo.get().upper()

        results = []
        filtered_df = self.df.copy()
        if year_filter and year_filter.isdigit():
            filtered_df = filtered_df[filtered_df["Year"] == int(year_filter)]

        for _, row in filtered_df.iterrows():
            course_code = str(row["Course Code"]).strip()
            if not code_filter or course_code.startswith(code_filter):
                line = " ".join([str(item) for item in row if pd.notna(item)])
                results.append(line)

        self.course_listbox.delete("0.0", "end")
        for course in results:
            self.course_listbox.insert("end", course + "\n")

        self.timetable_data = results

    def extract_times(self, course_line): # HH:MM-HH:MM
        return re.findall(r"\d{2}:\d{2}-\d{2}:\d{2}", course_line)

    def select_course(self, event=None):
        selected = self.course_listbox.get("insert linestart", "insert lineend").strip()
        if selected in self.selected_courses:
            messagebox.showwarning("Warning", "You have already selected this course.")
            return

        if selected in self.timetable_data:
            if len(self.selected_courses) >= 6:
                messagebox.showwarning("Warning", "You can select at most 6 courses.")
                return

            selected_times = self.extract_times(selected)
            for course_line in self.selected_courses:
                course_times = self.extract_times(course_line)
                if any(t1 == t2 for t1 in course_times for t2 in selected_times):
                    messagebox.showwarning("Warning", "Time conflict detected. Course not added.")
                    return

        match = re.search(r'\b[A-Z]{2,}\s?\d{2,3}\b', selected)
        course_code = match.group().strip() if match else selected

        self.selected_courses.append(selected)
        self.selected_text.insert("end", course_code + "\n")

    def clear_selection(self):
        self.selected_courses = []
        self.selected_text.delete("0.0", "end")

    def save_timetable(self):
        if not self.selected_courses:
            messagebox.showwarning("Warning", "No courses to save.")
            return

        try:
            with open("timetable.csv", "w", encoding="utf-8") as f:
                for course in self.selected_courses:
                    f.write(course + "\n")
            messagebox.showinfo("Success", "Timetable saved to timetable.csv")
        except Exception as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    app = TimetableApp()
    app.mainloop()
