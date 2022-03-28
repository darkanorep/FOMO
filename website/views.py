from flask import Blueprint, render_template, redirect, session, url_for, request, jsonify
import sqlite3, csv
import numpy as np
import pandas as pd
import yfinance as yf
import plotly.graph_objs as go
from plotly.subplots import  make_subplots
import json, plotly, requests, bs4
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
from datetime import datetime

import base64
from io import BytesIO

views = Blueprint('views', __name__)
auth = Blueprint('auth',__name__)


@views.route('/')
def index():

    return redirect(url_for("auth.login"))


@views.route('/assets/<symbol>')
def assetinfo(symbol):
    
    if "email" in session:

        con =sqlite3.connect('system.db')
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        date = datetime.now().strftime("%B %d, %Y")

        cur.execute("DELETE FROM ChartData where SYMBOL = '"+symbol+"';")
        con.commit()
        cur.execute("DELETE FROM Hour where SYMBOL = '"+symbol+"';")
        con.commit()

        cur.executemany("DELETE FROM Prediction where symbol=? and date=?", [(symbol, date)])
        con.commit()

        cur.execute("DELETE FROM Prediction where symbol=? and interval='1yr';", [symbol])
        cur.execute("DELETE FROM Prediction where symbol=? and interval='6mo';", [symbol])
        cur.execute("DELETE FROM Prediction where symbol=? and interval='3mo';", [symbol])
        cur.execute("DELETE FROM Prediction where symbol=? and interval='1mo';", [symbol])
        con.commit()


        data1yr = yf.download(tickers=''+symbol+'', period='1y', interval='1d')
        data1yr.to_csv('website/data/'+symbol+'1yr.csv')

        with open('website/data/'+symbol+'1yr.csv','r') as fin:
            df = pd.read_csv('website/data/'+symbol+'1yr.csv')
    
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
            df['prevClose'] = df['Adj Close'].shift(1)
            df['change'] = (df['Adj Close']-df['prevClose'])
            df['pchange'] = (df['Adj Close']/df['prevClose']) - 1
            df['finalpchange'] = (df['pchange'] * 100)
            df["interval"] = "1yr"

            fig = plt.figure()

            df = df.set_index(pd.DatetimeIndex(df['Date'].values))
            df['Numbers'] = list(range(0, len(df)))
            x = np.array(df[['Numbers']])
            y = df['Close'].values
            lin_model = LinearRegression().fit(x,y)
            y_pred = lin_model.coef_* x + lin_model.intercept_
            df['prePred'] = y_pred
            df['prePred'].plot(label="model")
            df['Close'].plot(label="price")
            plt.legend(loc="upper right")
            plt.title('1 Year '+symbol+' Close Price History and Prediction')
            fig.savefig('website/static/datavisual/'+symbol+'1yr.png')

            pred = lin_model.coef_* len(df)+1 + lin_model.intercept_
 
            df1 = pd.DataFrame(pred)
            df1["interval"] = "1yr"
            df1['r2score'] = r2_score(df['Close'], df['prePred'])
            df1.round(2).to_csv('website/data/'+symbol+'1yrpred.csv', index=False)

            df.round(2).to_csv(r'website/data/'+symbol+'1yr.csv', index=False)
            dr = csv.DictReader(fin)
            to_db = [(i['Date'], i['Open'], i['High'], i['Low'], i['Close'], i['Adj Close'], i['Volume'], i['change'], i['finalpchange'], i['interval']) for i in dr]
  
            cur.executemany("INSERT into ChartData (symbol, date, open, high, low, close, adj_close, volume, change, finalpchange, interval) values ('"+symbol+"',?, ?, ?, ?, ?, ?, ?,?,?,?);", to_db)
            con.commit()
        #--------------------------------------------------------------------
        data3mo = yf.download(tickers=''+symbol+'', period='3mo', interval='1d')
        data3mo.to_csv('website/data/'+symbol+'3mo.csv')

        with open('website/data/'+symbol+'3mo.csv','r') as fin:
            df = pd.read_csv('website/data/'+symbol+'3mo.csv')
    
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
            df['prevClose'] = df['Adj Close'].shift(1)
            df['change'] = (df['Adj Close']-df['prevClose'])
            df['pchange'] = (df['Adj Close']/df['prevClose']) - 1
            df['finalpchange'] = (df['pchange'] * 100)
            df["interval"] = "3mo"

            fig = plt.figure()
            #tmpfile = BytesIO()
            df = df.set_index(pd.DatetimeIndex(df['Date'].values))
            df['Numbers'] = list(range(0, len(df)))
            x = np.array(df[['Numbers']])
            y = df['Close'].values
            lin_model = LinearRegression().fit(x,y)
            y_pred = lin_model.coef_* x + lin_model.intercept_
            df['prePred'] = y_pred
            df['prePred'].plot(label="model")
            df['Close'].plot(label="price")
            plt.legend(loc="upper right")
            plt.title('3 Months '+symbol+' Close Price History and Prediction')
            #
            fig.savefig('website/static/datavisual/'+symbol+'3mo.png')
            #encoded = base64.b64encode(tmpfile.getvalue()).decode('utf-8')
            #html = 'Some html head' + '<img src=\'data:image/png;base64,{}\'>'.format(encoded) + 'Some more html'

            #with open('test.html','w') as f:
                #f.write(html)

            pred = lin_model.coef_* len(df)+1 + lin_model.intercept_
 
            df1 = pd.DataFrame(pred)
            df1["interval"] = "3mo"
            df1['r2score'] = r2_score(df['Close'], df['prePred'])
            df1.round(2).to_csv('website/data/'+symbol+'3mopred.csv', index=False)

            df.round(2).to_csv(r'website/data/'+symbol+'3mo.csv', index=False)
            dr = csv.DictReader(fin)
            to_db = [(i['Date'], i['Open'], i['High'], i['Low'], i['Close'], i['Adj Close'], i['Volume'], i['change'], i['finalpchange'], i['interval']) for i in dr]
  
            cur.executemany("INSERT into ChartData (symbol, date, open, high, low, close, adj_close, volume, change, finalpchange, interval) values ('"+symbol+"',?, ?, ?, ?, ?, ?, ?,?,?,?);", to_db)
            con.commit()
        
        #--------------------------------------------------------------------
        data30m = yf.download(tickers=''+symbol+'', period='1d', interval='30m')
        data30m.index = data30m.index.tz_localize(None)
        data30m.to_csv('website/data/'+symbol+'30min.csv')

        with open('website/data/'+symbol+'30min.csv','r') as fin:
            df = pd.read_csv('website/data/'+symbol+'30min.csv')
    
            df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
            df['prevClose'] = df['Adj Close'].shift(1)
            df['change'] = (df['Adj Close']-df['prevClose'])
            df['pchange'] = (df['Adj Close']/df['prevClose']) - 1
            df['finalpchange'] = (df['pchange'] * 100)
            df["interval"] = "30min"

            df.round(2).to_csv(r'website/data/'+symbol+'30min.csv', index=False)
            dr = csv.DictReader(fin)
            to_db = [(i['Datetime'], i['Open'], i['High'], i['Low'], i['Close'], i['Adj Close'], i['Volume'], i['change'], i['finalpchange'], i['interval']) for i in dr]
  
            cur.executemany("INSERT into ChartData (symbol, date, open, high, low, close, adj_close, volume, change, finalpchange, interval) values ('"+symbol+"',?, ?, ?, ?, ?, ?, ?,?,?,?);", to_db)
            con.commit()
        #--------------------------------------------------------------------
        data15m = yf.download(tickers=''+symbol+'', period='1d', interval='15m')
        data15m.index = data15m.index.tz_localize(None)
        data15m.to_csv('website/data/'+symbol+'15min.csv')

        with open('website/data/'+symbol+'15min.csv','r') as fin:
            df = pd.read_csv('website/data/'+symbol+'15min.csv')
    
            df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
            df['prevClose'] = df['Adj Close'].shift(1)
            df['change'] = (df['Adj Close']-df['prevClose'])
            df['pchange'] = (df['Adj Close']/df['prevClose']) - 1
            df['finalpchange'] = (df['pchange'] * 100)
            df["interval"] = "15min"

            df.round(2).to_csv(r'website/data/'+symbol+'15min.csv', index=False)
            dr = csv.DictReader(fin)
            to_db = [(i['Datetime'], i['Open'], i['High'], i['Low'], i['Close'], i['Adj Close'], i['Volume'], i['change'], i['finalpchange'], i['interval']) for i in dr]
  
            cur.executemany("INSERT into ChartData (symbol, date, open, high, low, close, adj_close, volume, change, finalpchange, interval) values ('"+symbol+"',?, ?, ?, ?, ?, ?, ?,?,?,?);", to_db)
            con.commit()

        #--------------------------------------------------------------------
        data1mo = yf.download(tickers=''+symbol+'', interval='1wk')
        data1mo.to_csv('website/data/'+symbol+'1wk.csv')

        with open('website/data/'+symbol+'1wk.csv','r') as fin:
            df = pd.read_csv('website/data/'+symbol+'1wk.csv')
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
            df['prevClose'] = df['Adj Close'].shift(1)
            df['change'] = (df['Adj Close']-df['prevClose'])
            df['pchange'] = (df['Adj Close']/df['prevClose']) - 1
            df['finalpchange'] = (df['pchange'] * 100)
            df["interval"] = "1wk"

            df.round(2).to_csv(r'website/data/'+symbol+'1wk.csv', index=False)
            dr = csv.DictReader(fin)

            to_db = [(i['Date'], i['Open'], i['High'], i['Low'], i['Close'], i['Adj Close'], i['Volume'], i['change'], i['finalpchange'], i['interval']) for i in dr]

            cur.executemany("INSERT into ChartData (symbol, date, open, high, low, close, adj_close, volume, change, finalpchange, interval) values ('"+symbol+"',?, ?, ?, ?, ?, ?, ?,?,?,?);", to_db)
            con.commit()
        #---------------------------------------------------------------------

        data1wk = yf.download(tickers=''+symbol+'', interval='1wk')
        data1wk.to_csv('website/data/'+symbol+'1wk.csv')

        with open('website/data/'+symbol+'1wk.csv','r') as fin:
            df = pd.read_csv('website/data/'+symbol+'1wk.csv')
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
            df['prevClose'] = df['Adj Close'].shift(1)
            df['change'] = (df['Adj Close']-df['prevClose'])
            df['pchange'] = (df['Adj Close']/df['prevClose']) - 1
            df['finalpchange'] = (df['pchange'] * 100)
            df["interval"] = "1wk"

            df.round(2).to_csv(r'website/data/'+symbol+'1wk.csv', index=False)
            dr = csv.DictReader(fin)

            to_db = [(i['Date'], i['Open'], i['High'], i['Low'], i['Close'], i['Adj Close'], i['Volume'], i['change'], i['finalpchange'], i['interval']) for i in dr]

            cur.executemany("INSERT into ChartData (symbol, date, open, high, low, close, adj_close, volume, change, finalpchange, interval) values ('"+symbol+"',?, ?, ?, ?, ?, ?, ?,?,?,?);", to_db)
            con.commit()

        #---------------------------------------------------------------------

        data1hr = yf.download(tickers=''+symbol+'', period='ytd', interval='1h')
        data1hr.index = data1hr.index.tz_localize(None)
        data1hr.to_csv('website/data/'+symbol+'1hr.csv')

        with open('website/data/'+symbol+'1hr.csv','r') as fin:
            df = pd.read_csv('website/data/'+symbol+'1hr.csv')
            df.columns.values[0] = 'Date'
            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
            df['prevClose'] = df['Adj Close'].shift(1)
            df['change'] = (df['Adj Close']-df['prevClose'])
            df['pchange'] = (df['Adj Close']/df['prevClose']) - 1
            df['finalpchange'] = (df['pchange'] * 100)
            df["interval"] = "1hr"

            df.round(2).to_csv(r'website/data/'+symbol+'1hr.csv', index=False)
            dr = csv.DictReader(fin)
            to_db = [(i['Date'], i['Open'], i['High'], i['Low'], i['Close'], i['Adj Close'], i['Volume'], i['change'], i['finalpchange'], i['interval']) for i in dr]

            cur.executemany("INSERT into ChartData (symbol, date, open, high, low, close, adj_close, volume, change, finalpchange, interval) values ('"+symbol+"',?, ?, ?, ?, ?, ?, ?,?,?,?);", to_db)
            con.commit()
        #---------------------------------------------------------------------

        data1 = yf.download(tickers=''+symbol+'', period='1d', interval='1m')
        data1.index = data1.index.tz_localize(None)
        data1.to_csv('website/data/'+symbol+'1min.csv')
      
        with open('website/data/'+symbol+'1min.csv','r') as fin:
            df = pd.read_csv('website/data/'+symbol+'1min.csv')
    
            df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
            df['prevClose'] = df['Adj Close'].shift(1)
            df['change'] = (df['Adj Close']-df['prevClose'])
            df['pchange'] = (df['Adj Close']/df['prevClose']) - 1
            df['finalpchange'] = (df['pchange'] * 100)
            df["interval"] = "1min"

            fig = plt.figure()
            df = df.set_index(pd.DatetimeIndex(df['Datetime'].values))
            df['Numbers'] = list(range(0, len(df)))
            x = np.array(df[['Numbers']])
            y = df['Close'].values
            lin_model = LinearRegression().fit(x,y)
            y_pred = lin_model.coef_* x + lin_model.intercept_
            df['prePred'] = y_pred
            df['prePred'].plot(label="model")
            df['Close'].plot(label="price")

            plt.legend(loc="upper right")
            plt.title('24 Hours '+symbol+' Close Price History and Prediction')
            #
            fig.savefig('website/static/datavisual/'+symbol+'24hr.png')

            pred = lin_model.coef_* len(df)+1 + lin_model.intercept_
 
            df1 = pd.DataFrame(pred)
            df1["r2score"] = r2_score(df['Close'], df['prePred'])
            df1["interval"] = "1d"
            df1['date'] = date
            df1.round(2).to_csv('website/data/'+symbol+'1dpred.csv', index=False)

            df.round(2).to_csv(r'website/data/'+symbol+'1min.csv', index=False)
            dr = csv.DictReader(fin)
            to_db = [(i['Datetime'], i['Open'], i['High'], i['Low'], i['Close'], i['Adj Close'], i['Volume'], i['change'], i['finalpchange'], i['interval']) for i in dr]
  
            cur.executemany("INSERT into ChartData (symbol, date, open, high, low, close, adj_close, volume, change, finalpchange, interval) values ('"+symbol+"',?, ?, ?, ?, ?, ?, ?,?,?,?);", to_db)
            con.commit()

        
        #---------------------------------------------------------------------

        data5 = yf.download(tickers=''+symbol+'', period='1d', interval='5m')
        data5.index = data5.index.tz_localize(None)
        data5.to_csv('website/data/'+symbol+'5min.csv')
      
        with open('website/data/'+symbol+'5min.csv','r') as fin:
            df = pd.read_csv('website/data/'+symbol+'5min.csv')
    
            df = df[['Datetime', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
            df['prevClose'] = df['Adj Close'].shift(1)
            df['change'] = (df['Adj Close']-df['prevClose'])
            df['pchange'] = (df['Adj Close']/df['prevClose']) - 1
            df['finalpchange'] = (df['pchange'] * 100)
            df["interval"] = "5min"

            df.round(2).to_csv(r'website/data/'+symbol+'5min.csv', index=False)
            dr = csv.DictReader(fin)
            to_db = [(i['Datetime'], i['Open'], i['High'], i['Low'], i['Close'], i['Adj Close'], i['Volume'], i['change'], i['finalpchange'], i['interval']) for i in dr]
  
            cur.executemany("INSERT into ChartData (symbol, date, open, high, low, close, adj_close, volume, change, finalpchange, interval) values ('"+symbol+"',?, ?, ?, ?, ?, ?, ?,?,?,?);", to_db)
            con.commit()

        #---------------------------------------------------------------------
        data = yf.download(tickers=''+symbol+'', period='6mo', interval='1d')
        data.to_csv('website/data/'+symbol+'6mo.csv')
      
        with open('website/data/'+symbol+'6mo.csv','r') as fin:
            #--------------------------------------------------------------------------------
            df = pd.read_csv('website/data/'+symbol+'6mo.csv')

            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
            df['prevClose'] = df['Adj Close'].shift(1)
            df['change'] = (df['Adj Close']-df['prevClose'])
            df['pchange'] = (df['Adj Close']/df['prevClose']) - 1
            df['finalpchange'] = (df['pchange'] * 100)
            df["interval"] = "6mo"

            fig = plt.figure()
            df = df.set_index(pd.DatetimeIndex(df['Date'].values))
            df['Numbers'] = list(range(0, len(df)))
            x = np.array(df[['Numbers']])
            y = df['Close'].values
            lin_model = LinearRegression().fit(x,y)
            y_pred = lin_model.coef_* x + lin_model.intercept_
            df['prePred'] = y_pred
            df['prePred'].plot(label="model")
            df['Close'].plot(label="price")
            plt.legend(loc="upper right")
            plt.title('6 Months '+symbol+' Close Price History and Prediction')
            fig.savefig('website/static/datavisual/'+symbol+'6mo.png')

            pred = lin_model.coef_* len(df)+1 + lin_model.intercept_
 
            df1 = pd.DataFrame(pred)
            df1["interval"] = "6mo"
            df1['r2score'] = r2_score(df['Close'], df['prePred'])
            df1.round(2).to_csv('website/data/'+symbol+'6mopred.csv', index=False)

            df.round(2).to_csv(r'website/data/'+symbol+'6mo.csv', index=False)
            dr = csv.DictReader(fin)

            to_db = [(i['Date'], i['Open'], i['High'], i['Low'], i['Close'], i['Adj Close'], i['change'], i['finalpchange'], i['interval']) for i in dr]

            cur.executemany("INSERT into ChartData (symbol, date, open, high, low, close, adj_close, change, finalpchange, interval) values ('"+symbol+"',?, ?, ?, ?, ?, ?,?,?,?);", to_db)
            con.commit()
            #----------------------------------------------------------------------------------

        
        data1month = yf.download(tickers=''+symbol+'', period='1mo', interval='1d')
        data1month.to_csv('website/data/'+symbol+'1mo.csv')
        with open('website/data/'+symbol+'1mo.csv','r') as fin:
            #--------------------------------------------------------------------------------
            df = pd.read_csv('website/data/'+symbol+'1mo.csv')

            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
            df['prevClose'] = df['Adj Close'].shift(1)
            df['change'] = (df['Adj Close']-df['prevClose'])
            df['pchange'] = (df['Adj Close']/df['prevClose']) - 1
            df['finalpchange'] = (df['pchange'] * 100)
            df["interval"] = "1mo"

            fig = plt.figure()
            df = df.set_index(pd.DatetimeIndex(df['Date'].values))
            df['Numbers'] = list(range(0, len(df)))
            x = np.array(df[['Numbers']])
            y = df['Close'].values
            lin_model = LinearRegression().fit(x,y)
            y_pred = lin_model.coef_* x + lin_model.intercept_
            df['prePred'] = y_pred
            df['prePred'].plot(label="model")
            df['Close'].plot(label="price")
            plt.legend(loc="upper right")
            plt.title('1 Month '+symbol+' Close Price History and Prediction')

            fig.savefig('website/static/datavisual/'+symbol+'1mo.png')

            pred = lin_model.coef_* len(df)+1 + lin_model.intercept_
 
            df1 = pd.DataFrame(pred)
            df1["interval"] = "1mo"
            df1['r2score'] = r2_score(df['Close'], df['prePred'])
            df1.round(2).to_csv('website/data/'+symbol+'1mopred.csv', index=False)

            df.round(2).to_csv(r'website/data/'+symbol+'1mo.csv', index=False)
            dr = csv.DictReader(fin)

            to_db = [(i['Date'], i['Open'], i['High'], i['Low'], i['Close'], i['Adj Close'], i['change'], i['finalpchange'], i['interval']) for i in dr]

            cur.executemany("INSERT into ChartData (symbol, date, open, high, low, close, adj_close, change, finalpchange, interval) values ('"+symbol+"',?, ?, ?, ?, ?, ?,?,?,?);", to_db)
            con.commit()
      
        data = yf.download(tickers=''+symbol+'', period='max', interval='1d')
        data.to_csv('website/data/'+symbol+'.csv')
        with open('website/data/'+symbol+'.csv','r') as fin:
            #--------------------------------------------------------------------------------
            df = pd.read_csv('website/data/'+symbol+'.csv')

            df = df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume', 'Adj Close']]
            df['prevClose'] = df['Adj Close'].shift(1)
            df['change'] = (df['Adj Close']-df['prevClose'])
            df['pchange'] = (df['Adj Close']/df['prevClose']) - 1
            df['finalpchange'] = (df['pchange'] * 100)
            df["interval"] = "1d"

            #df = df.set_index(pd.DatetimeIndex(df['Date'].values))
            #df['Numbers'] = list(range(0, len(df)))
            #x = np.array(df[['Numbers']])
            #y = df['Close'].values
            #lin_model = LinearRegression().fit(x,y)
            #y_pred = lin_model.coef_* x + lin_model.intercept_
            #df['prePred'] = y_pred
            #df['error'] = r2_score(df['Close'], df['prePred'])

            #pred = lin_model.coef_* len(df)+1 + lin_model.intercept_
 
            #df1 = pd.DataFrame(pred)
            #df1.round(2).to_csv('website/data/'+symbol+'pred.csv', index=False)

            df.round(2).to_csv(r'website/data/'+symbol+'.csv', index=False)
            dr = csv.DictReader(fin)

            to_db = [(i['Date'], i['Open'], i['High'], i['Low'], i['Close'], i['Adj Close'], i['Volume'], i['change'], i['finalpchange'], i['interval']) for i in dr]

            cur.executemany("INSERT into ChartData (symbol, date, open, high, low, close, adj_close, volume, change, finalpchange, interval) values ('"+symbol+"',?, ?, ?, ?, ?, ?,?,?,?,?);", to_db)
            con.commit()
            #--------------------------------------------------------------------------------

            fig = go.Figure()
            df = pd.read_sql_query("SELECT * FROM ChartData where symbol = '"+symbol+"' and interval='1d';","sqlite:////Users/Jerome/Desktop/THESIS - Rebrand/system.db")


            fig = make_subplots(specs=[[{"secondary_y":True}]])
            fig.add_trace(go.Candlestick(x=df.date,
                            open=df['open'],
                            high=df['high'],
                            low=df['low'],
                            close=df['close'], name = 'body'),
                            secondary_y=True)
            
            fig.add_trace(go.Bar(x=df['date'], y=df['volume'], name = 'volume'),
                                secondary_y=False)
            
            fig.update_layout(
                title=symbol+' Chart',
                yaxis_title=symbol+' Stock Price (USD)',
                paper_bgcolor='rgba(0,0,0,0)')

            fig.update_xaxes(
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1d", step="day", stepmode="backward"),
                        dict(count=7, label="1wk", step="day", stepmode="backward"),
                        dict(count=1, label="1mo", step="month", stepmode="backward"),
                        dict(count=1, label="1yr", step="year", stepmode="backward"),
                        dict(step="all", label="max")
                    ])
                )
            )

            graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        with open('website/data/'+symbol+'1yrpred.csv','r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['0'], i['interval'], i['r2score']) for i in dr]

            cur.executemany("INSERT into Prediction (symbol, prediction, interval, r2score) values ('"+symbol+"',?,?,?)", to_db)
            con.commit()

        with open('website/data/'+symbol+'6mopred.csv','r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['0'], i['interval'], i['r2score']) for i in dr]

            cur.executemany("INSERT into Prediction (symbol, prediction, interval, r2score) values ('"+symbol+"',?,?,?)", to_db)
            con.commit()

        with open('website/data/'+symbol+'3mopred.csv','r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['0'], i['interval'], i['r2score']) for i in dr]

            cur.executemany("INSERT into Prediction (symbol, prediction, interval, r2score) values ('"+symbol+"',?,?,?)", to_db)
            con.commit()
 
        with open('website/data/'+symbol+'1mopred.csv','r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['0'], i['interval'], i['r2score']) for i in dr]

            cur.executemany("INSERT into Prediction (symbol, prediction, interval, r2score) values ('"+symbol+"',?,?,?)", to_db)
            con.commit()
        
        with open('website/data/'+symbol+'1dpred.csv','r') as fin:
            dr = csv.DictReader(fin)
            to_db = [(i['0'], i['interval'], i['date'], i['r2score']) for i in dr]

            cur.executemany("INSERT into Prediction (symbol, prediction, interval, date, r2score) values ('"+symbol+"',?,?,?,?)", to_db)
            con.commit()

        r = requests.get('https://finance.yahoo.com/quote/'+symbol+'?p='+symbol+'')
        soup = bs4.BeautifulSoup(r.text, "html.parser")


        find_all_div = soup.find_all('div', {"class": "D(ib) Mend(20px)"})[0]
        closed_time = find_all_div.find_all("div", {"class":"C($tertiaryColor) D(b) Fz(12px) Fw(n) Mstart(0)--mobpsm Mt(6px)--mobpsm Whs(n)"})

        closed_time[0].text

        find_all_div = soup.find_all('div', {"class": "D(ib) Mend(20px)"})[0]
        current_price = find_all_div.find_all("fin-streamer", {"class":"Fw(b) Fz(36px) Mb(-4px) D(ib)"})

        current_price[0].text
        
        find_all_div = soup.find_all('fin-streamer', {"class": "Fw(500) Pstart(8px) Fz(24px)"})[0]
        current_change = find_all_div.find_all("span", {"class":["C($positiveColor)",
                                                                 "C($negativeColor)"]})

        current_change[0].text 


        find_all_div = soup.find_all('fin-streamer', {"class": "Fw(500) Pstart(8px) Fz(24px)"})[1]
        current_changepercent = find_all_div.find_all("span", {"class":["C($positiveColor)",
                                                                        "C($negativeColor)"]})
        current_changepercent[0].text

        find_all_div = soup.find_all('div', {"class": "D(ib) W(1/2) Bxz(bb) Pend(12px) Va(t) ie-7_D(i) smartphone_D(b) smartphone_W(100%) smartphone_Pend(0px) smartphone_BdY smartphone_Bdc($seperatorColor)"})[0]
        previousclose = find_all_div.find_all("td", {"class":["Ta(end) Fw(600) Lh(14px)"]})
        previousclose[0].text

        cur.execute("SELECT finalpchange FROM ChartData where symbol=? and interval='1wk' ORDER BY date desc LIMIT 1",([symbol]))
        fivedays = cur.fetchall()

        cur.execute("DELETE FROM ChartData WHERE date = (SELECT MAX(date) FROM ChartData) and symbol=? and interval='1min'",([symbol]))
        con.commit()

        cur.execute("SELECT finalpchange FROM ChartData where symbol=? and interval='1min' ORDER BY date desc LIMIT 1",([symbol]))
        onemin = cur.fetchall()

        cur.execute("DELETE FROM ChartData WHERE date = (SELECT MAX(date) FROM ChartData) and symbol=? and interval='5min'",([symbol]))
        con.commit()

        cur.execute("SELECT finalpchange FROM ChartData where symbol=? and interval='5min' ORDER BY date desc LIMIT 1",([symbol]))
        fivemin = cur.fetchall()

        cur.execute("DELETE FROM ChartData WHERE date = (SELECT MAX(date) FROM ChartData) and symbol=? and interval='1hr'",([symbol]))
        con.commit()

        cur.execute("SELECT finalpchange FROM ChartData where symbol =? and interval='1hr' ORDER BY date desc LIMIT 1",([symbol]))
        hour = cur.fetchall()

        cur.execute("SELECT finalpchange FROM ChartData where symbol =? and interval='6mo' ORDER BY date DESC LIMIT 1",([symbol]))
        phour = cur.fetchall()

        cur.execute("select * from Stocks WHERE symbol =?",([symbol]))
        profile = cur.fetchall()

        cur.execute("select * from Broker")
        broker = cur.fetchall()

        cur.execute("SELECT * FROM ChartData where symbol=? and interval='1d' ORDER BY DATE DESC LIMIT 7", ([symbol]))
        hdata = cur.fetchall()

        cur.execute("SELECT * FROM ChartData where symbol=? and interval = '1d' ORDER BY DATE DESC LIMIT 1", ([symbol]))
        info = cur.fetchall()

        cur.execute("SELECT date FROM ChartData where symbol=? ORDER BY DATE ASC LIMIT 1", ([symbol]))
        h = cur.fetchall()

        #----------------------------------------------------------------------------------------------
        cur.execute("SELECT * FROM Prediction where symbol=? and interval='1d' ORDER BY DATE DESC LIMIT 1", ([symbol]))
        prediction = cur.fetchall()

        #cur.execute("SELECT error from ChartData WHERE symbol=? and interval='1min' ORDER BY DATE DESC LIMIT 1", ([symbol]))
        #error= cur.fetchall()
        #---------------------------------------------------------------------------------------------
        cur.execute("SELECT * FROM Prediction where symbol=? and interval='1mo'", ([symbol]))
        onemopred = cur.fetchall()

        #cur.execute("SELECT error from ChartData WHERE symbol=? and interval='1mo' ORDER BY DATE DESC LIMIT 1", ([symbol]))
        #onemoerror= cur.fetchall()
        #---------------------------------------------------------------------------------------------
        cur.execute("SELECT * FROM Prediction where symbol=? and interval='3mo'", ([symbol]))
        threemopred = cur.fetchall()

        #cur.execute("SELECT error from ChartData WHERE symbol=? and interval='3mo' ORDER BY DATE DESC LIMIT 1", ([symbol]))
        #threemoerror= cur.fetchall()
        #---------------------------------------------------------------------------------------------
        cur.execute("SELECT * FROM Prediction where symbol=? and interval='6mo'", ([symbol]))
        sixmopred = cur.fetchall()

        #cur.execute("SELECT error from ChartData WHERE symbol=? and interval='6mo' ORDER BY DATE DESC LIMIT 1", ([symbol]))
        #sixmoerror= cur.fetchall()
        #---------------------------------------------------------------------------------------------
        cur.execute("SELECT * FROM Prediction where symbol=? and interval='1yr'", ([symbol]))
        oneyrpred = cur.fetchall()

        #cur.execute("SELECT error from ChartData WHERE symbol=? and interval='1yr' ORDER BY DATE DESC LIMIT 1", ([symbol]))
        #oneyrerror= cur.fetchall()
        #---------------------------------------------------------------------------------------------
        
        #------------------------Historical Data------------------------------------------------------------------
        cur.execute("SELECT * FROM ChartData where symbol=? and interval='1min' ORDER BY DATE DESC",([symbol]))
        onemindata = cur.fetchall()

        cur.execute("SELECT * FROM ChartData where symbol=? and interval='5min' ORDER BY DATE DESC",([symbol]))
        fivemindata = cur.fetchall()

        cur.execute("DELETE FROM ChartData WHERE date = (SELECT MAX(date) FROM ChartData) and symbol=? and interval='15min'",([symbol]))
        con.commit()

        cur.execute("SELECT * FROM ChartData where symbol=? and interval='15min' ORDER BY DATE DESC",([symbol]))
        fifteendata = cur.fetchall()

        cur.execute("DELETE FROM ChartData WHERE date = (SELECT MAX(date) FROM ChartData) and symbol=? and interval='30min'",([symbol]))
        con.commit()

        cur.execute("SELECT * FROM ChartData where symbol=? and interval='30min' ORDER BY DATE DESC",([symbol]))
        thirtymindata = cur.fetchall()

        cur.execute("SELECT * FROM ChartData where symbol=? and interval='1hr' ORDER BY DATE DESC",([symbol]))
        onehourdata = cur.fetchall()
        #----------------------------------------------------------------------------------------------------------
        cur.execute("SELECT * FROM Broker")
        market = cur.fetchall()

        cur.execute("SELECT interval FROM ChartData")
        interval = cur.fetchall()

        cur.execute("SELECT * FROM Blog WHERE category=? ORDER BY DATE DESC LIMIT 6",[(symbol)])
        blog = cur.fetchall()

        #---------------------------------------------------------------------------------------------------------

        #cur.execute(f"SELECT * from Interval WHERE SYMBOL='{symbol}' and interval='{'1min'}';")
        #rows3 = cur.fetchall()



        return render_template(("assetinfo.html"),  blog = blog,
                                                    interval = interval,
                                                    market=market,
                                                    onehourdata=onehourdata,
                                                    thirtymindata=thirtymindata,
                                                    fifteendata=fifteendata,
                                                    fivemindata= fivemindata,
                                                    onemindata = onemindata,
                                                    
                                                    sixmopred = sixmopred,
                                                    
                                                    onemopred = onemopred,
                                                    
                                                    threemopred = threemopred,
                                                    
                                                    oneyrpred = oneyrpred,
                                                    
                                                    prediction = prediction,  
                                                    fivedays = fivedays, 
                                                    fivemin=fivemin, 
                                                    onemin = onemin, 
                                                    phour=phour, 
                                                    hour=hour, 
                                                    h=h, 
                                                    info=info, 
                                                    graphJSON=graphJSON, 
                                                    current_price=current_price, 
                                                    current_change=current_change, 
                                                    current_changepercent=current_changepercent, 
                                                    closed_time=closed_time, 
                                                    previousclose = previousclose, 
                                                    data=data, profile=profile, 
                                                    broker=broker, 
                                                    hdata=hdata, 
                                                    symbol=symbol)
    
    else:
        return redirect(url_for("auth.login"))