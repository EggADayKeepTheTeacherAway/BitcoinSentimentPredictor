import requests
import datetime
import csv

coin_id = "bitcoin"
vs_currency = "usd"
days = "30"  # gets the last 30 days of data.
url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency={vs_currency}&days={days}"

response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    prices = data["prices"]

    csv_data = [["Date", "Price (USD)"]]  # Header row for CSV
    for timestamp, price in prices:
        date = datetime.datetime.fromtimestamp(timestamp / 1000)  # convert milliseconds to seconds
        csv_data.append([date, price])

    # Write data to CSV file
    with open("bitcoin_prices.csv", "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)

    print("Bitcoin prices written to bitcoin_prices.csv")

else:
    print(f"Error: {response.status_code}")