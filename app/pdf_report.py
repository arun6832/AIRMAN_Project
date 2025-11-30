from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
def create_report_bytes(route,aircraft,dep,arr,dep_metar,arr_metar,poh_limits,best_runway,final_dep,final_arr,decision_text,alt):
    buf=BytesIO(); c=canvas.Canvas(buf,pagesize=letter); w,h=letter
    c.setFont('Helvetica-Bold',14); c.drawString(40,h-40,'AIRMAN — Preflight Report')
    c.setFont('Helvetica',10); c.drawString(40,h-70,f'Route: {dep} ➜ {arr}'); c.drawString(40,h-90,f'Aircraft: {aircraft}')
    c.drawString(40,h-110,f'Decision: {decision_text}'); c.drawString(40,h-130,f'Suggested cruise altitude: {alt}')
    c.showPage(); c.save(); buf.seek(0); return buf.getvalue()
