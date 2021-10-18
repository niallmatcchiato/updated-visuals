import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd 

import matplotlib.pyplot as plt
import seaborn as sns
import folium 
import squarify
from scipy.interpolate import interp1d
import plotly.express as px

from io import BytesIO
from base64 import b64encode

from functools import wraps
from flask import redirect, url_for, session


def analyze(path):
    output = {}

    try:
        plt.switch_backend('agg')
        data = pd.read_csv(path)
        # settings for plot 1
        plt.rcParams['figure.figsize'] = (16, 8)
        plt.style.use('ggplot')
        sns.countplot(data['Category'], palette = 'gnuplot')
        plt.title('Major Crimes SanFernando', fontweight = 30, fontsize = 20)
        plt.xticks(rotation = 90)
        # generate plot 1
        output['plot_1'] = to_base64(plt)
        plt.clf()


        # settings for plot 2
        plt.style.use('seaborn')
        data['DayOfWeek'].value_counts().head(15).plot.pie(figsize = (15, 15))
        plt.title('Crime count on each day',fontsize = 20)
        plt.xticks(rotation = 90)
        # generate plot 2
        output['plot_2'] = to_base64(plt)
        plt.clf()


        # settings for plot 3
        data['Date'] = pd.to_datetime(data['Date'])
        data['Month'] = data['Date'].dt.month
        plt.style.use('fivethirtyeight')
        plt.rcParams['figure.figsize'] = (15, 8)
        sns.countplot(data['Month'], palette = 'autumn',)
        plt.title('Crimes in each Months', fontsize = 20)
        # generate plot 3
        output['plot_3'] = to_base64(plt)
        plt.clf()


        # settings for plot 4
        color = plt.cm.twilight(np.linspace(0, 5, 100))
        data['Time'].value_counts().head(20).plot.bar(color = color, figsize = (15, 9))
        plt.title('Distribution of crime over the day', fontsize = 20)
        # generate plot 4
        output['plot_4'] = to_base64(plt)
        plt.clf()


        # settings for plot 5
        df = pd.crosstab(data['Category'], data['PdDistrict'])
        color = plt.cm.Greys(np.linspace(0, 1, 10))
        df.div(df.sum(1).astype(float), axis = 0).plot.bar(stacked = True, color = color, figsize = (18, 12))
        plt.title('District vs Category of Crime', fontweight = 30, fontsize = 20)
        plt.xticks(rotation = 90)
        # generate plot 4
        output['plot_5'] = to_base64(plt)
        plt.clf()


        # settings for table
        t = data.PdDistrict.value_counts()
        table = pd.DataFrame(data=t.values, index=t.index, columns=['Count'])
        table = table.reindex(["Sindalan","San Agustin","San Isidro","Alasas"])
        table = table.reset_index()
        table.rename({'index': 'Neighborhood'}, axis='columns', inplace=True)
        # save table to output dictionary
        output['table'] = table.to_dict()

        output['status'] = 'success'
    except Exception as error:
        print(error)
        output['status'] = 'error'

    return output


def to_base64(plt_object):
    temp = BytesIO()
    plt_object.savefig(temp, format='png')
    encoded = b64encode(temp.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{encoded}'


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username') is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
