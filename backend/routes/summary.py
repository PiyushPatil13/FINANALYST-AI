from fastapi import APIRouter,HTTPException
from pydantic import BaseModel
from backend.utils.yfinance_loader import YFinanceLoader
from backend.core.llm_config import get_gemini_llm
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

SUMMARY_PROMPT = PromptTemplate(
    input_variables=[
        "name","ticker","sector","marketcap","pe_ratio","current_price","high","low"
    ],
    template="""
You are a senior equity research analyst.
Based on the following live market data, write a 4-5 sentence
professional stock summary covering valuation, sector context,
and observations from the price range.
Name: {name}
Ticker: {ticker}
Sector: {sector}
Market Cap: {market_cap}
P/E Ratio: {pe_ratio}
Current Price: {current_price}
52-Week High: {high}
52-Week Low: {low}

Write a concise analyst-style summary:
""",

)

# RESPONSE MODELS

class SummaryRequest(BaseModel):
    ticker:str

class SummaryResponse(BaseModel):
    ticker:str
    name:str = "N/A"
    market_data:dict
    ai_summary:str

#Endpoints

@router.post("/stock",response_model=SummaryResponse)
async def summarize_stock(request:SummaryRequest):
    # fetch live stock data
    ticker = request.ticker.strip().upper()

    if not ticker:
        raise HTTPException(status_code=400,detail="Ticker cannot be empty")
    
    try:

        loader = YFinanceLoader(ticker)
        stock = loader.get_ticker_summary()

        # get the llm 
        llm = get_gemini_llm()
        chain = SUMMARY_PROMPT | llm | StrOutputParser()

        ai_summary = chain.invoke({
            "name":stock["name"],
            "ticker":stock["ticker"],
            "sector":stock["sector"],
            "market_cap":stock["market_cap"],
            "pe_ratio":stock["pe_ratio"],
            "current_price":stock["current_price"],
            "high":stock["52w_high"],
            "low":stock["52w_low"]
        })

        return SummaryResponse(
            ticker=ticker,
            name = stock.get("name","N/A"),
            market_data=stock,
            ai_summary=ai_summary.strip()
        )
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    

@router.get("/stock/history/{ticker}")
async def get_history(ticker:str,period:str = "1y"):
    # Return historical prices for charting:
    valid = ["1mo","3mo","6mo","1y","2y"]
    if period not in valid:
        raise HTTPException(status_code=400,detail =f"Invalid period. Choose from {valid}")
    
    loader = YFinanceLoader(ticker.upper())
    prices = loader.get_historical_prices(period)

    return {
        "ticker":ticker.upper(),
        "period":period,
        "prices":prices
    }

@router.get("/stock/ohlc/{ticker}")
async def get_ohlc(ticker: str, period: str = "1y"):
    """Return OHLC data for candlestick chart."""
    valid = ["1mo", "3mo", "6mo", "1y", "2y"]
    if period not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid period.")

    try:
        loader = YFinanceLoader(ticker.upper())
        hist = loader.stock.history(period=period)

        if hist.empty:
            return {"ohlc": []}

        hist = hist.reset_index()
        return {
            "ohlc": [
                {
                    "date":  str(row["Date"].date()),
                    "open":  round(row["Open"], 2),
                    "high":  round(row["High"], 2),
                    "low":   round(row["Low"], 2),
                    "close": round(row["Close"], 2)
                }
                for _, row in hist.iterrows()
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

