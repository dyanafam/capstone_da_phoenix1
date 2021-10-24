from operator import add
from flask import Flask, render_template
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

from io import BytesIO
import base64
from bs4 import BeautifulSoup 
import requests

#don't change this
matplotlib.use('Agg')
app = Flask(__name__) #do not change this

#insert the scrapping here
url_get = requests.get('https://www.imdb.com/search/title/?release_date=2021-01-01,2021-12-31')
soup = BeautifulSoup(url_get.content,"html.parser")

#find your right key here
table = soup.find('div', attrs={'class':'lister-list'})

row = table.find_all('h3', attrs={'class':'lister-item-header'})
row_length = len(row)

temp = [] #initiating a list 
#insert the scrapping process here
for i in range(0, row_length):
    try: 
        judul = table.find_all('h3', attrs={'class':'lister-item-header'})[i].a.text.strip()
    except Exception as e:
        judul = "N/A"
    try:
        imdb_rating = table.find_all('div', attrs={"class": "inline-block ratings-imdb-rating"})[i].strong.text
    except Exception as e:
        imdb_rating = "N/A"
    try:
        metascore = table.find_all("span", attrs={"class": "metascore favorable"})[i].text
    except Exception as e:
        metascore = "N/A"
    try:
        votes = table.find_all("span", attrs={"name": "nv"})[i].text
    except Exception as e:
        votes = "N/A"
    temp.append((judul, imdb_rating, metascore, votes))
# apppend: masukin hasil dari looping di i ke temp
temp 

import numpy as np
import pandas as pd 
from matplotlib import rcParams
#change into dataframe
df = pd.DataFrame(temp, columns = ('judul', 'imdb_rating', 'metascore', 'votes')).replace('N/A',np.NaN)

#insert data wrangling here
df = df.set_index('judul')
df['imdb_rating'] = df['imdb_rating'].astype('float64')
df['metascore'] = df['metascore'].astype('float64')
df['votes'] = df['votes'].str.replace(",","")
df['votes'] = df['votes'].astype('float64')
df['votes'] = df['votes']/10000
df['metascore'] = df['metascore']/10
df.rename(columns = {"votes":"votes ('0.000)"}, inplace = True)
df.rename(columns = {"metascore": "metascore ('0)"}, inplace = True)

#end of data wranggling 

@app.route("/")
def index(): 
	
	card_data = f'{df["imdb_rating"].mean().round(2)}' #be careful with the " and ' 
	
# rata rata dari metascore misalnya^
	# generate plot
	ax = df.sort_values("votes ('0.000)", ascending=False).head(20).plot.barh(figsize = (12,9))
	
    # Rendering plot
	# Do not change this
	figfile = BytesIO()
	plt.savefig(figfile, format='png', transparent=True)
	figfile.seek(0)
	figdata_png = base64.b64encode(figfile.getvalue())
	plot_result = str(figdata_png)[2:-1]

	# render to html
	return render_template('index.html',
		card_data = card_data, 
		plot_result=plot_result
		)


if __name__ == "__main__": 
    app.run(debug=True)