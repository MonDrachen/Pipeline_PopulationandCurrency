# Global Population and Conversion Currency Pipeline

Global Population and Currency Conversion Data Pipeline

**Description:**
This project involved building a robust data pipeline in Python to handle and analyze global population data using APIs from the World Bank and a currency exchange service. The pipeline was designed to extract, process, and calculate potential currency accumulations from a hypothetical scenario (receiving one cent of the local coin from every people of the analyzed countries).

Key Features:

Data Extraction:

Implemented a module that connects to the World Bank's API to retrieve population data for various countries.
Integrated a parameter to allow the selection of the top N countries by population, which enhances flexibility in data retrieval and analysis.
Data Processing:

Developed a function to process the extracted data and store it in a Pandas DataFrame for easy manipulation and analysis.
Currency Conversion:

Implemented a module to retrieve the latest exchange rates, specifically to convert from various international currencies to Mexican pesos.
The pipeline calculates how much would be accumulated if every person in each selected country contributed one cent of their currency, converting the total to Mexican pesos.
Modular and Readable Code:

Employed object-oriented programming principles to make the code efficient, reusable, and easy to read.
Prioritized clear documentation and modularity to ensure that each component of the pipeline is standalone and can be easily modified or expanded.
Technologies Used:

Python, Pandas, World Bank Indicators API, Currency Conversion API (Fixer or equivalent)
