import pandas as pd
import yfinance as yf
import mplfinance as mpf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io

def generate_nifty_report_pdf(pdf_filename="Nifty_Report_Plain.pdf"):
    """
    Generates a PDF market report for Nifty 50 containing:
    1. Key Technical Levels (Close, SMA, Support, Resistance)
    2. A Candlestick Chart (embedded image)
    """
    print("Generating Nifty 50 PDF Report...")

    # --- 1. Fetch & Process Data ---
    ticker = "^NSEI"
    try:
        # Get historical data (6 months)
        data = yf.download(ticker, period="6mo", interval="1d", auto_adjust=True)
        
        # --- THE FIX IS HERE ---
        # Check if columns are MultiIndex (tuples) and flatten them
        if isinstance(data.columns, pd.MultiIndex):
            # Keep only the top level name (e.g., 'Close', 'Open', etc.)
            data.columns = [col[0] for col in data.columns]
        # -----------------------

        if data.empty:
            print("Failed to fetch data."); return False

        # Calculate Indicators
        data['SMA_50'] = data['Close'].rolling(window=50).mean()
        data['SMA_200'] = data['Close'].rolling(window=200).mean()
        
        # Simple Support & Resistance (Min/Max of last 20 days)
        support_level = data['Low'].tail(20).min()
        resistance_level = data['High'].tail(20).max()
        
        latest_close = data['Close'].iloc[-1]
        
    except Exception as e:
        print(f"Error processing data: {e}"); return False

    # --- 2. Create Chart using mplfinance ---
    chart_buffer = io.BytesIO()
    
    # Custom style
    mc = mpf.make_marketcolors(up='g', down='r', inherit=True)
    style = mpf.make_mpf_style(marketcolors=mc)
    
    mpf.plot(data.tail(60), type='candle', style=style, 
             title="Nifty 50 (Last 60 Days)",
             ylabel="Price",
             savefig=chart_buffer)
    
    chart_buffer.seek(0) # Reset buffer pointer

    # --- 3. Create PDF Report ---
    c = canvas.Canvas(pdf_filename, pagesize=letter)
    width, height = letter
    
    # Header
    c.setFont("Helvetica-Bold", 20)
    c.drawCentredString(width / 2, height - 50, "Nifty 50 Market Analysis")
    
    # Snapshot Section
    c.setFont("Helvetica", 12)
    text_y = height - 100
    line_height = 20
    
    c.drawString(50, text_y, f"Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}")
    text_y -= line_height
    c.drawString(50, text_y, f"Latest Close: {latest_close:,.2f}")
    text_y -= line_height * 2 # Add some space

    # Technical Levels
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, text_y, "Key Technical Levels:")
    text_y -= line_height
    
    c.setFont("Helvetica", 12)
    c.drawString(70, text_y, f"Resistance (20d High): {resistance_level:,.2f}")
    text_y -= line_height
    c.drawString(70, text_y, f"Support (20d Low): {support_level:,.2f}")
    text_y -= line_height
    c.drawString(70, text_y, f"50-Day SMA: {data['SMA_50'].iloc[-1]:,.2f}")
    text_y -= line_height
    c.drawString(70, text_y, f"200-Day SMA: {data['SMA_200'].iloc[-1]:,.2f}")
    
    # Embed the Chart
    # Use ImageReader to read the bytes buffer
    c.drawImage(ImageReader(chart_buffer), 50, height - 500, width=500, height=300)
    
    c.save()
    print(f"Report saved as {pdf_filename}")
    return True

# --- Main Execution ---
if __name__ == "__main__":
    generate_nifty_report_pdf()
