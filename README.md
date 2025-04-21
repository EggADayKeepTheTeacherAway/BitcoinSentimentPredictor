# Bitcoin sentiment predictor

## Project Overview
The Bitcoin Sentiment Predictor aims to analyze sentiment from recently collected social media posts about Bitcoin and correlate it with historical bitcoin data to predict short-term price movements.

## Primary data source(s)
Sentiment data from 1,917 Reddit posts in /bitcoin. Sentiment will be labeled as positive, negative, or neutral.

## Secondary data source(s)
Historical Bitcoin data CoinGecko API

## API to be provided to users
1. Get the prediction result (Bitcoin price will go up or down).
2. Get the last 30 days of Bitcoin prices.
3. Get the Reddit post related to Bitcoin.
4. Analyze the sentiment of provided text using NLTK's VADER sentiment analyzer.

## Installation Guide:

Clone this repository
```
git clone <repository link>
```

Create Python environment
```
python -m venv .venv
```

Activate the virtual environment

On Linux or MacOS

```
source venv/bin/activate
```

On Windows

```
venv\Scripts\activate
```

Install All packages

```
pip install -r requirements.txt
```

Set Values For Externalized Variables

For macOS/Linux

```
cp sample.env .env
```
For Windows

```
copy sample.env .env
```

## Running the Application

1. Activate the virtual environment
      
   On Linux or MacOS
   ```
   source venv/bin/activate
   ```
   On Windows
   ```
   venv\Scripts\activate
   ```

2. Use this command to run the sever the default server is [localhost:8501](http://localhost:8501)
  ```
  streamlit run main.py
  ```

## Running the API server

1. Change dir
  ```
  cd ./fast-api
  ```

2. Run the server the default server is [localhost:6969](http://localhost:6969)
  ```
  uvicorn very_fast:app --port 6969 --reload
  ```

## Member
1. Kasidet Uthaiwiwatkul
2. Panida Rumriankit

![egg](https://github.com/EggADayKeepTheTeacherAway/BitcoinSentimentPredictor/blob/dcead5fda27f86724a09c58ba9a69fcad366fd4a/public/egg_bitcoin.png)

