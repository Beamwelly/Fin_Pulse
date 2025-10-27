
from flask import Flask, render_template, request, jsonify, session
import yfinance as yf
import requests
from datetime import datetime, timedelta
from sentiment import analyze_sentiment  # Ensure this is implemented
import requests  # For OpenRouter calls
from dotenv import load_dotenv
import os
load_dotenv()
app = Flask(__name__)
app.secret_key = "your_secsk-or-v1-6915d651b953be52d2f7aeec2234ee8f18b5ba491057bb99cf33df55b09585c0ret_key_here"  # Change this to a secure secret key

# 🔑 OpenRouter setup
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY") 
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

NEWS_API_KEY = "df973ccce0ea4cb480af696121d92176"

SECTOR_KEYWORDS = {
    "Information Technology (IT)": "technology",
    "Healthcare & Pharmaceuticals": "healthcare OR pharmaceuticals",
    "Banking & Financial Services": "banking OR finance",
    "Infrastructure & Capital Goods": "infrastructure OR capital goods",
    "Fast-Moving Consumer Goods (FMCG)": "FMCG OR consumer goods",
    "Real Estate": "real estate",
    "Auto & Auto Ancillaries": "automobile OR auto ancillary",
    "Renewable Energy": "renewable energy OR green energy",
    "Railways & Logistics": "railways OR logistics",
    "Specialty Chemicals": "specialty chemicals"
}

NIFTY_50 = [
    "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", "ASIANPAINT.NS", "AXISBANK.NS",
    "BAJAJ-AUTO.NS", "BAJAJFINSV.NS", "BAJFINANCE.NS", "BHARTIARTL.NS", "BPCL.NS",
    "BRITANNIA.NS", "CIPLA.NS", "COALINDIA.NS", "DIVISLAB.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "GRASIM.NS", "HCLTECH.NS", "HDFCBANK.NS", "HDFCLIFE.NS",
    "HEROMOTOCO.NS", "HINDALCO.NS", "HINDUNILVR.NS", "ICICIBANK.NS", "INDUSINDBK.NS",
    "INFY.NS", "IOC.NS", "ITC.NS", "JSWSTEEL.NS", "KOTAKBANK.NS",
    "LT.NS", "M&M.NS", "MARUTI.NS", "NESTLEIND.NS", "NTPC.NS",
    "ONGC.NS", "POWERGRID.NS", "RELIANCE.NS", "SBILIFE.NS", "SBIN.NS",
    "SUNPHARMA.NS", "TATACONSUM.NS", "TATAMOTORS.NS", "TATASTEEL.NS", "TCS.NS",
    "TECHM.NS", "TITAN.NS", "ULTRACEMCO.NS", "UPL.NS", "WIPRO.NS"
]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/stocks', methods=['GET', 'POST'])
def stocks():
    selected_tickers = request.form.getlist('ticker') or ["RELIANCE.NS"]
    selected_months = request.form.get('months', '6')
    stocks_data = []
    infos = {}

    period = f"{selected_months}mo"

    for ticker in selected_tickers:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period).reset_index()
        hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
        stocks_data.append({'ticker': ticker, 'data': hist.to_dict('records')})
        infos[ticker] = stock.info

    return render_template('stocks.html',
                           selected_tickers=selected_tickers,
                           selected_months=selected_months,
                           stocks_data=stocks_data,
                           infos=infos,
                           companies=NIFTY_50)

@app.route('/news')
def news():
    selected_sector = request.args.get("sector", "Information Technology (IT)")
    selected_days = request.args.get("days", "7")
    query = SECTOR_KEYWORDS.get(selected_sector, "technology")

    try:
        today = datetime.now()
        from_date = (today - timedelta(days=int(selected_days))).strftime('%Y-%m-%d')
        to_date = today.strftime('%Y-%m-%d')

        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={query}&from={from_date}&to={to_date}&language=en&"
            f"pageSize=10&sortBy=relevancy&apiKey={NEWS_API_KEY}"
        )

        response = requests.get(url)
        data = response.json()
        articles = data.get("articles", [])[:10]
        news_items = []

        for item in articles:
            title = item.get("title", "")
            desc = item.get("description", "")
            content = f"{title}. {desc}"
            polarity, sentiment = analyze_sentiment(content)
            item["polarity"] = round(polarity, 2)
            item["sentiment"] = sentiment
            item["source"] = item.get("source", {}).get("name", "Unknown")
            news_items.append(item)

    except Exception as e:
        print("Error fetching news:", e)
        news_items = []

    return render_template(
        "news.html",
        news_items=news_items,
        selected_sector=selected_sector,
        selected_days=selected_days,
        sectors=list(SECTOR_KEYWORDS.keys())
    )

@app.route('/Visualisation', methods=['GET'])
def sector_visualization():
    selected_sector = request.args.get('sector', list(SECTOR_KEYWORDS.keys())[0])
    selected_days = request.args.get('days', '7')
    query = SECTOR_KEYWORDS.get(selected_sector, "business")

    try:
        today = datetime.now()
        from_date = (today - timedelta(days=int(selected_days))).strftime('%Y-%m-%d')
        to_date = today.strftime('%Y-%m-%d')

        url = (
            f"https://newsapi.org/v2/everything?"
            f"q={query}&from={from_date}&to={to_date}&language=en&"
            f"pageSize=10&sortBy=relevancy&apiKey={NEWS_API_KEY}"
        )

        response = requests.get(url)
        data = response.json()
        news_items = data.get("articles", [])[:10]

        article_titles = []
        article_sentiments = []
        article_urls = []

        for item in news_items:
            title = item.get("title", "")
            desc = item.get("description", "")
            url = item.get("url", "")
            content = f"{title}. {desc}"
            polarity, sentiment = analyze_sentiment(content)
            article_titles.append(title)
            article_sentiments.append(round(polarity, 3))
            article_urls.append(url)

    except Exception as e:
        print("Error fetching visualization news:", e)
        article_titles = []
        article_sentiments = []
        article_urls = []

    return render_template("visualisation.html",
                           sectors=SECTOR_KEYWORDS.keys(),
                           selected_sector=selected_sector,
                           selected_days=selected_days,
                           article_titles=article_titles,
                           article_sentiments=article_sentiments,
                           article_urls=article_urls)

@app.route('/chatbot')
def chatbot():
    return render_template('chatbot.html')

@app.route('/get_chat_response', methods=['POST'])
def get_chat_response():
    user_message = request.json.get("message")

    if 'history' not in session:
        session['history'] = []

    history = session['history'][-5:]

    messages = [
        {"role": "system", "content": "You are a helpful finance assistant. Greet users when they say hello or hi. Answer any questions related to stocks, finance, and investing in a simple, beginner-friendly way."}
    ]
    for h in history:
        messages.append({"role": "user", "content": h['user']})
        messages.append({"role": "assistant", "content": h['bot']})
    messages.append({"role": "user", "content": user_message})

    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "openai/gpt-3.5-turbo",  # 🔄 You can switch to other models available in OpenRouter
            "messages": messages
        }

        response = requests.post(OPENROUTER_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            return jsonify({"response": f"❌ API Error: HTTP {response.status_code} - {response.text}"})
        
        data = response.json()
        
        if "choices" not in data or not data["choices"]:
            return jsonify({"response": f"❌ API Error: Invalid response format - {data}"})

        bot_reply = data["choices"][0]["message"]["content"]
        session['history'].append({'user': user_message, 'bot': bot_reply})

        return jsonify({"response": bot_reply})

    except requests.exceptions.RequestException as e:
        return jsonify({"response": f"❌ Network Error: {str(e)}"})
    except KeyError as e:
        return jsonify({"response": f"❌ API Response Error: Missing key {str(e)}"})
    except Exception as e:
        return jsonify({"response": f"❌ Unexpected Error: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=True)
