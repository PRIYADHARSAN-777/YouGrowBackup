import pandas as pd
from nsepython import *
from datetime import datetime
import os
import time
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager

def get_pcr_data(csv_filename="nifty_pcr_data.csv"):
    """
    Fetches the latest NIFTY PCR (Put Call Ratio) and updates a local CSV file.
    
    Returns:
        float: The latest PCR value, or None if fetching fails.
    """
    try:
        # Fetch Option Chain Data using nsepython
        oi_data = nse_optionchain_scrapper('NIFTY')
        
        # Calculate Total PE and CE Open Interest
        current_pe = oi_data["filtered"]["PE"]["totOI"]
        current_ce = oi_data["filtered"]["CE"]["totOI"]
        
        # Calculate PCR
        pcr = round(current_pe / current_ce, 3)
        
        # Get Current Date and Time
        now = datetime.now()
        current_date = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M:%S")
        
        print(f"Fetched NIFTY PCR: {pcr} at {current_time}")
        
        # --- Update CSV History ---
        # Check if file exists to determine if we need a header
        file_exists = os.path.isfile(csv_filename)
        
        # Open in append mode
        with open(csv_filename, 'a') as f:
            if not file_exists:
                f.write("Date,Time,PCR\n") # Write header
            f.write(f"{current_date},{current_time},{pcr}\n")
            
        return pcr

    except Exception as e:
        print(f"Error fetching PCR data: {e}")
        return None

def get_pcr_trend_chart(output_filename="pcr_trend_chart.png"):
    """
    Scrapes a pre-built PCR chart from a website (e.g., Upstox or sensible)
    since plotting a single point isn't very useful without historical context.
    For this example, we'll try to get a snapshot from a public analysis page.
    """
    print("Fetching PCR Trend Chart...")
    
    driver = None
    try:
        # Setup headless browser
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")
        
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Example URL (Upstox Nifty OI Analysis often shows PCR)
        url = "https://upstox.com/fno-discovery/put-call-ratio/nifty-pcr/"
        driver.get(url)
        time.sleep(5) # Allow chart to load
        
        # Find the chart element (adjust selector based on actual site structure)
        # Using a generic full-screenshot approach for robustness in this example
        driver.save_screenshot("temp_pcr_page.png")
        
        # Crop the image (Approximate coordinates for the main content area)
        img = Image.open("temp_pcr_page.png")
        # Crop: Left, Top, Right, Bottom
        # Adjust these values based on the website layout
        cropped_img = img.crop((100, 200, 1800, 900)) 
        cropped_img.save(output_filename)
        
        os.remove("temp_pcr_page.png")
        print(f"Chart saved to {output_filename}")
        return True
        
    except Exception as e:
        print(f"Error capturing chart: {e}")
        return False
    finally:
        if driver:
            driver.quit()

def main():
    print("--- NIFTY PCR Analysis ---")
    
    # 1. Get Live PCR
    current_pcr = get_pcr_data()
    
    # 2. Analyze Sentiment
    sentiment = "Neutral"
    if current_pcr:
        if current_pcr > 1.2:
            sentiment = "Bullish"
        elif current_pcr < 0.8:
            sentiment = "Bearish"
        
        print(f"Current Sentiment based on PCR: {sentiment}")
    
    # 3. Get Chart
    get_pcr_trend_chart()
    
    # 4. Show Historical Context (Optional)
    if os.path.exists("nifty_pcr_data.csv"):
        df = pd.read_csv("nifty_pcr_data.csv")
        print("\nRecent PCR History:")
        print(df.tail(5)) # Show last 5 entries

if __name__ == "__main__":
    main()
