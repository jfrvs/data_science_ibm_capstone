import requests
import pandas as pd
import numpy as np
import datetime

def get_urls():
    """Returns a list of URLs from a specific file in the project directory structure (data/external/)"""
    urls = []

    with open('data/external/urls.txt', 'r') as file:
        for line in file:
            urls.append(line.strip())

    return urls

def get_data_from_url(index):
    """Sends HTTP request to URL depending on the index entered as argument (check data/external/urls.txt for info)"""
    urls = get_urls()
    return requests.get(urls[index])

def get_dataframe_from_response(response):
    """Extracts dataframe from response object"""
    return pd.json_normalize(response.json())

def filter_dataframe(df):
    """Clean response dataframe"""

    df = df[['rocket', 'payloads', 'launchpad', 'cores', 'flight_number', 'date_utc']]
    df = df[df['cores'].map(len)==1]
    df = df[df['payloads'].map(len)==1]
    df['cores'] = df['cores'].map(lambda x : x[0])
    df['payloads'] = df['payloads'].map(lambda x : x[0])
    df['date'] = pd.to_datetime(df['date_utc']).dt.date
    return df[df['date'] <= datetime.date(2020, 11, 13)]

def etl(response_df):
    BoosterVersion = []
    PayloadMass = []
    Orbit = []
    LaunchSite = []
    Outcome = []
    Flights = []
    GridFins = []
    Reused = []
    Legs = []
    LandingPad = []
    Block = []
    ReusedCount = []
    Serial = []
    Longitude = []
    Latitude = []

    print("Beginning Rocket Data Treatment...")

    for x in response_df['rocket']:
       if x:
        response = requests.get("https://api.spacexdata.com/v4/rockets/"+str(x)).json()
        BoosterVersion.append(response['name'])

    print("Beginning Launchpad Data Treatment...")
    for x in response_df['launchpad']:
       if x:
         response = requests.get("https://api.spacexdata.com/v4/launchpads/"+str(x)).json()
         Longitude.append(response['longitude'])
         Latitude.append(response['latitude'])
         LaunchSite.append(response['name'])

    print("Beginning Payload Data Treatment...")
    for load in response_df['payloads']:
       if load:
        response = requests.get("https://api.spacexdata.com/v4/payloads/"+load).json()
        PayloadMass.append(response['mass_kg'])
        Orbit.append(response['orbit'])
    
    print("Beginning Core Data Treatment...")
    for core in response_df['cores']:
            if core['core'] != None:
                response = requests.get("https://api.spacexdata.com/v4/cores/"+core['core']).json()
                Block.append(response['block'])
                ReusedCount.append(response['reuse_count'])
                Serial.append(response['serial'])
            else:
                Block.append(None)
                ReusedCount.append(None)
                Serial.append(None)
            Outcome.append(str(core['landing_success'])+' '+str(core['landing_type']))
            Flights.append(core['flight'])
            GridFins.append(core['gridfins'])
            Reused.append(core['reused'])
            Legs.append(core['legs'])
            LandingPad.append(core['landpad'])
    
    print("Building Dataframe...")

    launch_dict = {'FlightNumber': list(response_df['flight_number']),
    'Date': list(response_df['date']),
    'BoosterVersion':BoosterVersion,
    'PayloadMass':PayloadMass,
    'Orbit':Orbit,
    'LaunchSite':LaunchSite,
    'Outcome':Outcome,
    'Flights':Flights,
    'GridFins':GridFins,
    'Reused':Reused,
    'Legs':Legs,
    'LandingPad':LandingPad,
    'Block':Block,
    'ReusedCount':ReusedCount,
    'Serial':Serial,
    'Longitude': Longitude,
    'Latitude': Latitude}

    falcon_df = pd.DataFrame(launch_dict)

    falcon_df.to_csv("data/raw/Falcon_1-9.csv")

    return falcon_df

def final_treatment(falcon_csv):
    falcon_df = pd.read_csv(falcon_csv)

    falcon_df = falcon_df[falcon_df["BoosterVersion"] != "Falcon 1"]

    falcon_df.loc[:,'FlightNumber'] = list(range(1, falcon_df.shape[0]+1))

    falcon_df["PayloadMass"] = falcon_df["PayloadMass"].fillna(falcon_df["PayloadMass"].mean())

    falcon_df.to_csv("data/processed/Falcon_9.csv")

def get_null_landing_pads():
    falcon_df = pd.read_csv("./data/raw/Falcon_1-9.csv")
    return falcon_df["LandingPad"].isnull().count()

def main():


    print(get_null_landing_pads())

if __name__ == "__main__":
    main()