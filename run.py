from flask import Flask, render_template, request
app = Flask(__name__)
import requests
from bs4 import BeautifulSoup

class item():
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount

@app.route("/")
def currency():
    currency = request.args.get("currency_list")
    am = request.args.get("amount")
    amount = 0.00
    if am != None:
        amount = "{:.2f}".format(float(am))

    # build and get the import_currency
    def build_currency(line):
        currency = line[0] + line[1] + line[2]
        return currency

    # crawl the current exchange rate from "finanzen.ch/devisen" and save it in the file "currency.txt"
    def rate_crawler():
        currency_list = ["CHF", "EUR", "USD", "JPY", "GBP"]
        for i in range(0, len(currency_list)):
            url = "https://www.finanzen.ch/devisen/" + currency_list[i]
            print(url)
            r = requests.get(url)
            doc = BeautifulSoup(r.text, "html.parser")

            for line in doc.select(".table" ".table-small" ".tableAltColor" ".no-margin-bottom tr"):
                if line.select_one("a") == None:
                    continue
                else:
                    import_currency = build_currency(line.select_one("a").text)
                    if import_currency == currency_list[i]:
                        currency_short = currency_list[i] + "/" + line.select_one("a").text.split(currency_list[i], 1)[1]
                        description = line.select_one("a").attrs["title"]
                        exchange_rate = float(line.select(".text-right")[1].text)
                        rate = float(line.select(".text-right")[2].text.replace("’", ""))
                        land = line.select("td")[1].text.replace(",", " ")
                        rate_date = line.select(".text-right")[3].text
                        if "\n" in land:
                            continue
                        else:
                            with open("currency.txt", "a", newline="") as file:
                                file.write(currency_short + ";" + land + ";" + description + ";" + str(exchange_rate) + ";" + str(rate) + ";" + rate_date + "\n")

    # Check if we already have the current exchange rate in the file. So we crawl the rates just once.
    def check_file():
        dict = {}
        if currency == None:
            wfile = open("currency.txt", "w")
            wfile.write("")
            wfile.close()
            rate_crawler()
            with open("currency.txt", "r") as file:
                for line in file:
                    stripped = line.strip().split(";")
                    dict[stripped[0]] = (stripped[1], stripped[2], float(stripped[3]), float(stripped[4]), stripped[5])
                print(dict)
        else:
            with open("currency.txt", "r") as file:
                for line in file:
                    stripped = line.strip().split(";")
                    dict[stripped[0]] = (stripped[1], stripped[2], float(stripped[3]), float(stripped[4]), stripped[5])
        return dict

    currency_dict = check_file()

    # create the dict for the view
    result_dict = {}
    for item in currency_dict.items():
        if currency == item[0].split("/")[0]:
            fcurrency = item[0]
            description = item[1][1]
            rate = float(item[1][3])
            result = float(amount) * rate
            rate_date = item[1][4]
            result_dict[fcurrency] = (description, round(result, 4), rate_date)
        else:
            continue

    return render_template("currency.html", result_dict=result_dict, currency=currency, amount=amount)
