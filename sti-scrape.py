'''
Program to pull auction data from BringaTrailer.com
and export to excel for easy analysis

Created by Tropskee on 9/16/2021
Est. Completion Time: 2 hours
'''

from bs4 import BeautifulSoup
import requests
import re


base_URL = "https://bringatrailer.com/listing/"
# Years you are interested in
model_year = [2004, 2005, 2006, 2007]
# Prefix BaT uses for your model
model = "-subaru-impreza-wrx-sti-"
# ex_URL = "https://bringatrailer.com/listing/2006-subaru-impreza-wrx-sti-24/"
# ex_URL = base_URL+str(model_year[2])+model+str(24)+"/"

# Holds each cars data in it's own array
car_array = []

# BaT uses a number system for each model/year
# We simply loop through 0-100 to find all the auctions
# Could make this 500 if need be, but will increase time
for year in model_year:
    for i in range(100):
        car = []
        car_price_str = ""
        sold = ""
        sold_bool = False
        # The first auction of any model/year does not have a number suffix
        if i == 0:
            URL = base_URL+str(year)+model+"/"
        else:
            URL = base_URL+str(year)+model+str(i)+"/"
        print(URL)
        try:
            page = requests.get(URL)
        except requests.exceptions.RequestException as e:  # This is the correct syntax
            continue

        # Pull html data
        soup = BeautifulSoup(page.content, 'html.parser')

        try:
            # Get Date of sale
            get_date = soup.find_all('span', class_ = "data-value")
            sold_date = get_date[1].text
            car.append(sold_date)

            # Sold means it sold to the high bidder, bid to means it didnt sell
            # Or failed to reach reserve
            for bid in soup.find("span", class_ = "data-label"):
                sold = bid
                if "Sold" in sold or "sold" in sold:
                    car.append("Sold")
                    sold_bool = True
                else:
                    car.append("Not Sold")

            # Get Price
            if sold_bool:
                for price in soup.find(class_ = "data-value price"):
                    car_price_str = re.findall('[0-9]+,[0-9]+', price)
                    car.append(int(car_price_str[0].replace(",","")))
            else:
                for price in soup.find(class_ = "data-value"):
                    car_price_str = re.findall('[0-9]+,[0-9]+', price)
                    car.append(int(car_price_str[0].replace(",","")))

            # Get VIN
            for vin in soup.find("ul",class_="listing-essentials-items").find_all("li")[3]:
                car.append(vin)

            # Get Miles
            for miles in soup.find("ul",class_="listing-essentials-items").find_all("li")[4]:
                car.append(miles)

            # Get Year and insert first in array
            car.insert(0,year)
            # Add car array to car_array which holds all cars
            car_array.append(car)
            print(car)
        
        except:
            continue

    # print(car_array)

import pandas as pd

# convert your array into a dataframe
df = pd.DataFrame(car_array)

# save to xlsx file

filepath = 'sti_prices.xlsx'

df.to_excel(filepath, index=False)