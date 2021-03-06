"""Machine learning functions"""
from pickle import load
import requests
from bs4 import BeautifulSoup as bs
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.state_abbr import us_state_abbrev as abbr
from pathlib import Path
import pandas as pd
from pypika import Query, Table, CustomFunction
import asyncio

from app.db import database, select, select_all, select_housing_price_averages, select_schooldist_info
from app.db import select_weather_daily, select_weather_monthly, select_weather_conditions, select_weather_historical

from typing import List, Optional


router = APIRouter()


class City(BaseModel):
    city: str = "New York"
    state: str = "NY"


class CityRecommendations(BaseModel):
    recommendations: List[City]


class CityDataBase(BaseModel):
    city: City
    latitude: float
    longitude: float
    rental_price: float
    crime: str
    air_quality_index: str
    population: int
    diversity_index: float
    sunny_days_avg_year: int
    cloudy_days_avg_year: int
    rainy_days_avg_year: int
    snowy_days_avg_year: int


class CityData(CityDataBase):
    walkability: float
    livability: float
    recommendations: List[City]


class CityDataFull(CityDataBase):
    good_days: int
    crime_rate_ppt: float
    nearest_string: str


class LivabilityWeights(BaseModel):
    walkability: float = 1.0
    low_rent: float = 1.0
    low_pollution: float = 1.0
    diversity: float = 1.0
    low_crime: float = 1.0


def validate_city(
    city: City,
) -> City:
    """Ensure City name and State name are in the right format.

    Ensures that the city name is in Title Case and the State is converted from
    Full name to All Caps ABBR if needed.

    args:
        city: The City object to be Validated

    returns:
        a City object in a proper format to be used elsewhere.

    raises:
        HTTPException:
            If the state cannot be converted into an ABBR
    """

    city.city = city.city.title()

    try:
        if len(city.state) > 2:
            city.state = city.state.title()
            city.state = abbr[city.state]
        else:
            city.state = city.state.upper()
    except KeyError:
        raise HTTPException(status_code=422, detail=f"Unknown state: '{city.state}'")

    return city


@router.post("/api/get_data", response_model=CityData)
async def get_data(city: City):
    """Retrieve all data for city

    Fetch data from DB, calculate derived stats, scrape Walkscore
    return data

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """

    city = validate_city(city)

    value = await select_all(city)

    full_data = CityDataFull(city=city, **value)
    tasks = await asyncio.gather(
        get_livability_score(city, full_data),
        get_walkability(city),
        get_recommendation_cities(city, full_data.nearest_string),
    )
    data = {**full_data.dict()}

    for item in tasks:
        data.update(item)

    return data


@router.post("/api/coordinates")
async def get_coordinates(city: City):
    """Retrieve coordinates for target city

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    value = await select(["lat", "lon"], city)
    return {"latitude": value[0], "longitude": value[1]}


@router.post("/api/crime")
async def get_crime(city: City):
    """Retrieve crime rate for target city

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    data = Table("data")
    value = await select("Crime Rating", city)
    return {"crime": value[0]}


@router.post("/api/rental_price")
async def get_rental_price(city: City):
    """Retrieve rental price for target city

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    value = await select("Rent", city)

    return {"rental_price": value[0]}


@router.post("/api/pollution")
async def get_pollution(city: City):
    """Retrieve pollution rating for target city

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    value = await select("Air Quality Index", city)
    return {"air_quality_index": value[0]}


@router.post("/api/walkability")
async def get_walkability(city: City):
    """Retrieve walkscore for target city

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    try:
        score = (await get_walkscore(**city.dict()))[0]
    except IndexError:
        raise HTTPException(
            status_code=422, detail=f"Walkscore not found for {city.city}, {city.state}"
        )

    return {"walkability": score}


async def get_walkscore(city: str, state: str):
    """Scrape Walkscore.

    args:
        city: The target city
        state: Target state as an all-caps 2-letter abbr

    returns:
        List containing WalkScore, BusScore, and BikeScore in that order
    """

    r_ = requests.get(f"https://www.walkscore.com/{state}/{city}")
    images = bs(r_.text, features="lxml").select(".block-header-badge img")
    return [int(str(x)[10:12]) for x in images]


@router.post("/api/livability")
async def get_livability(city: City, weights: LivabilityWeights = None):
    """Calculate livability score

    Fetch data from DB, calculate derived stats, scrape Walkscore
    return data

    args:
        city: The target city
        LivabilityWeights: Weights for the to use for calculation

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    values = await select(["Rent", "Good Days", "Crime Rate per 1000"], city)
    with open("app/livability_scaler.pkl", "rb") as f:
        s = load(f)
    v = [[values[0] * -1, values[1], values[2] * -1]]
    scaled = s.transform(v)[0]
    walkscore = await get_walkscore(city.city, city.state)
    diversity_index = await select("Diversity Index", city)

    rescaled = [walkscore[0]]
    rescaled.append(round(diversity_index[0]) * 100)
    for score in scaled:
        rescaled.append(score * 100)
    # breakpoint()
    if weights is None:
        return {"livability": round(sum(rescaled) / 5)}
    else:
        weighted = [
            rescaled[0] * weights.walkability,
            rescaled[1] * weights.diversity,
            rescaled[2] * weights.low_rent,
            rescaled[3] * weights.low_pollution,
            rescaled[4] * weights.low_crime,
        ]

        sum_ = sum(weighted)
        divisor = sum(weights.dict().values())

        return {"livability": round(sum_ / divisor)}


async def get_livability_score(city: City, city_data: CityDataFull):
    """Calculate livability score

    Fetch data from DB, calculate derived stats, scrape Walkscore
    return data

    args:
        city: The target city


    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """

    with open("app/livability_scaler.pkl", "rb") as f:
        s = load(f)
    v = [
        [
            city_data.rental_price * -1,
            city_data.good_days,
            city_data.crime_rate_ppt * -1,
        ]
    ]
    scaled = s.transform(v)[0]
    walkscore = await get_walkscore(city.city, city.state)

    rescaled = [walkscore[0], city_data.diversity_index]
    for score in scaled:
        rescaled.append(score * 100)

    return {"livability": round(sum(rescaled) / 5)}


@router.post("/api/population")
async def get_population(city: City):
    """Retrieve population rating for target city

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """

    city = validate_city(city)
    value = await select("Population", city)
    return {"population": value[0]}


@router.post("/api/nearest", response_model=CityRecommendations)
async def get_recommendations(city: City):
    """Retrieve recommended cities for target city

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """

    city = validate_city(city)
    value = await select("Nearest", city)

    recommendations = await get_recommendation_cities(city, value.get("Nearest"))

    return recommendations


async def get_recommendation_cities(city: City, nearest_string: str):
    """Use the string and transform to City

    Fetch data from DB

    args:
        nearest_string: String consisting of the index numbers of the recommended cities.

    returns:
        Dictionary that contains the requested data, which is converted
            by fastAPI to a json object.
    """

    test_list = nearest_string.split(",")

    data = Table("data")
    q2 = (
        Query.from_(data)
        .select(data["City"])
        .select(data["State"])
        .where(data.index)
        .isin(test_list)
    )

    recommendations = await database.fetch_all(str(q2))
    recs = CityRecommendations(
        recommendations=[
            City(city=item["City"], state=item["State"]) for item in recommendations
        ]
    )

    return recs


@router.post("/api/housing_price_averages")
async def get_housing_price_averages(city: City):
    """Retrieve housing price averages per city
    
    The averages includes single family homes, condos, one bedroom,
    two bedroom, three bedroom, four bedroom, and five and up bedroom averages.
    (Bedroom averages are based off single family homes AND condos.)
    
    Fetch data from DB
    
    args:
        city: selected city
        
    returns:
        Dictionary that contains the requested data, which is converted by fastAPI to a json object.
    """
    city = validate_city(city)
    value = await select_housing_price_averages(city)

    
    return {'City': city.city, 'State': city.state, 'single_family_housing_avg_price'
            : value[0], 'condo_avg_price': value[1], '1_bedroom_avg_price': value[2], 
            '2_bedroom_avg_price': value[3], '3_bedroom_avg_price': value[4], '4_bedroom_avg_price':
           value[5], '5_and_up_bedroom_avg_price': value[6]}
  

@router.post("/api/school_district_information")
async def get_school_district_information(city: City):
    """Retrieve school district information per city

    this includes the total number of schools, the total number of students in that school district,
    the total number of teachers in that school district, and the pupil/teacher ratio in that school district
    
    Fetch data from DB
    
    args:
        city: selected city
        
    returns:
        Dictionary that contains the requested data, which is converted by fastAPI to a json object.
    """
    city = validate_city(city)
    value = await select_schooldist_info(city)

    
    return {'City': city.city, 'State': city.state, 'total_number_of_schools'
            : value[0], 'total_students': value[1], 'total_teachers': value[2], 
            'ratio': value[3],}

@router.post("/api/weather_historical")
async def get_historical_weather(city: City):
    """Retrieve daily historical weather for target city (date range 2017/01/01 - 2021/03/16)

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    weather_hist = await select_weather_historical(city)
    
    return {'City': city.city, 'State': city.state, 'weather_temperature': weather_hist}

@router.post("/api/weather_daily_forecast")
async def get_daily_forecast(city: City):
    """Retrieve daily weather forecast for target city
       Forecasted daily temperature for the next two years (2021/03/17 - 2023/03/16)

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    weather_temp = await select_weather_monthly(city)

    return {'City': city.city, 'State': city.state, 'weather_temperature': weather_temp}

  
@router.post("/api/weather_monthly_forecast")
async def get_monthly_forecast(city: City):
    """Retrieve monthly weather forecast for target city
       Forecasted monthly temperature for next two years (2021/03/17 - 2023/03/16)

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    weather_temp = await select_weather_monthly(city)
    
    return {'City': city.city, 'State': city.state, 'weather_temperature': weather_temp}


@router.post("/api/weather_conditions")
async def get_weather_conditions(city: City):
    """Retrieve weather conditions sunny/cloudy/rainy/snowy days for target city
       Average number of days based on 4 year historical data (from 2017-01-01 to 2020-12-31)

    Fetch data from DB

    args:
        city: The target city

    returns:
        Dictionary that contains the requested data, which is converted
        by fastAPI to a json object.
    """
    city = validate_city(city)
    weather_cond = await select_weather_conditions(city)
    
    return {'City': city.city, 'State': city.state, 'weather_conditions': weather_cond}


# Code scrapper to get jobs
def get_user_city_job(job_input, city_input, state_input):
    splitjob = job_input.split()
    splitcity = city_input.split()
    add_job_to_url = '+'.join(splitjob)
    add_city_to_url = '+'.join(splitcity)
    URL = 'https://www.indeed.com/jobs?q=' + add_job_to_url + '&l=' + add_city_to_url + '&2C' + state_input
    page = requests.get(URL)
    soup = bs(page.text, 'html.parser')
    jobs = []
    for div in soup.find_all(name='div', attrs={'class':'row'}):
        for a in div.find_all(name='a', attrs={'data-tn-element':'jobTitle'}):
            jobs.append(a['title'])
    return(jobs)


@router.post("/api/jobs")
async def get_jobs(job: str, city: str, state: str):
    """Retrieve jobs for target city
    Uses Beautiful Soup 
    args:
        
        job: The Job type i.e. Nurse, Software Engineer, Chef etc.
        
        city: Your City that you're looking for jobs in.

        state: Your State capitalized 2 letter abbreviation code.
    returns:
        List of the current job openings for that city, which is converted
            by fastAPI to a json object.
    """

    list_of_jobs = get_user_city_job(job, city, state)

    return {
        'scraped_jobs': list_of_jobs
        }
