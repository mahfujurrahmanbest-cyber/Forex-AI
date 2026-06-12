"""PDF report generation service."""
import os
from datetime import datetime, timedelta
from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)
from reportlab.pdfgen import canvas

from backend import db
from backend.models import CurrencyPair, PriceData, COTData, Signal, Report


class PDFReportGenerator:
    """Generate professional PDF reports for forex signals."""
    
    # Colors
    NAVY = colors.HexColor('#0D1B2A')
    GOLD = colors.HexColor('#C9A84C')
    RED = colors.HexColor('#C0392B')
    GREEN = colors.HexColor('#1E8449')
    LTGRAY = colors.HexColor('#F2F4F7')
    MIDGRAY = colors.HexColor('#D5D8DC')
    ORANGE = colors.HexColor('#E67E22')
    WHITE = colors.white
    
    # Page dimensions
    PAGE_W, PAGE_H = A4
    MARGIN = 20 * mm
    TW = PAGE_W - 2 * MARGIN  # Table width
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_styles()
    
    def _setup_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            fontName='Helvetica-Bold',
            fontSize=11,
            textColor=self.WHITE,
            alignment=TA_LEFT,
            spaceAfter=8,
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyText',
            fontName='Helvetica',
            fontSize=9,
            leading=13,
            textColor=colors.black,
        ))
        
        self.styles.add(ParagraphStyle(
            name='TableCell',
            fontName='Helvetica',
            fontSize=8,
            leading=10,
        ))
        
        self.styles.add(ParagraphStyle(
            name='SmallItalic',
            fontName='Helvetica-Oblique',
            fontSize=7.5,
            textColor=colors.HexColor('#888888'),
        ))
    
    def _create_section_header(self, text):
        """Create a section header bar."""
        data = [[Paragraph(text, self.styles['SectionHeader'])]]
        table = Table(data, colWidths=[self.TW])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.NAVY),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ]))
        return table
    
    def _create_data_table(self, data, col_ratios, header=True):
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
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.4, self.MIDGRAY),
        ]
        
        if header:
            style.extend([
                ('BACKGROUND', (0, 0), (-1, 0), self.NAVY),
                ('TEXTCOLOR', (0, 0), (-1, 0), self.WHITE),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ])
        
        # Alternating row colors
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(('BACKGROUND', (0, i), (-1, i), self.LTGRAY))
        
        table.setStyle(TableStyle(style))
        return table
    
    def _draw_cover_page(self, canvas, doc):
        """Draw the cover page."""
        canvas.saveState()
        
        # Full navy background
        canvas.setFillColor(self.NAVY)
        canvas.rect(0, 0, self.PAGE_W, self.PAGE_H, fill=1)
        
        # Title
        canvas.setFillColor(self.WHITE)
        canvas.setFont('Helvetica-Bold', 32)
        canvas.drawCentredString(self.PAGE_W / 2, 580, 'FOREX WEEKLY')
        
        canvas.setFillColor(self.GOLD)
        canvas.setFont('Helvetica-Bold', 28)
        canvas.drawCentredString(self.PAGE_W / 2, 540, 'SIGNAL REPORT')
        
        # Gold lines
        canvas.setStrokeColor(self.GOLD)
        canvas.setLineWidth(2)
        canvas.line(100, 520, self.PAGE_W - 100, 520)
        canvas.line(100, 380, self.PAGE_W - 100, 380)
        
        # Week info
        today = datetime.now()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        canvas.setFillColor(self.WHITE)
        canvas.setFont('Helvetica', 14)
        canvas.drawCentredString(
            self.PAGE_W / 2, 470,
            f"Week: {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}"
        )
        
        canvas.setFont('Helvetica', 11)
        canvas.drawCentredString(
            self.PAGE_W / 2, 440,
            'Data Sources: Technical Analysis + COT Positioning'
        )
        
        canvas.drawCentredString(
            self.PAGE_W / 2, 410,
            f"Generated: {today.strftime('%Y-%m-%d %H:%M UTC')}"
        )
        
        # Disclaimer
        canvas.setFillColor(self.GOLD)
        canvas.setFont('Helvetica-Oblique', 8)
        canvas.drawCentredString(
            self.PAGE_W / 2, 50,
            'For informational purposes only. Not financial advice. Trade at your own risk.'
        )
        
        canvas.restoreState()
    
    def _add_page_footer(self, canvas, doc):
        """Add footer to each page."""
        canvas.saveState()
        
        # Gold line
        canvas.setStrokeColor(self.GOLD)
        canvas.setLineWidth(0.5)
        canvas.line(self.MARGIN, 30, self.PAGE_W - self.MARGIN, 30)
        
        # Footer text
        canvas.setFillColor(colors.HexColor('#888888'))
        canvas.setFont('Helvetica', 7)
        canvas.drawString(
            self.MARGIN, 18,
            'Weekly Forex Signal Report | Technical + COT Analysis'
        )
        canvas.drawRightString(
            self.PAGE_W - self.MARGIN, 18,
            f'Page {doc.page} | {datetime.now().strftime("%Y-%m-%d")}'
        )
        
        canvas.restoreState()
    
    def generate_weekly_report(self):
        """Generate the weekly PDF report."""
        # Create reports directory if it doesn't exist
        reports_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'reports')
        os.makedirs(reports_dir, exist_ok=True)
        
        # Generate filename
        filename = f"Forex_Signal_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
        filepath = os.path.join(reports_dir, filename)
        
        # Create document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            leftMargin=self.MARGIN,
            rightMargin=self.MARGIN,
            topMargin=self.MARGIN,
            bottomMargin=self.MARGIN,
        )
        
        # Build content
        story = []
        
        # Cover page (handled by onFirstPage)
        story.append(PageBreak())
        
        # Page 2: Market Overview
        story.append(self._create_section_header('MARKET OVERVIEW'))
        story.append(Spacer(1, 8))
        
        overview_data = [
            ['TOPIC', 'DETAIL'],
            ['Report Period', f"{datetime.now().strftime('%B %d, %Y')} Weekly Analysis"],
            ['Instruments', '12 Currency Pairs + 2 Metals'],
            ['Analysis Type', 'Technical + COT Institutional Positioning'],
            ['Signal Focus', 'SHORT (SELL) Opportunities'],
            ['Risk Level', '1-2% per trade recommended'],
        ]
        story.append(self._create_data_table(overview_data, [0.25, 0.75]))
        story.append(Spacer(1, 14))
        
        # Page 3: COT Positioning
        story.append(self._create_section_header('COT INSTITUTIONAL POSITIONING'))
        story.append(Spacer(1, 8))
        
        story.append(Paragraph(
            'Commitment of Traders (COT) data shows institutional positioning. '
            'Bearish bias indicates large speculators are net short.',
            self.styles['BodyText']
        ))
        story.append(Spacer(1, 8))
        
        # Get COT data
        cot_table_data = [['PAIR', 'NC LONG', 'NC SHORT', 'NET POS', 'WK CHG', 'COMM NET', 'COT BIAS']]
        
        pairs = CurrencyPair.query.filter_by(is_active=True).all()
        for pair in pairs:
            cot = COTData.query.filter_by(pair_id=pair.id).order_by(COTData.report_date.desc()).first()
            if cot:
                cot_table_data.append([
                    pair.symbol,
                    f"{cot.nc_long:,}" if cot.nc_long else '-',
                    f"{cot.nc_short:,}" if cot.nc_short else '-',
                    f"{cot.nc_net:,}" if cot.nc_net else '-',
                    f"{cot.nc_net_change:+,}" if cot.nc_net_change else '-',
                    f"{cot.comm_net:,}" if cot.comm_net else '-',
                    cot.cot_bias or '-',
                ])
        
        story.append(self._create_data_table(
            cot_table_data,
            [0.15, 0.13, 0.13, 0.13, 0.13, 0.13, 0.20]
        ))
        story.append(Spacer(1, 14))
        
        # Page 4: Signal Scoring
        story.append(PageBreak())
        story.append(self._create_section_header('SIGNAL SCORING SUMMARY'))
        story.append(Spacer(1, 8))
        
        # Scoring legend
        legend_data = [
            ['CRITERIA', 'POINTS'],
            ['COT Net Position bearish', '+2'],
            ['RSI overbought (>65) or oversold (<35)', '+2'],
            ['MACD bearish crossover', '+1'],
            ['Price below 50 EMA', '+1'],
            ['Price below 200 EMA', '+1'],
            ['Technical consensus = SELL', '+1'],
            ['Price near resistance (within 0.3%)', '+1'],
            ['Weekly downtrend confirmed', '+1'],
        ]
        story.append(self._create_data_table(legend_data, [0.7, 0.3]))
        story.append(Spacer(1, 14))
        
        # Signals table
        signals = Signal.query.filter_by(status='active').order_by(Signal.score.desc()).all()
        
        signals_data = [['#', 'PAIR', 'PRICE', 'SCORE', 'RSI', 'MACD', 'MA SIG', 'COT', 'CONF', 'ACTION']]
        for i, signal in enumerate(signals, 1):
            pair = CurrencyPair.query.get(signal.pair_id)
            price_data = PriceData.query.filter_by(pair_id=signal.pair_id).order_by(PriceData.timestamp.desc()).first()
            
            signals_data.append([
                str(i),
                pair.symbol if pair else '-',
                f"{signal.entry_price:.5f}" if signal.entry_price and signal.entry_price < 10 else f"{signal.entry_price:.2f}" if signal.entry_price else '-',
                f"{signal.score}/10",
                f"{price_data.rsi_14:.1f}" if price_data and price_data.rsi_14 else '-',
                'Bear' if price_data and price_data.macd_histogram and price_data.macd_histogram < 0 else 'Bull',
                price_data.ma_consensus[:4] if price_data and price_data.ma_consensus else '-',
                signal.score_breakdown.get('cot_bearish', {}).get('met', False) if signal.score_breakdown else '-',
                signal.confidence[:3] if signal.confidence else '-',
                signal.direction,
            ])
        
        story.append(self._create_data_table(
            signals_data,
            [0.05, 0.12, 0.12, 0.09, 0.08, 0.08, 0.10, 0.08, 0.08, 0.10]
        ))
        story.append(Spacer(1, 14))
        
        # Page 5-6: Individual Signals
        story.append(PageBreak())
        story.append(self._create_section_header('TOP SIGNAL DETAILS'))
        story.append(Spacer(1, 8))
        
        top_signals = Signal.query.filter_by(status='active').order_by(Signal.score.desc()).limit(5).all()
        
        for i, signal in enumerate(top_signals, 1):
            pair = CurrencyPair.query.get(signal.pair_id)
            
            # Signal header
            header_data = [[
                f"#{i} {pair.symbol if pair else 'Unknown'}",
                f"Score: {signal.score}/10 | Confidence: {signal.confidence}"
            ]]
            header_table = Table(header_data, colWidths=[0.3 * self.TW, 0.7 * self.TW])
            header_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, 0), self.RED if signal.direction == 'SELL' else self.GREEN),
                ('BACKGROUND', (1, 0), (1, 0), self.NAVY),
                ('TEXTCOLOR', (0, 0), (-1, -1), self.WHITE),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (0, 0), 14),
                ('FONTSIZE', (1, 0), (1, 0), 11),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ]))
            story.append(header_table)
            story.append(Spacer(1, 6))
            
            # Trade levels
            levels_data = [
                ['PARAMETER', 'VALUE', 'NOTES'],
                ['Entry Price', f"{signal.entry_price:.5f}" if signal.entry_price and signal.entry_price < 10 else f"{signal.entry_price:.2f}" if signal.entry_price else '-', 'Market or limit order'],
                ['Stop Loss', f"{signal.stop_loss:.5f}" if signal.stop_loss and signal.stop_loss < 10 else f"{signal.stop_loss:.2f}" if signal.stop_loss else '-', 'Above resistance'],
                ['Take Profit 1', f"{signal.take_profit_1:.5f}" if signal.take_profit_1 and signal.take_profit_1 < 10 else f"{signal.take_profit_1:.2f}" if signal.take_profit_1 else '-', 'Conservative target'],
                ['Take Profit 2', f"{signal.take_profit_2:.5f}" if signal.take_profit_2 and signal.take_profit_2 < 10 else f"{signal.take_profit_2:.2f}" if signal.take_profit_2 else '-', 'Aggressive target'],
                ['Risk:Reward', f"1:{signal.risk_reward_ratio:.1f}" if signal.risk_reward_ratio else '-', 'Minimum 1:1.5 recommended'],
                ['Timeframe', signal.timeframe or 'H4', 'Entry timeframe'],
                ['Duration', signal.estimated_duration or '3-5 days', 'Estimated hold time'],
            ]
            story.append(self._create_data_table(levels_data, [0.25, 0.30, 0.45]))
            story.append(Spacer(1, 6))
            
            # Analysis
            if signal.analysis:
                story.append(Paragraph(
                    f"<b>Analysis:</b> {signal.analysis}",
                    self.styles['BodyText']
                ))
            
            story.append(Spacer(1, 12))
            
            # Gold divider
            story.append(HRFlowable(
                width='100%',
                thickness=1,
                color=self.GOLD,
                spaceAfter=12
            ))
        
        # Page 7: Risk Disclaimer
        story.append(PageBreak())
        story.append(self._create_section_header('RISK DISCLAIMER'))
        story.append(Spacer(1, 8))
        
        disclaimer_sections = [
            ('Trading Risk', 'Forex and CFD trading involves substantial risk of loss and is not suitable for all investors. You should carefully consider your investment objectives, level of experience, and risk appetite before trading.'),
            ('No Guarantee', 'Past performance is not indicative of future results. The signals provided are based on technical and fundamental analysis but do not guarantee profits.'),
            ('Not Financial Advice', 'This report is for informational purposes only and should not be considered as financial advice. Always consult with a qualified financial advisor before making trading decisions.'),
            ('Data Sources', 'Technical data is derived from public market sources. COT data is from CFTC reports. While we strive for accuracy, we cannot guarantee the completeness or timeliness of all data.'),
            ('Your Responsibility', 'You are solely responsible for your trading decisions. Never risk more than you can afford to lose. Use proper risk management including stop losses on all trades.'),
        ]
        
        for title, text in disclaimer_sections:
            story.append(Paragraph(f"<b>{title}</b>", self.styles['BodyText']))
            story.append(Spacer(1, 4))
            story.append(Paragraph(text, self.styles['SmallItalic']))
            story.append(Spacer(1, 10))
        
        # Build PDF
        doc.build(
            story,
            onFirstPage=self._draw_cover_page,
            onLaterPages=self._add_page_footer
        )
        
        # Save report record
        report = Report(
            filename=filename,
            report_type='weekly',
            period_start=datetime.now().date(),
            period_end=(datetime.now() + timedelta(days=7)).date(),
            file_path=filepath,
            signals_count=len(signals),
            top_signals=[s.to_dict() for s in top_signals[:3]],
        )
        db.session.add(report)
        db.session.commit()
        
        return filepath
