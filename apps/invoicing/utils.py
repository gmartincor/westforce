from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from io import BytesIO


class PDFStyles:
    @staticmethod
    def get_styles():
        base = getSampleStyleSheet()
        return {
            'company': ParagraphStyle('Company', parent=base['Normal'], fontSize=10, spaceBefore=0, spaceAfter=0),
            'invoice_data': ParagraphStyle('InvoiceData', parent=base['Normal'], fontSize=10, alignment=TA_RIGHT),
            'client': ParagraphStyle('Client', parent=base['Normal'], fontSize=9),
            'table_content': ParagraphStyle('TableContent', parent=base['Normal'], fontSize=9),
            'legal': ParagraphStyle('Legal', parent=base['Normal'], fontSize=7, alignment=TA_CENTER, spaceBefore=3, spaceAfter=6),
            'footer': ParagraphStyle('Footer', parent=base['Normal'], fontSize=8, alignment=TA_CENTER),
            'tax_invoice': ParagraphStyle('TaxInvoice', parent=base['Normal'], fontSize=14, fontName='Helvetica-Bold', alignment=TA_RIGHT)
        }


class InvoiceHeaderBuilder:
    @staticmethod
    def build(invoice, styles):
        company_info = InvoiceHeaderBuilder._get_company_info(invoice.company)
        invoice_info = InvoiceHeaderBuilder._get_invoice_info(invoice)
        
        header_data = [[
            Paragraph("<br/>".join(company_info), styles['company']),
            Paragraph("<br/>".join(invoice_info), styles['invoice_data'])
        ]]
        
        header_table = Table(header_data, colWidths=[11*cm, 6*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        return header_table

    @staticmethod
    def _get_company_info(company):
        info = [f"<b>{company.business_name}</b>"]
        
        if company.legal_name and company.legal_name != company.business_name:
            info.append(company.legal_name)
        
        info.extend([
            f"ABN: {company.get_formatted_abn()}",
            f"{company.address}",
            f"{company.city} {company.state} {company.postal_code}"
        ])
        
        if company.acn:
            info.append(f"ACN: {company.get_formatted_acn()}")
        
        if company.phone:
            info.append(f"Phone: {company.phone}")
        if company.email:
            info.append(f"Email: {company.email}")
        if company.website:
            info.append(f"Web: {company.website}")
        
        return info

    @staticmethod
    def _get_invoice_info(invoice):
        title = "<b>TAX INVOICE</b>" if invoice.is_tax_invoice else "<b>INVOICE</b>"
        
        info = [
            title,
            f"Number: {invoice.reference or 'DRAFT'}",
            f"Date: {invoice.issue_date.strftime('%d/%m/%Y')}"
        ]
        
        return info


class InvoiceClientSection:
    @staticmethod
    def build(invoice, styles):
        client_info = [
            "<b>BILL TO:</b>",
            f"{invoice.client_name}",
            f"{invoice.client_address}"
        ]
        
        if invoice.client_abn:
            client_info.append(f"ABN: {invoice.client_abn}")
        
        client_data = [[Paragraph("<br/>".join(client_info), styles['client'])]]
        
        client_table = Table(client_data, colWidths=[17*cm])
        client_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        return client_table


class InvoiceItemsTable:
    @staticmethod
    def build(invoice, styles):
        headers = ['Description', 'Qty', 'Unit Price', 'GST', 'Amount']
        item_data = [headers]
        
        for item in invoice.items.all():
            item_data.append([
                Paragraph(item.description.replace('\n', '<br/>'), styles['table_content']),
                str(item.quantity),
                f"${item.unit_price:.2f}",
                f"{item.gst_rate:.0f}%",
                f"${item.total:.2f}"
            ])
        
        items_table = Table(item_data, colWidths=[8*cm, 1.5*cm, 2*cm, 1.5*cm, 2*cm])
        items_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ]))
        
        return items_table


class InvoiceTotalsSection:
    @staticmethod
    def build(invoice, styles):
        payment_info = InvoiceTotalsSection._get_payment_info(invoice)
        totals_table = InvoiceTotalsSection._get_totals_table(invoice)
        
        final_data = [[
            Paragraph("<br/>".join(payment_info), styles['table_content']),
            totals_table
        ]]
        
        final_table = Table(final_data, colWidths=[10.5*cm, 6.5*cm])
        final_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ]))
        
        return final_table

    @staticmethod
    def _get_payment_info(invoice):
        info = []
        if invoice.payment_terms:
            info.extend([
                "<b>PAYMENT TERMS</b>",
                invoice.payment_terms,
                ""
            ])
        
        if invoice.company.bank_name:
            info.extend([
                "<b>Bank Details:</b>",
                f"Bank: {invoice.company.bank_name}",
                f"BSB: {invoice.company.get_formatted_bsb()}",
                f"Account: {invoice.company.account_number}"
            ])
        
        return info

    @staticmethod
    def _get_totals_table(invoice):
        totals_data = [
            ["Subtotal (excl. GST)", f"${invoice.subtotal:.2f}"]
        ]
        
        if invoice.gst_amount > 0:
            totals_data.append(["GST (10%)", f"${invoice.gst_amount:.2f}"])
        
        totals_data.append(["TOTAL (inc. GST)", f"${invoice.total_amount:.2f}"])
        
        totals_table = Table(totals_data, colWidths=[4*cm, 2.5*cm])
        totals_table.setStyle(TableStyle([
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ]))
        
        return totals_table


def generate_invoice_pdf(invoice):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=30*mm
    )
    
    styles = PDFStyles.get_styles()
    story = []
    
    story.append(InvoiceHeaderBuilder.build(invoice, styles))
    story.append(Spacer(1, 12*mm))
    
    story.append(InvoiceClientSection.build(invoice, styles))
    story.append(Spacer(1, 8*mm))
    
    story.append(InvoiceItemsTable.build(invoice, styles))
    story.append(Spacer(1, 8*mm))
    
    story.append(InvoiceTotalsSection.build(invoice, styles))
    story.append(Spacer(1, 10*mm))
    
    legal_note = invoice.get_tax_invoice_note()
    if legal_note:
        story.append(Paragraph(legal_note, styles['legal']))
        story.append(Spacer(1, 5*mm))
    
    footer_text = _build_footer_text(invoice)
    story.append(Paragraph(footer_text, styles['footer']))
    
    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def _build_footer_text(invoice):
    footer_parts = []
    
    if invoice.company.gst_registered:
        footer_parts.append("GST registered")
    
    footer_parts.append(f"{invoice.company.get_legal_form_display()} | ABN: {invoice.company.get_formatted_abn()}")
    
    return " | ".join(footer_parts)
