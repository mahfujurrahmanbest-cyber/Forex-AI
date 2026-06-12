"""PDF Report Generator for Execution Decisions."""
import os
from datetime import datetime
from typing import Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas


class ExecutionPDFGenerator:
    """
    Generate Bloomberg/Goldman Sachs style PDF reports.
    
    Pages:
    1. Executive Decision Dashboard
    2. Weekly Report Extraction
    3. Live Market Analysis
    4. ICT Analysis
    5. Trade Execution Card
    6. Risk Management
    7. Decision Summary
    """
    
    # Colors
    NAVY = colors.HexColor('#0D1B2A')
    GOLD = colors.HexColor('#C9A84C')
    GREEN = colors.HexColor('#1E8449')
    RED = colors.HexColor('#C0392B')
    ORANGE = colors.HexColor('#E67E22')
    YELLOW = colors.HexColor('#F4D03F')
    LTGRAY = colors.HexColor('#F2F4F7')
    MIDGRAY = colors.HexColor('#D5D8DC')
    DARKGRAY = colors.HexColor('#2C3E50')
    WHITE = colors.white
    
    # Page dimensions
    PAGE_W, PAGE_H = A4
    MARGIN = 15 * mm
    TW = PAGE_W - 2 * MARGIN
    
    def __init__(self):
        self.styles = {}
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup paragraph styles."""
        self.styles['title'] = ParagraphStyle(
            'title',
            fontName='Helvetica-Bold',
            fontSize=24,
            textColor=self.WHITE,
            alignment=TA_CENTER,
        )
        
        self.styles['subtitle'] = ParagraphStyle(
            'subtitle',
            fontName='Helvetica',
            fontSize=12,
            textColor=self.GOLD,
            alignment=TA_CENTER,
        )
        
        self.styles['section_header'] = ParagraphStyle(
            'section_header',
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=self.WHITE,
            leftIndent=10,
        )
        
        self.styles['body'] = ParagraphStyle(
            'body',
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            textColor=self.DARKGRAY,
        )
        
        self.styles['small'] = ParagraphStyle(
            'small',
            fontName='Helvetica',
            fontSize=7,
            textColor=colors.HexColor('#666666'),
        )
    
    def generate(self, data: Dict[str, Any], output_folder: str) -> str:
        """
        Generate the PDF report.
        
        Args:
            data: Complete analysis data
            output_folder: Folder to save the PDF
            
        Returns:
            Path to generated PDF
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"Instant_Trade_Decision_{timestamp}.pdf"
        filepath = os.path.join(output_folder, filename)
        
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            leftMargin=self.MARGIN,
            rightMargin=self.MARGIN,
            topMargin=self.MARGIN,
            bottomMargin=self.MARGIN,
        )
        
        story = []
        
        # Page 1: Executive Decision Dashboard
        story.extend(self._build_executive_dashboard(data))
        story.append(PageBreak())
        
        # Page 2: Weekly Report Extraction
        story.extend(self._build_report_extraction(data))
        story.append(PageBreak())
        
        # Page 3: Live Market Analysis
        story.extend(self._build_live_market(data))
        story.append(PageBreak())
        
        # Page 4: ICT Analysis
        story.extend(self._build_ict_analysis(data))
        story.append(PageBreak())
        
        # Page 5: Trade Execution Card
        story.extend(self._build_execution_card(data))
        story.append(PageBreak())
        
        # Page 6: Risk Management
        story.extend(self._build_risk_management(data))
        story.append(PageBreak())
        
        # Page 7: Decision Summary
        story.extend(self._build_decision_summary(data))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_footer, onLaterPages=self._add_footer)
        
        return filepath
    
    def _section_header(self, text: str, bg_color=None) -> Table:
        """Create a section header."""
        if bg_color is None:
            bg_color = self.NAVY
        
        data = [[Paragraph(f'<b>{text}</b>', self.styles['section_header'])]]
        table = Table(data, colWidths=[self.TW])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LINEABOVE', (0, 0), (-1, 0), 2, self.GOLD),
        ]))
        return table
    
    def _decision_box(self, decision: Dict[str, Any]) -> Table:
        """Create the main decision display box."""
        action = decision.get('action', 'ABORT')
        emoji = decision.get('emoji', '🔴')
        confidence = decision.get('confidence', 0)
        
        # Determine background color
        color_map = {
            'EXECUTE NOW': self.GREEN,
            'WAIT FOR CONFIRMATION': self.YELLOW,
            'MONITOR ONLY': self.ORANGE,
            'ABORT': self.RED,
        }
        bg_color = color_map.get(action, self.RED)
        text_color = self.WHITE if action != 'WAIT FOR CONFIRMATION' else self.DARKGRAY
        
        # Create decision display
        decision_text = Paragraph(
            f'<b>{emoji} {action}</b>',
            ParagraphStyle('decision', fontName='Helvetica-Bold', fontSize=20,
                          textColor=text_color, alignment=TA_CENTER)
        )
        
        confidence_text = Paragraph(
            f'Confidence: {confidence}%',
            ParagraphStyle('conf', fontName='Helvetica', fontSize=12,
                          textColor=text_color, alignment=TA_CENTER)
        )
        
        data = [[decision_text], [confidence_text]]
        table = Table(data, colWidths=[self.TW])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return table
    
    def _data_table(self, data: list, col_ratios: list, header: bool = True) -> Table:
        """Create a styled data table."""
        widths = [r * self.TW for r in col_ratios]
        table = Table(data, colWidths=widths, repeatRows=1 if header else 0)
        
        style = [
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 0.5, self.MIDGRAY),
        ]
        
        if header:
            style.extend([
                ('BACKGROUND', (0, 0), (-1, 0), self.NAVY),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.WHITE),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ])
        
        # Alternating rows
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), self.LTGRAY))
        
        table.setStyle(TableStyle(style))
        return table
    
    def _build_executive_dashboard(self, data: Dict) -> list:
        """Build Page 1: Executive Decision Dashboard."""
        elements = []
        
        # Header
        elements.append(self._section_header('INSTANT TRADE DECISION - EXECUTIVE DASHBOARD'))
        elements.append(Spacer(1, 10))
        
        # Main decision box
        decision = data.get('final_decision', {})
        elements.append(self._decision_box(decision))
        elements.append(Spacer(1, 15))
        
        # Quick stats
        pair = data.get('pair', 'N/A')
        direction = data.get('direction', 'N/A')
        instant_score = data.get('instant_score', {}).get('total', 0)
        trade_quality = data.get('trade_quality', {}).get('total', 0)
        
        stats_data = [
            ['PAIR', 'DIRECTION', 'INSTANT SCORE', 'TRADE QUALITY', 'TIMESTAMP'],
            [pair, direction, f'{instant_score}/28', f'{trade_quality}/100',
             datetime.now().strftime('%Y-%m-%d %H:%M UTC')],
        ]
        elements.append(self._data_table(stats_data, [0.2, 0.2, 0.2, 0.2, 0.2]))
        elements.append(Spacer(1, 15))
        
        # Score breakdown
        elements.append(self._section_header('SCORE BREAKDOWN', self.DARKGRAY))
        elements.append(Spacer(1, 8))
        
        breakdown = data.get('instant_score', {}).get('breakdown', {})
        breakdown_data = [['CRITERIA', 'POINTS', 'STATUS']]
        for key, value in breakdown.items():
            status = '✓' if value > 0 else '✗'
            breakdown_data.append([key.replace('_', ' ').title(), str(value), status])
        
        elements.append(self._data_table(breakdown_data, [0.5, 0.25, 0.25]))
        elements.append(Spacer(1, 15))
        
        # Reason
        reason = decision.get('reason', 'No reason provided')
        elements.append(Paragraph(f'<b>Decision Reason:</b> {reason}', self.styles['body']))
        
        return elements
    
    def _build_report_extraction(self, data: Dict) -> list:
        """Build Page 2: Weekly Report Extraction."""
        elements = []
        
        elements.append(self._section_header('WEEKLY REPORT EXTRACTION'))
        elements.append(Spacer(1, 10))
        
        report = data.get('report_summary', {})
        
        if not report or not report.get('parsed'):
            elements.append(Paragraph(
                'No weekly report uploaded or parsing failed.',
                self.styles['body']
            ))
            return elements
        
        # Report data table
        report_data = [
            ['METRIC', 'VALUE'],
            ['Weekly Direction', report.get('weekly_direction', 'N/A')],
            ['Buy Score', str(report.get('weekly_buy_score', 'N/A'))],
            ['Sell Score', str(report.get('weekly_sell_score', 'N/A'))],
            ['Confidence', f"{report.get('weekly_confidence', 'N/A')}%"],
            ['MTF Score', str(report.get('mtf_score', 'N/A'))],
            ['Classification', report.get('classification', 'N/A')],
            ['COT Bias', report.get('cot_bias', 'N/A')],
            ['DXY Bias', report.get('dxy_bias', 'N/A')],
        ]
        
        elements.append(self._data_table(report_data, [0.4, 0.6]))
        
        return elements
    
    def _build_live_market(self, data: Dict) -> list:
        """Build Page 3: Live Market Analysis."""
        elements = []
        
        elements.append(self._section_header('LIVE MARKET ANALYSIS'))
        elements.append(Spacer(1, 10))
        
        live_data = data.get('live_data', {})
        price_data = live_data.get('price_data', {})
        tech_data = live_data.get('technical_data', {})
        
        # Price data
        price_table = [
            ['METRIC', 'VALUE'],
            ['Current Price', str(price_data.get('current', 'N/A'))],
            ['Daily High', str(price_data.get('high', 'N/A'))],
            ['Daily Low', str(price_data.get('low', 'N/A'))],
            ['Day Change', f"{price_data.get('day_change_pct', 0)}%"],
            ['Week Change', f"{price_data.get('week_change_pct', 0)}%"],
        ]
        elements.append(self._data_table(price_table, [0.4, 0.6]))
        elements.append(Spacer(1, 10))
        
        # Technical indicators
        elements.append(self._section_header('TECHNICAL INDICATORS', self.DARKGRAY))
        elements.append(Spacer(1, 8))
        
        rsi = tech_data.get('rsi', {})
        macd = tech_data.get('macd', {})
        adx = tech_data.get('adx', {})
        
        tech_table = [
            ['INDICATOR', 'VALUE', 'SIGNAL'],
            ['RSI (14)', str(rsi.get('value', 'N/A')), rsi.get('signal', 'N/A')],
            ['MACD', str(macd.get('histogram', 'N/A')), macd.get('trend', 'N/A')],
            ['ADX', str(adx.get('value', 'N/A')), adx.get('trend_strength', 'N/A')],
            ['Consensus', tech_data.get('consensus', 'N/A'), '-'],
        ]
        elements.append(self._data_table(tech_table, [0.33, 0.33, 0.34]))
        
        return elements
    
    def _build_ict_analysis(self, data: Dict) -> list:
        """Build Page 4: ICT Analysis."""
        elements = []
        
        elements.append(self._section_header('ICT SMART MONEY ANALYSIS'))
        elements.append(Spacer(1, 10))
        
        ict = data.get('ict_analysis', {})
        
        # ICT components
        liquidity = ict.get('liquidity', {})
        ob = ict.get('order_blocks', {})
        fvg = ict.get('fair_value_gaps', {})
        zones = ict.get('zones', {})
        smt = ict.get('smt_divergence', {})
        
        ict_table = [
            ['COMPONENT', 'STATUS', 'DETAILS'],
            ['Liquidity Sweep', '✓' if liquidity.get('sweep_detected') else '✗',
             liquidity.get('sweep_direction', 'None')],
            ['Order Block', '✓' if ob.get('active_ob') else '✗',
             ob.get('ob_direction', 'None')],
            ['Fair Value Gap', '✓' if fvg.get('fvg_present') else '✗',
             fvg.get('fvg_direction', 'None')],
            ['Zone', zones.get('zone', 'N/A'),
             f"{zones.get('zone_percentage', 0)}%"],
            ['SMT Divergence', '✓' if smt.get('detected') else '✗',
             smt.get('divergence_type', 'None')],
        ]
        elements.append(self._data_table(ict_table, [0.3, 0.2, 0.5]))
        elements.append(Spacer(1, 10))
        
        # ICT Score
        alignment = ict.get('alignment_score', {})
        elements.append(Paragraph(
            f"<b>ICT Alignment Score:</b> {alignment.get('score', 0)}/100 "
            f"({alignment.get('percentage', 0)}%)",
            self.styles['body']
        ))
        
        return elements
    
    def _build_execution_card(self, data: Dict) -> list:
        """Build Page 5: Trade Execution Card."""
        elements = []
        
        elements.append(self._section_header('TRADE EXECUTION CARD', self.GREEN))
        elements.append(Spacer(1, 10))
        
        levels = data.get('trade_levels', {})
        
        if not levels or levels.get('error'):
            elements.append(Paragraph(
                'Trade levels not calculated - score below minimum threshold.',
                self.styles['body']
            ))
            return elements
        
        level_data = levels.get('levels', {})
        sizing = levels.get('sizing', {})
        
        # Trade levels
        trade_table = [
            ['LEVEL', 'PRICE', 'PIPS', 'R:R'],
            ['Entry', str(level_data.get('entry', 'N/A')), '-', '-'],
            ['Stop Loss', str(level_data.get('stop_loss', 'N/A')),
             str(level_data.get('sl_pips', 'N/A')), '-'],
            ['TP1 (25%)', str(level_data.get('tp1', 'N/A')),
             str(level_data.get('tp1_pips', 'N/A')), '1:1.5'],
            ['TP2 (25%)', str(level_data.get('tp2', 'N/A')),
             str(level_data.get('tp2_pips', 'N/A')), '1:3'],
            ['TP3 (25%)', str(level_data.get('tp3', 'N/A')),
             str(level_data.get('tp3_pips', 'N/A')), '1:5'],
            ['TP4 (25%)', str(level_data.get('tp4', 'N/A')),
             str(level_data.get('tp4_pips', 'N/A')), '1:8'],
        ]
        elements.append(self._data_table(trade_table, [0.25, 0.3, 0.2, 0.25]))
        elements.append(Spacer(1, 10))
        
        # Position sizing
        elements.append(self._section_header('POSITION SIZING', self.DARKGRAY))
        elements.append(Spacer(1, 8))
        
        sizing_table = [
            ['PARAMETER', 'VALUE'],
            ['Lot Size', str(sizing.get('lot_size', 'N/A'))],
            ['Risk Amount', f"${sizing.get('risk_amount', 'N/A')}"],
            ['Max Loss', f"${sizing.get('max_loss', 'N/A')}"],
            ['Margin Required', f"${sizing.get('margin_required', 'N/A')}"],
            ['Risk %', f"{sizing.get('risk_percentage', 'N/A')}%"],
        ]
        elements.append(self._data_table(sizing_table, [0.5, 0.5]))
        
        return elements
    
    def _build_risk_management(self, data: Dict) -> list:
        """Build Page 6: Risk Management."""
        elements = []
        
        elements.append(self._section_header('RISK MANAGEMENT', self.ORANGE))
        elements.append(Spacer(1, 10))
        
        # News gate
        news = data.get('news_gate', {})
        elements.append(Paragraph(f"<b>News Status:</b> {news.get('risk_level', 'N/A')}",
                                  self.styles['body']))
        elements.append(Paragraph(f"<b>Recommendation:</b> {news.get('recommendation', 'N/A')}",
                                  self.styles['body']))
        elements.append(Spacer(1, 10))
        
        # Session
        session = data.get('kill_zone', {})
        elements.append(Paragraph(
            f"<b>Current Session:</b> {', '.join(session.get('active_sessions', ['N/A']))}",
            self.styles['body']
        ))
        elements.append(Paragraph(
            f"<b>Kill Zone:</b> {'Yes' if session.get('is_kill_zone') else 'No'}",
            self.styles['body']
        ))
        elements.append(Paragraph(
            f"<b>Session Quality:</b> {session.get('session_score', {}).get('quality', 'N/A')}",
            self.styles['body']
        ))
        elements.append(Spacer(1, 10))
        
        # DXY
        dxy = data.get('dxy_analysis', {})
        elements.append(Paragraph(
            f"<b>DXY Status:</b> {dxy.get('classification', {}).get('status', 'N/A')}",
            self.styles['body']
        ))
        elements.append(Paragraph(
            f"<b>Supports Trade:</b> {'Yes' if dxy.get('supports_trade') else 'No'}",
            self.styles['body']
        ))
        
        return elements
    
    def _build_decision_summary(self, data: Dict) -> list:
        """Build Page 7: Decision Summary."""
        elements = []
        
        elements.append(self._section_header('FINAL DECISION SUMMARY'))
        elements.append(Spacer(1, 10))
        
        decision = data.get('final_decision', {})
        
        # Final decision box again
        elements.append(self._decision_box(decision))
        elements.append(Spacer(1, 15))
        
        # Summary table
        summary_data = [
            ['METRIC', 'VALUE', 'STATUS'],
            ['Instant Score', f"{decision.get('instant_score', 0)}/28",
             '✓' if decision.get('instant_score', 0) >= 14 else '✗'],
            ['Trade Quality', f"{decision.get('trade_quality', 0)}/100",
             '✓' if decision.get('trade_quality', 0) >= 70 else '✗'],
            ['Confidence', f"{decision.get('confidence', 0)}%",
             '✓' if decision.get('confidence', 0) >= 80 else '✗'],
            ['Can Trade', 'Yes' if decision.get('can_trade') else 'No',
             '✓' if decision.get('can_trade') else '✗'],
        ]
        elements.append(self._data_table(summary_data, [0.4, 0.3, 0.3]))
        elements.append(Spacer(1, 15))
        
        # Disclaimer
        elements.append(HRFlowable(width='100%', thickness=1, color=self.GOLD))
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(
            '<b>DISCLAIMER:</b> This analysis is for informational purposes only. '
            'Trading forex involves substantial risk. Past performance is not indicative '
            'of future results. Always use proper risk management.',
            self.styles['small']
        ))
        
        return elements
    
    def _add_footer(self, canvas, doc):
        """Add footer to each page."""
        canvas.saveState()
        canvas.setFont('Helvetica', 7)
        canvas.setFillColor(colors.HexColor('#888888'))
        canvas.setStrokeColor(self.GOLD)
        canvas.setLineWidth(0.5)
        canvas.line(self.MARGIN, 15 * mm, self.PAGE_W - self.MARGIN, 15 * mm)
        canvas.drawString(
            self.MARGIN, 10 * mm,
            'Instant Trade Decision Engine | ICT + SMC + COT Analysis'
        )
        canvas.drawRightString(
            self.PAGE_W - self.MARGIN, 10 * mm,
            f'Page {doc.page} | {datetime.now().strftime("%Y-%m-%d %H:%M UTC")}'
        )
        canvas.restoreState()
