from fpdf import FPDF
import os

def get_next_invoice_number():
    file_path = "invoice_counter.txt"
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("A013000")
    with open(file_path, "r") as f:
        current = f.read().strip()
    prefix = current[:1]
    number = int(current[1:]) + 1
    new_number = f"{prefix}{number:06}"
    with open(file_path, "w") as f:
        f.write(new_number)
    return new_number

invoice_data = {
    "title": "Invoice",
    "invoice_date": "2025-09-08",
    "billed_by": "You Clinic\nTurkey",
    "billed_to": "Maryam Ilyas\nUnited Kingdom",
    "cash_note": "Payment is done in cash",
    "items": [
        {
            "item": "Autism Treatment Package",
            "quantity": 1,
            "rate": 8280.00,
            "note": ""
        }
    ],
    "currency": "£",
    "show_quantity": True,
    "show_rate": False,
    "show_amount": True,
    "deposit": 810.00
}

invoice_data["invoice_no"] = get_next_invoice_number()

class PDF(FPDF):
    def header(self):
        self.image("template_clean.jpg", x=0, y=0, w=210, h=297)

    def add_invoice(self, data):
        self.set_y(45)
        self.set_font("Arial", "B", 16)
        self.set_text_color(0, 51, 102)
        self.cell(0, 20, data["title"], ln=True, align="C")

        self.set_font("Arial", "", 11)
        self.set_text_color(0)

        self.set_y(65)
        self.set_x(10)
        self.set_draw_color(180)
        self.set_line_width(0.2)
        self.multi_cell(90, 5.5, f"Billed By:\n{data['billed_by']}", border=1)

        self.set_y(65)
        self.set_x(110)
        self.multi_cell(90, 5.5, f"Billed To:\n{data['billed_to']}", border=1)

        self.set_y(85)
        self.set_x(10)
        self.cell(90, 8, f"Invoice No: {data['invoice_no']}", ln=0)
        self.set_x(110)
        self.cell(90, 8, f"Invoice Date: {data['invoice_date']}", ln=1)

        self.set_y(102)
        self.set_x(10)
        self.set_fill_color(225, 236, 247)
        self.set_text_color(0, 51, 102)
        self.set_font("Arial", "B", 12)

        headers = ["Item"]
        if data["show_quantity"]:
            headers.append("Quantity")
        if data["show_rate"]:
            headers.append("Rate")
        if data["show_amount"]:
            headers.append("Amount")

        col_widths = [80]
        if data["show_quantity"]:
            col_widths.append(30)
        if data["show_rate"]:
            col_widths.append(40)
        if data["show_amount"]:
            col_widths.append(40)

        for header, width in zip(headers, col_widths):
            self.cell(width, 9, header, 1, 0, "C", True)
        self.ln()

        self.set_font("Arial", "", 11)
        self.set_text_color(0)
        total = 0.0
        for item in data["items"]:
            item_name = item["item"]
            quantity = item.get("quantity", 1)
            rate = item.get("rate", 0)
            amount = quantity * rate
            note = item.get("note", None)

            self.set_x(10)
            self.cell(col_widths[0], 9, item_name, 1)

            col_idx = 1
            if data["show_quantity"]:
                self.cell(col_widths[col_idx], 9, str(quantity), 1, 0, "R")
                col_idx += 1
            if data["show_rate"]:
                self.cell(col_widths[col_idx], 9, f"{data['currency']}{rate:,.2f}", 1, 0, "R")
                col_idx += 1
            if data["show_amount"]:
                self.cell(col_widths[col_idx], 9, f"{data['currency']}{amount:,.2f}", 1, 0, "R")
            total += amount
            self.ln()

            if note:
                self.set_x(12)
                self.set_font("Arial", "I", 10)
                self.set_text_color(90)
                self.multi_cell(sum(col_widths), 6, note)
                self.set_font("Arial", "", 11)
                self.set_text_color(0)

        self.set_font("Arial", "B", 12)
        self.set_x(10)
        self.cell(sum(col_widths[:-1]), 10, "Total", 1)
        self.cell(col_widths[-1], 10, f"{data['currency']}{total:,.2f}", 1, 1, "R")

        deposit = data.get("deposit", 0.0)
        remaining = total - deposit

        self.set_font("Arial", "", 11)
        self.set_x(10)
        self.cell(sum(col_widths[:-1]), 10, "Deposit", 1)
        self.cell(col_widths[-1], 10, f"{data['currency']}{deposit:,.2f}", 1, 1, "R")

        self.set_font("Arial", "B", 12)
        self.set_x(10)
        self.cell(sum(col_widths[:-1]), 10, "Remaining", 1)
        self.cell(col_widths[-1], 10, f"{data['currency']}{remaining:,.2f}", 1, 1, "R")

        if data.get("cash_note"):
            self.set_font("Arial", "I", 10)
            self.set_text_color(120)
            self.set_y(self.get_y() + 3)
            self.set_x(10)
            self.cell(0, 10, data["cash_note"], ln=True)
            self.set_text_color(0)

pdf = PDF()
pdf.add_page()
pdf.add_invoice(invoice_data)

name = invoice_data["billed_to"].split("\n")[0].replace(" ", "_")
file_name = f"invoice_{invoice_data['invoice_no']}_{name}.pdf"
pdf.output(f"invoices/{file_name}")
print(f"PDF created: {file_name}")

# Create a new file named generate_invoice.command
with open("generate_invoice.command", "w") as command_file:
    command_file.write("#!/bin/bash\n")
    command_file.write('cd "$(dirname "$0")"\n')
    command_file.write("python3 generate_invoice_notes_enabled.py\n")
    command_file.write('read -n 1 -s -r -p "Press any key to close"\n')

# Make it executable
os.chmod("generate_invoice.command", 0o755)
