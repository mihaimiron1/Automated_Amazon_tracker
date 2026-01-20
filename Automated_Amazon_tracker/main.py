from bs4 import BeautifulSoup
import requests
import smtplib
import os
from dotenv import load_dotenv

load_dotenv()

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/84.0.4147.125 Safari/537.36",
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8"
}

url = "https://www.amazon.com/Lenovo-Legion-Gaming-2560x1600-Shutter/dp/B0FMBTDX9L?th=1"
resp = requests.get(url, headers=headers, timeout=20)
print("status:", resp.status_code)

soup = BeautifulSoup(resp.text, "html.parser")

core = soup.select_one("#corePriceDisplay_desktop_feature_div") or soup.select_one("#corePrice_feature_div")
whole = core.select_one("span.a-price-whole") if core else None
frac  = core.select_one("span.a-price-fraction") if core else None

price = None
if whole and frac:
    w = whole.get_text(strip=True).replace(",", "").replace(".", "")
    f = frac.get_text(strip=True)
    price = float(f"{w}.{f}")
    print("Price:", price)
else:
    print("Nu am găsit prețul.")

title_el = soup.find(id="productTitle")
title = title_el.get_text(strip=True) if title_el else "(Titlu negăsit)"
print("Title:", title)

BUY_PRICE = 1900

if price is not None and price < BUY_PRICE:
    message = f"{title} is on sale for {price}!"
    try:
        with smtplib.SMTP(os.environ["SMTP_ADDRESS"], 587) as connection:
            connection.set_debuglevel(1)  # vezi conversația SMTP în consolă
            connection.starttls()
            connection.login(os.environ["EMAIL_ADDRESS"], os.environ["EMAIL_PASSWORD"])
            connection.sendmail(
                from_addr=os.environ["EMAIL_ADDRESS"],
                to_addrs=os.environ["EMAIL_ADDRESS"],
                msg=f"Subject:Amazon Price Alert!\n\n{message}\n{url}".encode("utf-8")
            )
        print("Email trimis!")
    except Exception as e:
        print("Eroare trimitere email:", repr(e))
else:
    print("Nu trimit email (price None sau nu e sub BUY_PRICE).")
