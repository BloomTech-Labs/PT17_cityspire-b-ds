"""Database functions"""

import os
from fastapi import APIRouter, Depends
import sqlalchemy
from dotenv import load_dotenv
import databases
import asyncio
from typing import Union, Iterable
from pypika import Query, Table, CustomFunction
from pypika.terms import Field

Field_ = Union[Field, str]

load_dotenv()
database_url = os.getenv("DATABASE_URL")
database = databases.Database(database_url)

router = APIRouter()


@router.get("/info")
async def get_url():
    """Verify we can connect to the database,
    and return the database URL in this format:

    dialect://user:password@host/dbname

    The password will be hidden with ***
    """

    url_without_password = repr(database.url)
    return {"database_url": url_without_password}


@router.get("/all_cities")
async def get_cities():
    """
    Get available cities from DB
    """
    data = Table("data")
    
    columns = (
        data["City"].as_("City"),
        data["State"].as_("State"),
    )

    q = (
        Query.from_(data)
        .select(*columns)
    )
    value = await database.fetch_all(str(q))
    return value


async def select(columns: Union[Iterable[Field_], Field_], city):
    data = Table("data")
    if type(columns) == str or type(columns) == Field:
        q = Query.from_(data).select(columns)
    else:
        cols = [data[x] for x in columns]
        q = Query.from_(data).select(*cols)

    q = q.where(data.City == city.city).where(data.State == city.state)

    value = await database.fetch_one(str(q))
    return value


async def select_all(city):
    """Fetch all data at once

    Fetch data from DB

    args:
        city: selected city

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """
    data = Table("data")
    di_fn = CustomFunction("ROUND", ["number"])
    columns = (
        # 'lat', 'lon'
        data["lat"].as_("latitude"),
        data["lon"].as_("longitude"),
        data['SunnyDays_avgPerYear'].as_("sunny_days_avg_year"),
        data['CloudyDays_avgPerYear'].as_("cloudy_days_avg_year"),
        data['RainyDays_avgPerYear'].as_("rainy_days_avg_year"),
        data['SnowyDays_avgPerYear'].as_("snowy_days_avg_year"),
        data["Crime Rating"].as_("crime"),
        data["Rent"].as_("rental_price"),
        data["Air Quality Index"].as_("air_quality_index"),
        data["Population"].as_("population"),
        data["Nearest"].as_("nearest_string"),
        data["Good Days"].as_("good_days"),
        data["Crime Rate per 1000"].as_("crime_rate_ppt"),
        di_fn(data["Diversity Index"] * 100).as_("diversity_index"),
    )

    q = (
        Query.from_(data)
        .select(*columns)
        .where(data.City == city.city)
        .where(data.State == city.state)
    )
    value = await database.fetch_one(str(q))
    return value

  
async def select_housing_price_averages(city):
    """Fetch housing price averages per city
    
    The averages includes single family homes, condos, one bedroom,
    two bedroom, three bedroom, four bedroom, and five and up bedroom averages.
    (Bedroom averages are based off single family homes AND condos.)
    
    Fetch data from DB
    
    args:
        city: selected city
        
    returns:
        Dictionary that contains the requested data, which is converted by fastAPI to a json object.
    """
    prices = Table("data")
    
    columns = (
        prices['SingleFamilyHousingAvgValue'].as_("single_family_housing_avg_price"),
        prices['CondoAvgValue'].as_("condo_avg_price"),
        prices['1-BedroomAvgValue'].as_("1_bedroom_avg_price"),
        prices['2-BedroomAvgValue'].as_("2_bedroom_avg_price"),
        prices['3-BedroomAvgValue'].as_("3_bedroom_avg_price"),
        prices['4-BedroomAvgValue'].as_("4_bedroom_avg_price"),
        prices['5+-BedroomAvgValue'].as_("5_and_up_bedroom_avg_price"),
    )
    
    q = (
        Query.from_(prices)
        .select(*columns)
        .where(prices.City == city.city)
        .where(prices.State == city.state)
    )
    value = await database.fetch_one(str(q))
    return value


async def select_weather_historical(city):
    """Fetch historical weather per city

    Fetch data from DB

    args:
        city: selected city

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """
    historical = Table("historical_weather")

    columns = (
        historical["Date time"].as_("date"),
        historical["Latitude"].as_("lat"),
        historical["Longitude"].as_("lon"),
        historical["Temperature (degF)"].as_("avg_temp_fahrenheit"),
        historical["Minimum Temperature (degF)"].as_("min_temp_fahrenheit"),
        historical["Maximum Temperature (degF)"].as_("max_temp_fahrenheit"),
        historical["Precipitation (in)"].as_("precipitation_inches"),
        historical["Precipitation Cover (%)"].as_("precipitation_percentage"),
        historical["Relative Humidity (%)"].as_("humidity_percentage"),
        historical["Conditions"].as_("weather_conditions"),
        historical["Wind Direction"].as_("wind_direction"),
        historical["Wind Speed (mph)"].as_("wind_speed_mph"),
        historical["Wind Gust (mph)"].as_("wind_gust_mph"),
        historical["Cloud Cover (%)"].as_("cloud_cover_percentage"),
        historical["Dew Point (degF)"].as_("dew_point_fahrenheit"),
        historical["Visibility (mi)"].as_("visibility_miles"),
        historical["Snow (in)"].as_("snow_inches"),
        historical["Snow Depth (in)"].as_("snow_depth_inches"),
        historical["Sea Level Pressure (mb)"].as_("sea_level_pressure_millibars"), 
    )

    q = (
        Query.from_(historical)
        .select(*columns)
        .where(historical.City == city.city)
        .where(historical.State == city.state)
        # .where(historical["Date time"] >= '2020-01-01')
    )
    value = await database.fetch_all(str(q))


async def select_schooldist_info(city):
    """Fetch school district information
    
    Fetch data from DB
    
    args:
        city: selected city
        
    returns:
        Dictionary that contains the requested data, which is converted by fastAPI to a json object.
    """
    schoold = Table("schooldist")
    
    columns = (
        schoold['Total Number of Public Schools'].as_("total_number_of_schools"),
        schoold['Total Students'].as_("total_students"),
        schoold['Total Teachers'].as_("total_teachers"),
        schoold['Student/Teacher Ratio'].as_("ratio"),
    )
    
    q = (
        Query.from_(schoold)
        .select(*columns)
        .where(schoold.City == city.city)
        .where(schoold.State == city.state)
    )
    value = await database.fetch_one(str(q))

    return value

async def select_weather_daily(city):
    """Fetch weather forecast per city

    Fetch data from DB

    args:
        city: selected city

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """
    forecast = Table("weather_daily_forecast")

    columns = (
        forecast["date"].as_("date"),
        forecast["temperature_pred"].as_("average_temperature"),
        forecast["temp_lower_pred"].as_("min_temperature"),
        forecast["temp_upper_pred"].as_("max_temperature"),
    )

    q = (
        Query.from_(forecast)
        .select(*columns)
        .where(forecast.city == city.city)
        .where(forecast.state == city.state)
    )
    value = await database.fetch_all(str(q))
    return value

  
async def select_weather_monthly(city):
    """Fetch weather forecast per city

    Fetch data from DB

    args:
        city: selected city

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """
    forecast = Table("weather_monthly_forecast")

    columns = (
        forecast["date"].as_("date"),
        forecast["temperature_pred"].as_("average_temperature"),
        forecast["temp_lower_pred"].as_("min_temperature"),
        forecast["temp_upper_pred"].as_("max_temperature"),
    )

    q = (
        Query.from_(forecast)
        .select(*columns)
        .where(forecast.city == city.city)
        .where(forecast.state == city.state)
    )
    value = await database.fetch_all(str(q))
    return value
    

async def select_weather_conditions(city):
    """Fetch weather conditions sunny/cloudy/rainy/snowy days per city
    
    Fetch data from DB
    
    args:
        city: selected city
        
    returns:
        Dictionary that contains the requested data, which is converted by fastAPI to a json object.
    """
    conditions = Table("data")
    
    columns = (
        conditions['SunnyDays_avgPerYear'].as_("sunny_days_avg_year"),
        conditions['CloudyDays_avgPerYear'].as_("cloudy_days_avg_year"),
        conditions['RainyDays_avgPerYear'].as_("rainy_days_avg_year"),
        conditions['SnowyDays_avgPerYear'].as_("snowy_days_avg_year"),
    )
    
    q = (
        Query.from_(conditions)
        .select(*columns)
        .where(conditions.City == city.city)
        .where(conditions.State == city.state)
    )
    value = await database.fetch_one(str(q))
    return value
