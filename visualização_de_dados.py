# -*- coding: utf-8 -*-
"""visualização de dados

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1glO749gojIjf6uOTWZwdWm_8Cv8jtqTX

# Código Fonte. Não é necessário ler.

Código para criar um file path para a base central dos dados, e para minerar alguns dados de uma API bastante útil para nós. Também define uma função para extrair dados dessa base secundária.
"""

import pandas as pd
import requests as rq
from collections import Counter
import time

# Load the dataset
file_path = 'Steam Trends 2023 by @evlko and @Sadari - Games Data.csv'
data = pd.read_csv(file_path)
dataCopy = data.copy()

#steamspy test (alternate database)
steamspy_url = "https://steamspy.com/api.php?request=all&page="
ssapp = "https://steamspy.com/api.php?request=appdetails&appid="
spydata = {}
for i in range(74):
  try:
    spydata.update(rq.get(steamspy_url+str(i)).json())
  except:
    continue
data = data.drop(data[data["App ID"] == 2204850].index)

spydata

def ssget(id):
  return rq.get("https://steamspy.com/api.php?request=appdetails&appid="+str(id)).json()

"""Re-estruturação da database central com 65.000+ instâncias para seis novas databases filtradas, usando como principal meio de seleção a quantidade de reviews de cada jogo. <br>
**Threshold 1** -> Jogos acima de 1.500 reviews. *Principal exemplo: Shoppe Keep* <br>
**Threshold 2** -> Jogos acima de 3.000 reviews. *Principal exemplo: Owlboy* <br>
**Threshold 4** -> Jogos acima de 10.000 reviews. *Principal exemplo: Fear & Hunger* <br>
**Threshold 5** -> Jogos acima de 15.000 reviews. *Principal exemplo: Darkwood* <br>
**Threshold 6** -> Jogos acima de 30.000 reviews. *Principal exemplo: Fallout 3* <br>
"""

#several thresholds. for testing with multiple types of games
datath1 = data.drop(data[data['Reviews Total'] < 1501].index)
datath2 = data.drop(data[data['Reviews Total'] < 3101].index)
datath4 = data.drop(data[data['Reviews Total'] < 10001].index)
datath5 = data.drop(data[data['Reviews Total'] < 15001].index)
datath6 = data.drop(data[data['Reviews Total'] < 30001].index)

"""Implementação, no **Threshold 1**, de uma nova nova coluna 'developer' que relaciona cada jogo com sua equipe desenvolvedora."""

list_of_devs = []
for index, row in datath1.iterrows():
  id = row['App ID']
  if str(id) in spydata:
    dev = spydata[str(id)]["developer"]
  else:
    app = rq.get(ssapp + str(id)).json()
    dev = app["developer"]
  list_of_devs.append(dev)
datath1.insert(14, "developer", list_of_devs, True)

"""Quantificação de para quantos jogos cada tag está aplicada. Usa **Threshold 2**."""

X = datath2.iloc[:, 9]
#for each game split tags and appends the first one to a list.
#then, counts which tags are most popular.
TAGS = list()
for i in range(0, len(X)):
    tag = X[i]
    split_tags = tag.split(',')
    for j in range(0, len(split_tags)):
      TAGS.append(split_tags[j].strip().lower())
count = dict(Counter(TAGS))
sorted_tagcount = sorted(count.items(), key=lambda item: item[1], reverse=True)

"""Dicionários contendo, por tag, a quantidade de instâncias de cada ano/preço/nota/reviewcount. Usa **Threshold 6**."""

#creates timelines for each tag, to be viewed in a graph
tag_years = {}
tag_prices = {}
tag_scores = {}
tag_reviewcount = {}
for index, row in datath6.iterrows():
  for tag in row['Tags'].split(','):
    tag = tag.strip().lower()
    # create three dictionaries to record each
    # tag's year, score and price distribution
    if tag not in tag_years:
      tag_years[tag] = {}
      tag_prices[tag] = {}
      tag_scores[tag] = {}
      tag_reviewcount[tag] = {}

    if row['Release Date'][:4] not in tag_years[tag]:
      tag_years[tag][row['Release Date'][:4]] = 0
    tag_years[tag][row['Release Date'][:4]] += 1
    if row['Launch Price'] not in tag_prices[tag]:
      tag_prices[tag][row['Launch Price']] = 0
    tag_prices[tag][row['Launch Price']] += 1
    if row['Reviews Score Fancy'] not in tag_scores[tag]:
      tag_scores[tag][row['Reviews Score Fancy']] = 0
    tag_scores[tag][row['Reviews Score Fancy']] += 1
    if row['Reviews Total'] not in tag_reviewcount[tag]:
      tag_reviewcount[tag][row['Reviews Total']] = 0
    tag_reviewcount[tag][row['Reviews Total']] += 1

tag_prices['nsfw']

"""Dicionários contendo, por desenvolvedora, a quantidade de instâncias de cada ano/preço/nota/reviewcount. Usa **Threshold 1**."""

#creates timelines for each tag, to be viewed in a graph
dev_years = {}
dev_prices = {}
dev_scores = {}
dev_reviewcount = {}
for index, row in datath1.iterrows():
  developer = row['developer']
  # create three dictionaries to record each
  # tag's year, score and price distribution
  if developer not in dev_years:
    dev_years[developer] = {}
    dev_prices[developer] = {}
    dev_scores[developer] = {}
    dev_reviewcount[developer] = {}

  if row['Release Date'][:4] not in dev_years[developer]:
    dev_years[developer][row['Release Date'][:4]] = 0
  dev_years[developer][row['Release Date'][:4]] += 1
  if row['Launch Price'] not in dev_prices[developer]:
    dev_prices[developer][row['Launch Price']] = 0
  dev_prices[developer][row['Launch Price']] += 1
  if row['Reviews Score Fancy'] not in dev_scores[developer]:
    dev_scores[developer][row['Reviews Score Fancy']] = 0
  dev_scores[developer][row['Reviews Score Fancy']] += 1
  if row['Reviews Total'] not in dev_reviewcount[developer]:
    dev_reviewcount[developer][row['Reviews Total']] = 0
  dev_reviewcount[developer][row['Reviews Total']] += 1

# sorted(dev_reviewcount['Valve'].items())

tag_histogram = {}
for tag in tag_prices:
  if len(tag_prices[tag]) > 50:
    avg = 0
    for price in tag_prices[tag]:
      avg += tag_prices[tag][price]*price
    tag_histogram[tag] = avg/len(tag_prices[tag])
sorted_tag_histogram = sorted(tag_histogram.items(), key=lambda item: item[1], reverse=True)
sorted_tag_histogram

"""# Funções e variáveis básicas que eu desenvolvi e que são úteis.
Melissa, importante ler isso aqui se você nao quiser ter que fazer tudo de novo!!
<br> <br>

"""

# função que retorna dados de um appid pela base secundária
ssget('20')

# cinco bases de dados com escolhas diferentes de onde cortar
# e de até onde filtrar.
datath1 #coluna exclusiva 'developer'. adicionei apenas nessa base
datath2
datath4
datath5
datath6

# um dicionário ordenado, onde cada tag possui um valor.
# este valor representa o número de instâncias com essa tag.
sorted_tagcount

dev_years['Valve']
dev_prices['Valve']
dev_scores['Valve']
dev_reviewcount['Valve']

tag_years['indie']
tag_prices['indie']
tag_scores['indie']
tag_reviewcount['indie']

"""Acessar `dev_years['Valve']` assim como eu acessei vai retornar um dicionário com cada ano onde a *Valve* lançou um jogo, e um valor igual ou maior a 1 representando a quantidade de jogos lançados pela *Valve* nesse ano.

Acessar `dev_prices['Valve']` vai retornar outro dicionário, igual. A diferença é que as chaves agora são preços. Os valores continuam representando a quantidade de vezes que esse preço específico foi usado em um jogo da *Valve*.

`tag_years['indie']` faz a mesma coisa, porém agrupando jogos do gênero indie ao invés de jogos desenvolvidos pela *Valve*.

---


A implementação: Oito dicionários. Os dicionarios que começam com "dev" possuem como chaves os nomes de cada desenvolvedora dentro da TH1. como valores, eles tem mais outros dicionários próprios. esses dicionarios próprios possuem chaves onde cada uma é uma string de year, por exemplo, 2010. e o valor correspondente é a quantidade de vezes que essa string apareceu associada a esse dev.

# Parte de Melissa
"""

tag_scores['indie']

"""## Preço Médio"""

import plotly.express as px
import matplotlib.pyplot as plt

def price_to_float(price_str):
    return float(price_str.replace('$', '').replace(',', '.').replace(' ', ''))


# Calcular a média dos preços para cada tag
tag_avg_prices = {}
for tag, price_dict in tag_prices.items():
    total_price = 0
    total_count = 0
    for price_str, count in price_dict.items():
        price = price_to_float(price_str)
        total_price += price * count
        total_count += count
    avg_price = total_price / total_count if total_count > 0 else 0
    tag_avg_prices[tag] = avg_price

tag_avg_prices

def price_to_float(price_str):
    return float(price_str.replace('$', '').replace(',', '.').replace(' ', ''))

tag_frequencies = {}
for tag, years in tag_years.items():
    total = 0
    for count in years.values():
        total += count
    tag_frequencies[tag] = total

top_tags = sorted(tag_frequencies, key=tag_frequencies.get, reverse=True)

# Filtrar os dados de preços para incluir apenas os X gêneros mais frequentes
filtered_tag_prices = {}
for tag in tag_prices:
    if tag in top_tags:
        filtered_tag_prices[tag] = tag_prices[tag]

# Calcular a média dos preços para cada um dos 25 gêneros mais frequentes
tag_avg_prices = {}
for tag, price_dict in filtered_tag_prices.items():
    total_price = 0
    total_count = 0
    for price_str, count in price_dict.items():
        price = price_to_float(price_str)
        total_price += price * count
        total_count += count
    avg_price = total_price / total_count if total_count > 0 else 0
    tag_avg_prices[tag] = avg_price

# Converter os dados em um DataFrame para visualização
price_data = [{'Tag': tag, 'Average Price': avg_price} for tag, avg_price in tag_avg_prices.items()]
price_df = pd.DataFrame(price_data)

# Verificar os dados
print(price_df.head(3))
print(price_df.columns)
price_df = price_df.sort_values(by=['Average Price'], ascending=True)

# Criar um histograma interativo
#fig = px.histogram(price_df, x='Tag', y='Average Price', title='Distribuição dos Preços Médios de Lançamento por Gênero', labels={'Tag':'Gênero', 'Average Price':'Preço Médio'})
fig = px.histogram(price_df, x='Average Price',y='Tag', title='Distribuição dos Preços Médios de Lançamento por Gênero', labels={'Tag':'Gênero', 'Average Price':'Preço Médio'})
fig.update_layout(width=1000, height=2000)
fig.show()

# Calcular a soma total dos preços médios
total_avg_price = sum(tag_avg_prices.values())
print(total_avg_price)
# Normalizar os preços médios dividindo pelo total de todos os preços
tag_normalized_prices = {tag: price / total_avg_price for tag, price in tag_avg_prices.items()}


# Converter os dados em um DataFrame para visualização
price_data = [{'Tag': tag, 'Normalized Price': tag_normalized_prices[tag]} for tag in tag_avg_prices]
price_df = pd.DataFrame(price_data)


print(price_df.head(22))
print(price_df.columns)

fig = px.bar(price_df, x='Tag', y='Normalized Price', title='Distribuição Normalizada dos Preços Médios de Lançamento por Gênero', labels={'Tag':'Gênero', 'Normalized Price':'Preço Normalizado'})
#fig.update_layout(width=1000, height=2000)
fig.show()



import pandas as pd
import plotly.express as px


# Calcular a média dos scores para cada gênero
tag_avg_scores = {}
for tag, scores_dict in tag_scores.items():
    total_score = 0
    total_count = 0
    for year, score in scores_dict.items():
        total_score += score
        total_count += 1
    avg_score = total_score / total_count if total_count > 0 else 0
    tag_avg_scores[tag] = avg_score

# Calcular a soma total dos scores médios
total_avg_score = sum(tag_avg_scores.values())

# Normalizar os scores médios dividindo pelo total de todos os scores
tag_normalized_scores = {tag: score / total_avg_score for tag, score in tag_avg_scores.items()}

# Converter os dados em um DataFrame para visualização
score_data = [{'Tag': tag, 'Average Score': tag_avg_scores[tag], 'Normalized Score': tag_normalized_scores[tag]} for tag in tag_avg_scores]
score_df = pd.DataFrame(score_data)


print(score_df.head(25))
print(score_df.columns)

fig = px.bar(score_df, x='Tag', y='Normalized Score', title='Distribuição Normalizada dos Scores Médios por Gênero (Dividido pela Soma Total)', labels={'Tag':'Gênero', 'Normalized Score':'Score Normalizado'})
fig.show()

def score_to_float(price_str):
    return float(price_str.replace('%', '').replace(',', '.').replace(' ', ''))

tag_frequencies = {}
for tag, years in tag_years.items():
    total = 0
    for count in years.values():
        total += count
    tag_frequencies[tag] = total

top_tags = sorted(tag_frequencies, key=tag_frequencies.get, reverse=True)[:25]

# Filtrar os scores para incluir apenas os X gêneros mais frequentes
filtered_tag_scores = {}
for tag in tag_scores:
    if tag in top_tags:
        filtered_tag_scores[tag] = tag_scores[tag]

# Calcular a média dos preços para cada um dos 25 gêneros mais frequentes
tag_avg_scores = {}
for tag, scores_dict in filtered_tag_scores.items():
    total_score = 0
    total_count = 0
    for year, score in scores_dict.items():
        total_score += score
        total_count += 1
    avg_score = total_score / total_count if total_count > 0 else 0
    tag_avg_scores[tag] = avg_score

# Calcular a soma total dos scores médios
total_avg_score = sum(tag_avg_scores.values())

# Normalizar os scores médios dividindo pelo total de todos os scores
tag_normalized_scores = {tag: score / total_avg_score for tag, score in tag_avg_scores.items()}

# Converter os dados em um DataFrame para visualização
score_data = [{'Tag': tag, 'Average Score': tag_avg_scores[tag], 'Normalized Score': tag_normalized_scores[tag]} for tag in tag_avg_scores]
score_df = pd.DataFrame(score_data)

# Verificar os dados
print(score_df.head(3))
print(score_df.columns)

# Criar um gráfico de barras interativo para os scores normalizados
fig = px.bar(score_df, x='Tag', y='Normalized Score', title='Distribuição Normalizada dos Scores Médios por Gênero (Dividido pela Soma Total)', labels={'Tag':'Gênero', 'Normalized Score':'Score Normalizado'})

# Exibir o gráfico
fig.show()

# Converter os dados em um DataFrame para visualização
price_data = [{'Tag': tag, 'Average Price': avg_price} for tag, avg_price in tag_avg_prices.items()]
price_df = pd.DataFrame(price_data)

# Verificar os dados
print(price_df.head(25))
print(price_df.columns)

# Criar um histograma interativo
fig = px.histogram(price_df.head(25), x='Average Price', y='Tag', title='Distribuição dos Preços Médios de Lançamento por Gênero', labels={'Tag':'Gênero', 'Average Price':'Preço Médio'})

# Exibir o gráfico
fig.show()

import matplotlib.pyplot as plt

tags_series = datath1['Tags'].str.split(',').explode().str.strip()
top_genres = tags_series.value_counts().head(25)

genres = top_genres.index.tolist()
counts = top_genres.values.tolist()
print(counts)
plt.figure(figsize=(10, 10))
plt.barh(genres, counts, color='skyblue')
plt.xlabel('Frequência')
plt.title('Top 25 Gêneros Mais Frequentes')
plt.gca().invert_yaxis()
plt.show()

import plotly.express as px

tags_count = tags_series.value_counts().nlargest(15).reset_index()
tags_count.columns = ['Tag', 'Count']
print(tags_count)
fig = px.scatter(tags_count, x='Count', y='Tag', size='Count', color='Tag',
                 hover_name='Tag', size_max=60, title='Top 15 Game Genres on Steam')
fig.show()

#datath1['Release Year'] = pd.to_datetime(datath1['Release Date']).dt.year

#expanded_data = datath1.explode('Tags')
#expanded_data = expanded_data[expanded_data['Tags'].isin(genres)]

#games_per_year = expanded_data.groupby(['Release Year', 'Tags']).size().reset_index(name='Count')
#games_per_year = games_per_year[games_per_year['Release Year'] >= 2003]

#fig = px.line(games_per_year, x='Release Year', y='Count', color='Tags', title='Quantidade de Jogos Lançados por Ano por Gênero')
#fig.show()

tags_count = tags_series.value_counts().nlargest(10).reset_index()
tags_count.columns = ['Tag', 'Count']

top_tags = tags_count['Tag'].tolist()

filtered_data = data[data['Tags'].apply(lambda x: any(tag in x for tag in top_tags) if pd.notnull(x) else False)]
filtered_data['Release Year'] = pd.to_datetime(filtered_data['Release Date'], errors='coerce').dt.year
filtered_data['Tags'] = filtered_data['Tags'].apply(lambda x: x.split(', ') if pd.notnull(x) else [])

expanded_data = filtered_data.explode('Tags')
expanded_data = expanded_data[expanded_data['Tags'].isin(top_tags)]

games_per_year = expanded_data.groupby(['Release Year', 'Tags']).size().reset_index(name='Count')
games_per_year = games_per_year[games_per_year['Release Year'] <= 2020]
games_per_year = games_per_year[games_per_year['Release Year'] >= 2000]

fig = px.line(games_per_year, x='Release Year', y='Count', color='Tags', title='Quantidade de Jogos Lançados por Ano por Gênero', log_y= True)
fig.show()

import pandas as pd
import plotly.express as px
# Filtrar os dados para a tag 'Indie'
filtered_data = data[data['Tags'].apply(lambda x: 'Indie' in x if pd.notnull(x) else False)]

# Extrair o ano de lançamento
filtered_data['Release Year'] = pd.to_datetime(filtered_data['Release Date'], errors='coerce').dt.year

# Explodir a coluna 'Tags' para ter uma linha por tag
filtered_data['Tags'] = filtered_data['Tags'].apply(lambda x: x.split(', ') if pd.notnull(x) else [])
expanded_data = filtered_data.explode('Tags')

# Filtrar para manter apenas a tag 'Indie'
expanded_data = expanded_data[expanded_data['Tags'] == 'Indie']

games_per_year = expanded_data.groupby(['Release Year', 'Tags']).size().reset_index(name='Count')
games_per_year = games_per_year[(games_per_year['Release Year'] <= 2020) & (games_per_year['Release Year'] >= 2000)]


fig = px.line(games_per_year, x='Release Year', y='Count', title='Quantidade de Jogos Indie Lançados por Ano')
fig.show()

"""# Distribuições e Correlações"""

# Import
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
file_path = 'Steam Trends 2023 by @evlko and @Sadari - Games Data.csv'
dataCopy = pd.read_csv(file_path)

# data treating
dataCopy['Launch Price'] = dataCopy['Launch Price'].apply(lambda x: float(x.replace('\xa0','').replace('$' ,'').replace(',','.')))
dataCopy['Release Date'] = pd.to_datetime(dataCopy['Release Date'])
dataCopy['Revenue Estimated'] = dataCopy['Revenue Estimated'].apply(lambda x: float(x.replace('\xa0','').replace('$','').replace(',','.')))
dataCopy['Reviews Score Fancy'] = dataCopy['Reviews Score Fancy'].apply(lambda x: float(x.replace('%' ,'').replace(',','.')))

# remoção de outliers
spooky_men_id = 2204850
cs_id = 730
pubg_id = 578080
main_outliers_ids = [spooky_men_id , cs_id]
dataCopy = dataCopy[-dataCopy['App ID'].isin(main_outliers_ids)]
dataCopy = dataCopy[dataCopy['Release Date'].dt.year > 1980]
dataCopy = dataCopy[dataCopy['Launch Price'] < 170]

#several thresholds. for testing with multiple types of games
datath1_c = dataCopy.drop(dataCopy[dataCopy['Reviews Total'] < 1501].index)
datath2_c = dataCopy.drop(dataCopy[dataCopy['Reviews Total'] < 3101].index)
datath4_c = dataCopy.drop(dataCopy[dataCopy['Reviews Total'] < 10001].index)
datath5_c = dataCopy.drop(dataCopy[dataCopy['Reviews Total'] < 15001].index)
datath6_c = dataCopy.drop(dataCopy[dataCopy['Reviews Total'] < 30001].index)

fig = make_subplots(rows=2,cols=2 , subplot_titles=[
    "Launch Price",
    "Number of Reviews",
    "Revenue Estimated",
    "Release Date"
])


fig.add_trace(go.Histogram(
    x=datath1_c["Launch Price"],
    name="Launch Price",
    # hovertemplate=datath1_c["Title"],
    ),row=1,col=1)
fig.add_trace(go.Histogram(x=datath6_c["Reviews Total"],name="Number of Reviews"), row=1, col=2)
fig.add_trace(go.Histogram(x=datath1_c["Revenue Estimated"],name="Revenue"), row=2, col=1)
fig.add_trace(go.Histogram(x=datath1_c["Release Date"],name="Release"), row=2, col=2)

fig.show()

target_dists = ['Reviews Total', 'Reviews Score Fancy','Launch Price', 'Revenue Estimated']
fig = px.scatter_matrix(datath1_c,
                        dimensions = target_dists,
                        labels = {'Reviews Total':'reviews' ,'Reviews Score Fancy': 'score(%)' , 'Launch Price':'price','Revenue Estimated':'revenue'},
                        title='Correlation between attributes with outliers')
fig.show()

spooky_men_id = 2204850
cs_id = 730
pubg_id = 578080
main_outliers_ids = [spooky_men_id , cs_id]


dataNoOutliers = datath1_c[-datath1_c['App ID'].isin(main_outliers_ids)]
target_dists = ['Reviews Total', 'Reviews Score Fancy','Launch Price', 'Revenue Estimated']
fig = px.scatter_matrix(dataNoOutliers,
                        dimensions = target_dists,
                        labels = {'Reviews Total':'reviews' ,
                                  'Reviews Score Fancy': 'score(%)' ,
                                  'Launch Price':'price',
                                  'Revenue Estimated':'revenue'
                                  },
                        title='Correlation between attributes without outliers'
                        )

# dataCopy.sort_values(by=['Reviews Total'], ascending=False)

"""

*   Existem muitos jogos entre 0 e 100 dolares
*   Existem jogos com poucas reviews de mais de 250 dolares

"""

dataNoOutliers.sort_values(by=[''])

# dataCopy['Release Date'].dt.day
months = ['January','February','March','April','May','June','July', 'August','September','October', 'November','December']
days = [x for x in range(1,32)]

# expanded days and month columns
dataCopy['Month'] = dataCopy['Release Date'].dt.month_name()
dataCopy['Day'] = dataCopy['Release Date'].dt.day.astype(int)
dayGroupedData = dataCopy.groupby(['Month','Day']).size().reset_index().pivot(index='Month',columns='Day').fillna(0)
dayGroupedData = dayGroupedData.reindex(index=months)
dayGroupedData = dayGroupedData.astype(int)
dayGroupedData = dayGroupedData.to_numpy()
dateDataframe = pd.DataFrame(data=dayGroupedData,
                              index=months,
                              columns=days)

def makeplot():
  fig = px.imshow(dateDataframe,
                  x=dateDataframe.columns,
                  y=dateDataframe.index,
                  labels=dict(x="Day", y="Month", color="Number of games launched")
                  )
  fig.update_xaxes(side="bottom")
  fig.show()

makeplot()

# selection debug
dataCopy[(dataCopy['Day'] == 1) & (dataCopy['Month'] == months[0])].shape[0]

# baixar notebook , upar na session storage e executar o codigo:

# %%shell
# jupyter nbconvert --to html /content/visualização_de_dados.ipynb

def a():
  return (132 , 4 , 89 , 123)

(
    dd,
    b,
    c,
    d
) = a()

print(dd)