from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..services.report_services import generate_report
from ..database.models import FuelData
from typing import Optional
import markdown
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
import io, re, logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/report")
def get_report(
    station_id: str = Query(...),
    fuel_type: Optional[str] = Query(None),  # optional; determine if not provided
    db: Session = Depends(get_db)
):
    # If no fuel_type provided, pick the most recent fuel_type for the station
    if not fuel_type:
        latest = db.query(FuelData).filter(FuelData.station_id == station_id).order_by(FuelData.timestamp.desc()).first()
        if latest:
            fuel_type = latest.fuel_type
            logger.info(f"No fuel_type supplied; using latest fuel_type={fuel_type} for station {station_id}")
        else:
            raise HTTPException(status_code=400, detail="fuel_type is required when station has no fuel data")

    logger.info(f"/report called for station_id={station_id}, fuel_type={fuel_type}")
    try:
        report = generate_report(db, station_id, fuel_type)
        return {"station_id": station_id, "fuel_type": fuel_type, "report": report}
    except Exception as e:
        logger.exception(f"Report generation error for {station_id} / {fuel_type}")
        raise HTTPException(status_code=500, detail=f"Report generation failed: {str(e)}")


@router.get("/report/debug")
def get_report_debug(
    station_id: str = Query(...),
    fuel_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Debug endpoint: returns raw LLM client response or error details to aid debugging."""
    logger.info(f"/report/debug called for station_id={station_id}, fuel_type={fuel_type}")
    # resolve fuel_type same as get_report
    if not fuel_type:
        latest = db.query(FuelData).filter(FuelData.station_id == station_id).order_by(FuelData.timestamp.desc()).first()
        if latest:
            fuel_type = latest.fuel_type
            logger.info(f"No fuel_type supplied for debug; using latest fuel_type={fuel_type}")
        else:
            raise HTTPException(status_code=400, detail="fuel_type is required when station has no fuel data")
    try:
        report = generate_report(db, station_id, fuel_type)
        return Response(content=report, media_type="text/plain")
    except Exception as e:
        logger.exception("Debug report generation failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/report/pdf")
def get_report_pdf(
    station_id: str = Query(...),
    fuel_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    if not fuel_type:
        latest = db.query(FuelData).filter(FuelData.station_id == station_id).order_by(FuelData.timestamp.desc()).first()
        if latest:
            fuel_type = latest.fuel_type
        else:
            raise HTTPException(status_code=400, detail="fuel_type is required when station has no fuel data")

    report_md = generate_report(db, station_id, fuel_type)
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    h1_style = ParagraphStyle('H1', parent=styles['Heading1'],
                               textColor=HexColor('#003366'), fontSize=18, spaceAfter=12)
    h2_style = ParagraphStyle('H2', parent=styles['Heading2'],
                               textColor=HexColor('#0066cc'), fontSize=14, spaceAfter=8)
    h3_style = ParagraphStyle('H3', parent=styles['Heading3'],
                               textColor=HexColor('#444444'), fontSize=12, spaceAfter=6)
    body_style = ParagraphStyle('Body', parent=styles['Normal'],
                                 fontSize=10, spaceAfter=6, leading=16)
    bullet_style = ParagraphStyle('Bullet', parent=styles['Normal'],
                                   fontSize=10, spaceAfter=4, leftIndent=20, leading=14)

    # Parse markdown lines
    for line in report_md.split('\n'):
        if line.startswith('# '):
            story.append(Paragraph(line[2:], h1_style))
            story.append(Spacer(1, 6))
        elif line.startswith('## '):
            story.append(Spacer(1, 8))
            story.append(Paragraph(line[3:], h2_style))
        elif line.startswith('### '):
            story.append(Paragraph(line[4:], h3_style))
        elif line.startswith('- ') or line.startswith('* '):
            text = line[2:].replace('**', '<b>').replace('**', '</b>')
            story.append(Paragraph(f"• {text}", bullet_style))
        elif line.strip() == '':
            story.append(Spacer(1, 6))
        else:
            text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
            story.append(Paragraph(text, body_style))
    
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=report_{station_id}.pdf"}
    )