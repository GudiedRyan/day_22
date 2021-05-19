import os
import requests
import smtplib

email_add = "yesmanvong@gmail.com"
password = os.environ["yesmanvongpass"]

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"

stock_key = os.environ["AV_key"]
news_key = os.environ["news_api_key"]

stock_params = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "apikey": stock_key
}

news_params = {
    "q": COMPANY_NAME,
    "apikey": news_key
}
global message

message = ""

def stock_changes():
    global message
    stock_response = requests.get(url=STOCK_ENDPOINT, params=stock_params)
    stock_response.raise_for_status()
    stock_data = stock_response.json()["Time Series (Daily)"]

    prices = [close for (date,close) in stock_data.items()]
    yesterday = float(prices[0]["4. close"])
    day_before = float(prices[1]["4. close"])

    change = abs(day_before - yesterday)/day_before
    change = round(change,3)
    change *= 100

    if change > 5:
        if day_before - yesterday >= 0:
            articles = get_news()
            message = generate_message(articles, direction="positive", change=change)
            email()
            
        else:
            articles = get_news()
            message = generate_message(articles, direction="negative", change=change)
            email()

    else:
        if day_before - yesterday >= 0:
            message = f"Subject: Stock Update\nThere was a {change}% increase."
            email()
            
        else:
            message = f"Subject: Stock Update\nThere was a {change}% decrease."
            email()



def get_news():
    news_response = requests.get(url=NEWS_ENDPOINT, params=news_params)
    news_response.raise_for_status()
    news_data = news_response.json()
    top_three = news_data["articles"][:3]
    headlines = []
    for article in top_three:
        headlines.append((article["title"], article["description"], article["url"]))
    return headlines

def generate_message(articles, direction, change):
    article_messages = [f"Title: {article[0]}\nBrief: {article[1]}\nURL: {article[2]}" for article in articles]
    subject = ""
    if direction == "positive":
        subject = "Increase"
    else:
        subject = "Decrease"
    email_message = f"Subject: TSLA: {subject} {change}%\n\n{article_messages[0]}\n{article_messages[1]}\n{article_messages[2]}"
    return email_message


def email():
    with smtplib.SMTP("smtp.gmail.com", port=587) as connection:
        connection.starttls()
        connection.login(user=email_add, password=password)
        connection.sendmail(
            from_addr=email_add,
            to_addrs="gudiedryan@gmail.com",
            msg=message
        )

stock_changes()