#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 29 13:44:05 2023

@author: joao
"""

from flask import Flask, render_template, request
import pandas as pd
from geopy.geocoders import Nominatim
from scipy.spatial.distance import cdist

app = Flask(__name__)

final_data = pd.read_csv('final_data.csv')
final_data['solar_panel_power_kwh'] = final_data['solar_panel_power_kwh'].astype(float)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    global final_data  
    city = request.form['city']
    geolocator = Nominatim(user_agent="my_app")
    location = geolocator.geocode(city)
    lat = location.latitude
    lon = location.longitude

    new_city = [(lat, lon)]
    distances = cdist(final_data[["latitude", "longitude"]], new_city, metric="euclidean")

    accuracies = []
    for k in range(1, 21):
        nearest_neighbor_indices = distances.argsort(axis=0)[:k, 0]
        actual_month = final_data.iloc[nearest_neighbor_indices]["month"].mode()[0]
        predicted_month = final_data.iloc[nearest_neighbor_indices]["month"].mean()
        accuracy = 100 - abs((predicted_month - actual_month) / actual_month) * 100
        accuracies.append(accuracy)

    predicted_month = final_data.iloc[nearest_neighbor_indices]["month"].mean()
    predicted_hours_of_sun = final_data.iloc[nearest_neighbor_indices]["hours_of_sun"].mean()
    predicted_temperature = final_data.iloc[nearest_neighbor_indices]["temp"].mean()
    predicted_humidity = final_data.iloc[nearest_neighbor_indices]["humidity"].mean()
    predicted_precip = final_data.iloc[nearest_neighbor_indices]["precip"].mean()
    predicted_cloudcover = final_data.iloc[nearest_neighbor_indices]["cloudcover"].mean()
    predicted_avg_mth_en_consumption_house_kwh = final_data.iloc[nearest_neighbor_indices]["avg_mth_en_consumption_house_kwh"].mean()
    predicted_energy_price_eur_kwh = final_data.iloc[nearest_neighbor_indices]["energy_price_eur_kwh"].mean()
    predicted_solar_panel_power_kwh = final_data.iloc[nearest_neighbor_indices]["solar_panel_power_kwh"].mean()
    predicted_solar_panel_price = final_data.iloc[nearest_neighbor_indices]["solar_panel_price"].mean()
    
    new_city_data = {
        "city": city,
        "month": predicted_month,
        "latitude": lat,
        "longitude": lon,
        "hours_of_sun":predicted_hours_of_sun,
        "temp": predicted_temperature,
        "humidity": predicted_humidity,
        "precip": predicted_precip,
        "cloudcover": predicted_cloudcover,
        "avg_mth_en_consumption_house_kwh":predicted_avg_mth_en_consumption_house_kwh,
        "energy_price_eur_kwh":predicted_energy_price_eur_kwh,
        "solar_panel_power_kwh":predicted_solar_panel_power_kwh,
        "monthly_energy_produced_kwh":(predicted_hours_of_sun * predicted_solar_panel_power_kwh *(1 - (predicted_cloudcover / 100)))/1000,
        "montlhy_energy_cost_eur": predicted_avg_mth_en_consumption_house_kwh * predicted_energy_price_eur_kwh,
        "montlhy_solar_panel_cost_saved":((predicted_hours_of_sun * predicted_solar_panel_power_kwh *(1 - (predicted_cloudcover / 100)))/1000)*(predicted_energy_price_eur_kwh),
        "money_saved": round(((((predicted_hours_of_sun * predicted_solar_panel_power_kwh *(1 - (predicted_cloudcover / 100)))/1000)*(predicted_energy_price_eur_kwh))/(predicted_avg_mth_en_consumption_house_kwh * predicted_energy_price_eur_kwh))*100,0),
        "solar_panel_price":predicted_solar_panel_price,
        "years_to_pay_the_solar_panel":(predicted_solar_panel_price/(((predicted_hours_of_sun * predicted_solar_panel_power_kwh *(1 - (predicted_cloudcover / 100)))/1000)*(predicted_energy_price_eur_kwh)))/12
    }
    final_data = final_data.append(new_city_data, ignore_index=True)

    return render_template('resultado.html', city=city, hours_of_sun=predicted_hours_of_sun,
                           temperature=predicted_temperature, humidity=predicted_humidity,
                           precip=predicted_precip,cloudcover=predicted_cloudcover,
                           avg_mth_en_consumption_house_kwh=predicted_avg_mth_en_consumption_house_kwh,
                           energy_price_eur_kwh=predicted_energy_price_eur_kwh,
                           solar_panel_power_kwh=predicted_solar_panel_power_kwh,
                           monthly_energy_produced_kwh=(predicted_hours_of_sun * predicted_solar_panel_power_kwh *(1 - (predicted_cloudcover / 100)))/1000,
                           montlhy_energy_cost_eur= predicted_avg_mth_en_consumption_house_kwh * predicted_energy_price_eur_kwh,
                           montlhy_solar_panel_cost_saved =((predicted_hours_of_sun * predicted_solar_panel_power_kwh *(1 - (predicted_cloudcover / 100)))/1000)*(predicted_energy_price_eur_kwh),
                           money_saved= round(((((predicted_hours_of_sun * predicted_solar_panel_power_kwh *(1 - (predicted_cloudcover / 100)))/1000)*(predicted_energy_price_eur_kwh))/(predicted_avg_mth_en_consumption_house_kwh * predicted_energy_price_eur_kwh))*100,0),
                           solar_panel_price=predicted_solar_panel_price,
                           years_to_pay_the_solar_panel=(predicted_solar_panel_price/(((predicted_hours_of_sun * predicted_solar_panel_power_kwh *(1 - (predicted_cloudcover / 100)))/1000)*(predicted_energy_price_eur_kwh)))/12
                           )

if __name__ == '__main__':
    app.run(debug=True, port=5001)
