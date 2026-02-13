import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import mplfinance as mpf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
import io
import os

def generate_nifty_report_with_slider(pdf_filename="Nifty_Report_Slider.pdf"):
    """
    Generates a PDF report for Nifty 50 with:
    1. A candlestick chart with support/resistance lines.
    2. Key levels (Support/Resistance).
    3. A "slider" graphic indicating current position relative to Day's Range.
    """
    print("Generating Nifty 50 Report with Slider...")

    # --- 1. Fetch Data ---
    ticker = "^NSEI"
    try:
        # Get historical data for chart (3 months)
        data = yf.download(ticker, period="3mo", interval="1d", auto_adjust=True)
        
        # Get intraday data for current price and range (1 day)
        today_data = yf.download(ticker, period="1d", interval="5m", auto_adjust=True)
        
        if data.empty or today_data.empty:
            print("Failed to fetch data."); return False
            
        # --- THE FIX IS HERE: Handling Multi-Level Column Headers ---
        # yfinance often returns multi-level columns like ('Close', 'Nifty 50')
        # We flatten them to simple strings like 'Close'
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = [col[0] for col in data.columns]
        
        if isinstance(today_data.columns, pd.MultiIndex):
            today_data.columns = [col[0] for col in today_data.columns]
        # -----------------------------------------------------------

        current_price = today_data['Close'].iloc[-1]
        day_high = today_data['High'].max()
        day_low = today_data['Low'].min()
        
        # Calculate moving averages
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()

        # Identify Support & Resistance (Simple approach)
        # Using recent lows and highs as proxies
        recent_low = data['Low'].tail(20).min()
        recent_high = data['High'].tail(20).max()
        
        support_level = recent_low
        resistance_level = recent_high

    except Exception as e:
        print(f"Error fetching/processing data: {e}"); return False

    # --- 2. Create Candlestick Chart ---
    chart_buffer = io.BytesIO()
    
    # Custom style for the chart
    mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
    s = mpf.make_mpf_style(marketcolors=mc)
    
    # Add horizontal lines for support and resistance
    hlines = dict(hlines=[support_level, resistance_level], colors=['g', 'r'], linestyle='-.')

    mpf.plot(data, type='candle', style=s, 
             title=f"Nifty 50 - 3 Month Trend\nSupport: {support_level:.0f} | Resistance: {resistance_level:.0f}",
             hlines=hlines,
             volume=False, savefig=chart_buffer)
    
    chart_buffer.seek(0)
    
    # --- 3. Create PDF Report ---
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width / 2, height - 50, "Nifty 50 Market Pulse")
    
    # Date
    c.setFont("Helvetica", 12)
    from datetime import datetime
    c.drawCentredString(width / 2, height - 70, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Summary Section
    c.setFont("Helvetica", 14)
    c.drawString(50, height - 120, f"Current Price: {current_price:,.2f}")
    c.drawString(50, height - 140, f"Day's Range: {day_low:,.2f} - {day_high:,.2f}")
    
    # --- Slider Graphic ---
    slider_y = height - 180
    slider_x_start = 50
    slider_width = 500
    slider_height = 20
    
    # Draw background bar (Day's Range)
    c.setFillColor(colors.lightgrey)
    c.rect(slider_x_start, slider_y, slider_width, slider_height, fill=1, stroke=0)
    
    # Calculate position of current price on the slider
    if day_high > day_low:
        percentage = (current_price - day_low) / (day_high - day_low)
        # Clamp percentage between 0 and 1
        percentage = max(0, min(1, percentage))
    else:
        percentage = 0.5 # Default to middle if range is 0

    marker_x = slider_x_start + (percentage * slider_width)
    
    # Draw marker (Current Price)
    c.setFillColor(colors.blue)
    c.circle(marker_x, slider_y + (slider_height / 2), 8, fill=1, stroke=0)
    
    # Labels for slider
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)
    c.drawString(slider_x_start, slider_y - 15, f"Low: {day_low:,.0f}")
    c.drawRightString(slider_x_start + slider_width, slider_y - 15, f"High: {day_high:,.0f}")
    c.drawCentredString(marker_x, slider_y + 25, f"Current: {current_price:,.0f}")

    # Embed Chart
    c.drawImage(ImageReader(chart_buffer), 50, height - 550, width=500, height=300)
    
    # Key Levels Table
    table_y = height - 600
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, table_y, "Key Technical Levels")
    
    c.setFont("Helvetica", 12)
    c.drawString(50, table_y - 25, f"Resistance (Recent High): {resistance_level:,.2f}")
    c.drawString(50, table_y - 45, f"Support (Recent Low): {support_level:,.2f}")
    c.drawString(50, table_y - 65, f"50-Day SMA: {data['SMA_50'].iloc[-1]:,.2f}")
    c.drawString(50, table_y - 85, f"200-Day SMA: {data['SMA_200'].iloc[-1]:,.2f}")

    c.save()
    print(f"PDF Report saved as {pdf_filename}")
    return True

# --- Main Execution ---
if __name__ == "__main__":
    generate_nifty_report_with_slider()
