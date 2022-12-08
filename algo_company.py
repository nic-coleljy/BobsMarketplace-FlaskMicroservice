from math import floor
import pdfplumber
from datetime import datetime
import urllib3
import io
from flask import Flask, jsonify, request

def open_pdf(url):
    http = urllib3.PoolManager()
    temp = io.BytesIO()
    temp.write(http.request("GET", url).data)
    try:    # to verify is the url has valid pdf file!
        pdf = pdfplumber.open(temp)
    except:
        pass
    return pdf



app = Flask(__name__)

@app.route("/")
def welcome():
    return "HELLO!"

@app.route("/api")
def api():
    pdf_url = request.args.get("file")
    #LIST OF ALL TEXTS & BASE CREDITWORTHINESS
    data = []
    creditworthiness = 100

    pdf = open_pdf(pdf_url)

    #OPEN PDF FILE & EXTRACT TEXT
    for page_num in range(0, len(pdf.pages)):
        page = pdf.pages[page_num]
        text = page.extract_text()
        temp_list = text.split("\n")
        for line in range(0, len(temp_list)):
            data.append(temp_list[line])

    #NAME CHANGE
    if data[data.index(" Former Name if any :") + 1] != " Incorporation Date. :":
        creditworthiness -= 5

    #COMPANY AGE
    commencement_date = datetime.strptime(data[data.index(" Incorporation Date. :") + 1], "%d/%m/%Y").date()
    company_age = floor(((datetime.now().date() - commencement_date).days)/365.2425)

    if company_age >= 25:
        creditworthiness += 10
    elif company_age < 5:
        creditworthiness -= 20
    elif company_age < 10:
        creditworthiness -= 10
    elif company_age < 25:
        creditworthiness += 5

    #STATUS OF BUSINESS
    if data[data.index(" Status :") + 1] != "Live Company":
        creditworthiness = 0
        print("The Business is Not Live!")

    #TYPE OF BUSINESS
    business_type = data[data.index(" Company Type :") + 1]

    if business_type == "Sole-Proprietor":
        creditworthiness *= 0.5
    elif business_type == "LIMITED EXEMPT PRIVATE COMPANY":
        creditworthiness *= 0.75

    #CAPITAL
    capital = int("".join(words for words in data[data.index("Paid-Up Capital Number of Shares Currency Share Type") + 2] if words.isdigit()))
    if capital < 1000:
        creditworthiness -= 50
    elif capital < 10000:
        creditworthiness -= 25
    elif capital < 100000:
        creditworthiness -= 5


    #CREDITWORTHINESS LIMIT
    if creditworthiness > 100:
        creditworthiness = 100

    return jsonify({"creditworthiness": creditworthiness})

if __name__ == "__main__":
    app.run(debug=True)