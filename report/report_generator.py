import json
import os
from datetime import datetime

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    from reportlab.lib.units import inch
except ImportError:
    SimpleDocTemplate = None

class ForensicReportEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle non-serializable objects gracefully."""
    def default(self, obj):
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)

class ReportGenerator:
    def __init__(self, output_dir="data/reports"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_json(self, report_data, filename="forensic_report.json"):
        filepath = os.path.join(self.output_dir, filename)
        try:
            with open(filepath, 'w') as f:
                json.dump(report_data, f, indent=4, cls=ForensicReportEncoder)
            return filepath
        except Exception as e:
            print(f"Error generating JSON report: {e}")
            return None

    def generate_pdf(self, report_data, filename="forensic_report.pdf"):
        if not SimpleDocTemplate:
            print("ReportLab is not installed or incomplete. PDF generation skipped.")
            return None
            
        filepath = os.path.join(self.output_dir, filename)
        
        try:
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Custom Styles
            title_style = styles['Heading1']
            subtitle_style = styles['Heading2']
            normal_style = styles['Normal']
            code_style = ParagraphStyle('Code', parent=styles['Normal'], fontName='Helvetica', fontSize=8, leading=10)
            
            elements = []
            
            # Title
            elements.append(Paragraph("Digital Forensics Investigation Report", title_style))
            elements.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", normal_style))
            elements.append(Spacer(1, 0.25 * inch))
            
            # Executive Summary
            elements.append(Paragraph("Executive Summary", subtitle_style))
            summary_data = [
                ["Target Image:", report_data.get('target_image', 'Unknown')],
                ["Files Parsed:", str(len(report_data.get('hashes', [])) or len(report_data.get('timeline', [])))],
                ["Recovered Artifacts:", str(len(report_data.get('recovered_files', [])))],
                ["Anomalies Detected:", str(len(report_data.get('anomalies', [])))]
            ]
            t = Table(summary_data, colWidths=[2*inch, 4*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('PADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(t)
            elements.append(Spacer(1, 0.5 * inch))
            
            # Anomalies Section
            if report_data.get('anomalies'):
                elements.append(Paragraph("Threat Intelligence & Anomalies", subtitle_style))
                anomaly_headers = ["Severity", "Reason", "File Path"]
                anomaly_rows = [anomaly_headers]
                
                for a in report_data.get('anomalies', [])[:50]: # Limit to top 50 for PDF
                    severity = a.get('severity', 'N/A')
                    reason = a.get('reason', 'N/A')
                    file_path = Paragraph(a.get('file', 'N/A'), code_style) # Wrap long paths
                    anomaly_rows.append([severity, reason, file_path])
                
                at = Table(anomaly_rows, colWidths=[0.8*inch, 1.5*inch, 4.2*inch], repeatRows=1)
                at.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(at)
                elements.append(Spacer(1, 0.5 * inch))

            # Timeline Section
            if report_data.get('timeline'):
                elements.append(PageBreak())
                elements.append(Paragraph("Forensic Timeline (Top 100 Events)", subtitle_style))
                timeline_headers = ["Timestamp", "Action", "File"]
                timeline_rows = [timeline_headers]
                
                for e in report_data.get('timeline', [])[:100]:
                    timeline_rows.append([
                        e.get('timestamp', ''),
                        e.get('action', ''),
                        Paragraph(e.get('file', ''), code_style)
                    ])
                
                tt = Table(timeline_rows, colWidths=[1.8*inch, 0.8*inch, 3.9*inch], repeatRows=1)
                tt.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                elements.append(tt)

            # Build PDF
            doc.build(elements)
            return filepath
        except Exception as e:
            print(f"Error generating PDF report: {e}")
            import traceback
            traceback.print_exc()
            return None
