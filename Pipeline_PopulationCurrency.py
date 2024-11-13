import requests 
import pandas as pd
from dotenv import load_dotenv
import os


class APIclient:
    def __init__(self, url, params=None, API_key=None):
        self.url = url
        self.params = params
        self.API_key = API_key
    
    def get_method(self):
        headers = {'Authorization': f'Bearer {self.API_key}'} if self.API_key else {}
        response = requests.get(self.url, params = self.params, headers = headers)
        # print(response.url)
        if response.status_code == 200:
            return response.json()
        
        print('Failed operation. Status code: {}'.format(response.status_code))


class Population_pipeline:
    def __init__(self, year, n_countries, data):
        self.year = year
        self.n_countries = n_countries
        self.data = data 

    def create_df(self):

        # Check if the response has more than 1 element and number of pages more than 0
        if len(self.data) <= 1 or self.data[0]['page'] < 1:
            print('There is no information for the specified year ({})'.format(self.year))
            exit()

        # Separate data and metadata
        metadata = self.data[0]
        info = self.data[1]

        # Filter data to columns of interest (country code, country and population)
        filtered_data = [
        {
            'Country Code': item['countryiso3code'],
            'Country': item['country']['value'],
            'Population': item['value']
        }
        for item in info[49:]  # Iterate over elements from data (countries)
        ]
        
        # Check if the number of countries required by the user exceeds the total number of countries
        if self.n_countries > metadata['total']:
            print(f"There are only {metadata['total']} countries")
            self.n_countries = metadata['total'] 
        
        # Create DF and transform data 
        df = pd.DataFrame(filtered_data)
        sorted_df = df.sort_values(by ='Population', ascending=False).iloc[:self.n_countries].reset_index(drop=True)
        sorted_df = sorted_df.fillna(0).astype({'Population':'int32'})
        
        # Print Top n counties by population
        print(f'Top {self.n_countries} countries by Population in year {self.year}')
        print(sorted_df)
        return sorted_df
    

class Currency_pipeline:
    def __init__(self, data_currency, df_population):
        self.data = data_currency
        self.df = df_population

    def add_currency(self):

        # Filter data to columns of interest (country code and currencies)
        filtered_data = {
        item['cca3']:list(item['currencies'].keys())[0] if len(list(item['currencies'].keys())) else '-'
        
        for item in self.data 
        }  # Iterate over countries

        # Add currency column to population df
        self.df['Currency'] = self.df['Country Code'].map(filtered_data)
        return self.df


class Exchange_pipeline:
    def __init__(self, data_exchange):
        self.data = data_exchange
    
    def add_exchangerate(self, df_currency):

        # Filter data to column of interest (conversion rates) and add column to currency df
        exchange = self.data['conversion_rates']
        df_currency['Conversion Rate'] = df_currency['Currency'].map(exchange)
        return df_currency
    
    def print_penny(self, df_exchange, year):

        # Print exchange df (country code, name, population, currency, conversion rate)
        print('----------------------------------')
        print('Exchange rate from mxn to local coin of specified countries')
        print(df_exchange)

        # Obtain the total in mxn if every country gives you 1 penny of their local coin
        total_money = ((df_exchange['Population']/df_exchange['Conversion Rate']).sum()) * 0.01 
        print(f"""Considering the population in those countries in year {year}. If each of them gives you 1 penny of their local 
coin (current exchange rate), you will have: ${round(total_money, 2):,} MXN""")

def user_input():
    # Validate user input (integer numbers)
    try:
        year = abs(int(input('From which year do you want to obtain the population? ')))
        n_countries = abs(int(input('How many countries do you want to visualize? ')))
        if n_countries < 1:
            print("The number of cuntries needs to be more than 0.")
            exit()
        return year, n_countries

    except ValueError:
        print("That's not an integer number")
        exit()


# Main Program

if __name__ == "__main__":
    # Get user input
    year, n_countries = user_input()

    # Define params of the population URL for API Client
    params_population = {
        'date' : year,
        'format' : 'json',
        'per_page' : 266, 
    }
    url_population = 'https://api.worldbank.org/v2/country/all/indicator/SP.POP.TOTL'

    # Create APIclient object from poupulation API and obtain data 
    client_population = APIclient(url_population, params_population)
    data_population = client_population.get_method()

    # Create Population pipeline object and obtain dataframe with top n countries
    pipe_population = Population_pipeline(year, n_countries, data_population) 
    df_population = (pipe_population.create_df())



    # Define params of the currency URL for API Client
    params_currency = {
        'fields' : 'cca3,currencies'
    }
    url_currency = 'https://restcountries.com/v3.1/all'

    # Create APIclient object from currency API and obtain data 
    client_currency = APIclient(url_currency, params_currency)
    data_currency = client_currency.get_method()

    # Create Currency pipeline object
    pipe_currency = Currency_pipeline(data_currency, df_population) 
    df_currency = (pipe_currency.add_currency())



    # Prepare key and URL for API exchange rate Client

    # Load environment variables from .env file
    load_dotenv()

    # Get the API key
    API_exchange_key = os.getenv('API_KEY')
    url_exchange = 'https://v6.exchangerate-api.com/v6/latest/MXN'

    # Create APIclient object from exchange rate  API and obtain data 
    client_exchange = APIclient(url_exchange, API_key=API_exchange_key)
    data_exchange = client_exchange.get_method()

    # Create Exchange rate pipeline object
    pipe_exchange = Exchange_pipeline(data_exchange) 
    df_exchange = (pipe_exchange.add_exchangerate(df_currency))

    pipe_exchange.print_penny(df_exchange, year)
