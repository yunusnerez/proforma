from fpdf import FPDF
import os

# USER: Edit this data
data = {
    "title": "Treatment Plan",
    "billed_to": "Amir_",
    "treatments": [
        {"name": "Stem Cell Derived Exosomes",
         "note": "20 billion exosomes"},
    ],
    "total": "£3000"
}

class PDF(FPDF):
    def header(self):
        self.image("template_clean.jpg", x=0, y=0, w=210, h=297)

    def add_content(self, data):
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 51, 102)
        self.set_y(50)
        self.cell(0, 10, data["title"], ln=True, align="C")

        self.set_font("Arial", "B", 11)
        self.multi_cell(0, 6, f"Tailored for:\n")
        self.set_font("Arial", "", 11)
        self.multi_cell(0, 6, data['billed_to'])

        self.set_y(95)
        self.set_font("Arial", "B", 12)
        self.set_fill_color(225, 236, 247)
        self.set_text_color(0, 51, 102)
        self.cell(180, 9, "Included Therapies", 1, 1, "C", True)

        self.set_font("Arial", "", 11)
        self.set_text_color(0)
        for i, item in enumerate(data["treatments"], 1):
    # Ana satır (kutulu)
            self.cell(180, 8, f"{i}. {item['name']}", border=1, ln=1)

    # Eğer not varsa, alt satıra italik ve gri olarak yaz (kutusuz)
            if "note" in item and item["note"]:
                self.set_font("Arial", "I", 10)
                self.set_text_color(100)
                self.cell(180, 6, f"   {item['note']}", border=0, ln=1)
                self.set_font("Arial", "", 11)
                self.set_text_color(0)

        if data["total"]:
            self.set_y(self.get_y() + 10)
            self.set_font("Arial", "B", 12)
            self.cell(0, 10, f"Total Package Price: {data['total']}", ln=True, align="R")
            self.set_font("Arial", "I", 9)
            self.set_text_color(80)
            self.cell(0, 6, "Payment is done in cash", ln=True, align="R")
            self.set_text_color(0)
        self.set_font("Arial", "B", 10)
        self.cell(0, 6, "Your Medical Consultant:", ln=True, align="R")
        self.set_font("Arial", "", 10)
        self.cell(0, 6, "Yunus", ln=True, align="R")

pdf = PDF()
pdf.add_page()
pdf.add_content(data)
name = data["billed_to"].split("\\n")[0].replace(" ", "_")
file_name = f"treatment_plan_{name}.pdf"
os.makedirs("Treatment Plans", exist_ok=True)
pdf.output(f"Treatment Plans/{file_name}")
print(f"PDF created: {file_name}")
# print("PDF created: treatment_package.pdf")
