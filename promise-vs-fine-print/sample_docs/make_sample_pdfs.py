"""Create two short original PDFs for the Promise vs Fine Print demo."""

from pathlib import Path

from fpdf import FPDF

OUT_DIR = Path(__file__).resolve().parent


class SimplePdf(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", size=9)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def add_heading(pdf: FPDF, text: str):
    pdf.set_font("Helvetica", style="B", size=16)
    pdf.multi_cell(0, 8, text)
    pdf.ln(4)


def add_body(pdf: FPDF, text: str):
    pdf.set_font("Helvetica", size=12)
    pdf.multi_cell(0, 7, text)
    pdf.ln(3)


def write_promise():
    pdf = SimplePdf()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    add_heading(pdf, "Harbor Study Pack - Spring Offer")
    add_body(
        pdf,
        "Welcome to Harbor Learning. This one-page brochure is marketing copy only. "
        "It describes what we like to highlight in ads.",
    )
    add_body(
        pdf,
        "Promise 1: Every Student Starter pack includes a laptop. You do not pay extra "
        "for the computer. Bring it to class on day one.",
    )
    add_body(
        pdf,
        "Promise 2: 30-day money-back guarantee. If the pack is not for you, ask for a "
        "full refund within 30 days. No awkward questions.",
    )
    add_body(
        pdf,
        "Promise 3: Live Q and A every Friday at 6pm Pakistan time with a human tutor.",
    )
    pdf.add_page()
    add_heading(pdf, "Harbor Study Pack - Extra highlights")
    add_body(
        pdf,
        "Promise 4: Email support with a reply within one business day.",
    )
    add_body(
        pdf,
        "Promise 5: The printed workbook ships free inside Pakistan.",
    )
    out = OUT_DIR / "promise_brochure.pdf"
    pdf.output(out)
    print(f"Wrote {out}")


def write_fine_print():
    pdf = SimplePdf()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    add_heading(pdf, "Harbor Study Pack - Terms and Handbook")
    add_body(
        pdf,
        "This is the binding contract. If this page disagrees with any brochure or ad, "
        "this handbook wins.",
    )
    add_body(
        pdf,
        "Section A - Hardware. Laptops, tablets, and headphones are sold separately. "
        "The Student Starter pack price never includes a computer. Staff must not promise "
        "free hardware.",
    )
    add_body(
        pdf,
        "Section B - Refunds. You may request a refund within 7 days of purchase, and "
        "only if you have not opened any online lesson. After day 7, or after you open a "
        "lesson, fees are non-refundable. There is no 30-day refund.",
    )
    pdf.add_page()
    add_heading(pdf, "Harbor Study Pack - Support rules")
    add_body(
        pdf,
        "Section C - Live sessions. A tutor hosts live Q and A every Friday at 6pm "
        "Pakistan time. Recordings are not guaranteed.",
    )
    add_body(
        pdf,
        "Section D - Email. We aim to reply to support email within one business day. "
        "Public holidays do not count as business days.",
    )
    add_body(
        pdf,
        "Section E - Shipping. Printed workbooks ship free to addresses inside Pakistan. "
        "International shipping is paid by the student.",
    )
    out = OUT_DIR / "fine_print_terms.pdf"
    pdf.output(out)
    print(f"Wrote {out}")


if __name__ == "__main__":
    write_promise()
    write_fine_print()
