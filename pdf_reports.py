from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4 
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import datetime as dt

pdfmetrics.registerFont(TTFont('Signika-Bold', 'C:/Users/SATHWIK/Downloads/Signika/static/Signika-Bold.ttf'))
pdfmetrics.registerFont(TTFont('Signika-SemiBold', 'C:/Users/SATHWIK/Downloads/Signika/static/Signika-SemiBold.ttf'))

def first_page_heading(canvas, doc):
    canvas.setFont("Signika-Bold", 24)
    canvas.drawString(110, 790, "Running Room")
    canvas.setFont("Signika-SemiBold", 24)
    canvas.drawString(270, 790, "(Simhachalam-North)")
    canvas.setFont("Signika-SemiBold", 20)
    canvas.drawString(160, 760, doc.title)
    canvas.drawString(290, 760, "Date: " + dt.datetime.now().date().strftime('%d/%m/%Y'))
    canvas.line(0, 740, 800, 740)  

def table_generator(name, df):
    # Initialize the PDF buffer
    pdf_buffer = BytesIO()
    my_doc = SimpleDocTemplate(pdf_buffer, pagesize=A4, title=name)

    # Convert DataFrame into data format for the table
    data = [df.columns.tolist()] + df.values.tolist()

    # Initialize total_diff for Rest Report calculation
    total_diff = 0

    # Only if the report is "Rest Report", sum the Diff column
    if name == "Rest Report":
        if 'Difference' in df.columns:
            total_diff = df['Difference'].sum()
        else:
            total_diff = 0

        # Add a row at the end with the total of the 'Diff' column
        total_row = [''] * len(df.columns)  # Empty values for all columns
        total_row[df.columns.get_loc('Difference')] = f"Total: {total_diff:.2f} hours"  # Insert total at the Diff column
        data.append(total_row)

    # Layout calculations for column widths
    page_width = A4[0]
    margin = 0.02 * inch  
    available_width = page_width - 2 * margin  
    num_columns = len(df.columns)
    equal_width = available_width / num_columns
    col_widths = [equal_width] * num_columns

    # Specific column width adjustments based on report name
    try:
        if(name == "Meals Report"):
            cmsid_index = df.columns.get_loc('CMS ID')
            crewname_index = df.columns.get_loc('Crew Name')
            checkin_index = df.columns.get_loc('CheckIn Time')
            checkout_index = df.columns.get_loc('CheckOut Time')

            col_widths[cmsid_index] = available_width * 0.1  
            col_widths[crewname_index] = available_width * 0.25 
            col_widths[checkin_index] = available_width * 0.14
            col_widths[checkout_index] = available_width * 0.14

            remaining_width = available_width - col_widths[cmsid_index] - col_widths[crewname_index]- col_widths[checkin_index] - col_widths[checkout_index]
            remaining_columns = num_columns - 4 
            remaining_equal_width = remaining_width / remaining_columns if remaining_columns > 0 else 0
            for i in range(num_columns):
                if i != cmsid_index and i != crewname_index and i != checkin_index and i != checkout_index:
                    col_widths[i] = remaining_equal_width
        elif(name == "Linen Report"):
            cmsid_index = df.columns.get_loc('CMS ID')
            crewname_index = df.columns.get_loc('Crew Name')
            checkin_index = df.columns.get_loc('CheckIn Time')

            col_widths[cmsid_index] = available_width * 0.1  
            col_widths[crewname_index] = available_width * 0.28 
            col_widths[checkin_index] = available_width * 0.14

            remaining_width = available_width - col_widths[cmsid_index] - col_widths[crewname_index]- col_widths[checkin_index]
            remaining_columns = num_columns - 3 
            remaining_equal_width = remaining_width / remaining_columns if remaining_columns > 0 else 0
            for i in range(num_columns):
                if i != cmsid_index and i != crewname_index and i != checkin_index:
                    col_widths[i] = remaining_equal_width
        elif(name == "Rest Report"):
            cmsid_index = df.columns.get_loc('CMS ID')
            crewname_index = df.columns.get_loc('Crew Name')
            checkin_index = df.columns.get_loc('CheckIn Time')
            checkout_index = df.columns.get_loc('CheckOut Time')

            col_widths[cmsid_index] = available_width * 0.1  
            col_widths[crewname_index] = available_width * 0.25 
            col_widths[checkin_index] = available_width * 0.14
            col_widths[checkout_index] = available_width * 0.14

            remaining_width = available_width - col_widths[cmsid_index] - col_widths[crewname_index]- col_widths[checkin_index] - col_widths[checkout_index]
            remaining_columns = num_columns - 4 
            remaining_equal_width = remaining_width / remaining_columns if remaining_columns > 0 else 0
            for i in range(num_columns):
                if i != cmsid_index and i != crewname_index and i != checkin_index and i != checkout_index:
                    col_widths[i] = remaining_equal_width
        else:
            print(f"Report name '{name}' not recognized. Applying default column widths.")
            col_widths = [equal_width] * num_columns 
    except KeyError as e:
        print(f"Column not found: {e}")

    # Create the table
    table = Table(data, colWidths=col_widths, hAlign='CENTER', vAlign='MIDDLE')

    # Apply the styling to the table
    table.setStyle(TableStyle([  # Apply styling here
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Signika-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    # Create the document and build it
    elements = []
    my_doc.topMargin = 100
    elements.append(table)

    # Build the PDF document
    my_doc.build(elements, onFirstPage=first_page_heading)

    # Return the PDF buffer
    pdf_buffer.seek(0)
    return pdf_buffer.read()
