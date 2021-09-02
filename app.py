import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import re
from datetime import date
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

# external Css files
external_stylesheets = ['assets/style.css']
# external JavaScript files
external_scripts = [
    {'src': 'https://platform.twitter.com/widgets.js'},
]

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP],
				 external_scripts=external_scripts)

#read input file
df = pd.read_csv("tweets.csv");

#make a copy of dataframe
maindata=df.copy(deep=True) 

#chnage date of tweet to yeat-month so we can take number of tweets in a month
maindata["post_date"] = pd.to_datetime(maindata["post_date"],unit='s').dt.strftime('%Y-%m')

#data group byth year/month and company name
data_main_plot=maindata.groupby(['post_date','company_name'])['post_date'].count().reset_index(name="Number of tweets")

#count tweets
counts=data_main_plot.groupby(['company_name'])['Number of tweets'].sum()

#Pie chart
pie_data=pd.DataFrame({'count' : maindata.groupby( [ "company_name"] ).size()}).reset_index()
fig = px.pie(pie_data, values='count', names='company_name',color="company_name")

fig.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
))


#main plots

main_figure = px.line(data_main_plot, x="post_date", y="Number of tweets",color="company_name")
main_figure_bar = px.bar(data_main_plot, x="post_date", y="Number of tweets",color="company_name")


main_figure.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
))
main_figure_bar.update_layout(legend=dict(
    orientation="h",
    yanchor="bottom",
    y=1.02,
    xanchor="right",
    x=1,
))

#pie plot div

pie_figu =html.Div(dcc.Graph(
        id='pie_fig',
        figure=fig,
        className="piediv"
    ))


#Dropdown componment div

select_char=html.Div([
    dcc.Dropdown(
        id='dropdown',
        options=[
            {'label': 'Line Chart', 'value': 'line'},
            {'label': 'Bar Chart', 'value': 'Bar'}
        ],
        value='Bar'
    )
])

@app.callback(
    dash.dependencies.Output('plot', 'figure'),
    [dash.dependencies.Input('dropdown', 'value'),
    
    ])
def update_output(value):
	if value=="Bar":
		return main_figure_bar
	else:
		return main_figure





# change date format
df["post_date"] = pd.to_datetime(df["post_date"],unit='s').dt.strftime('%Y-%m-%d')

#first div that contain num of tweets of each company
company_count_div= dbc.Row(
            [dbc.Col([
           		 html.H5(counts.sum()),
            		 html.P("Total"),
    		      ],className=["comp","text-center"]),
            dbc.Col([
           		 html.H5(counts["Google Inc"]),
            		 html.P("Google"),
    		      ],className=["comp","text-center"]),
            dbc.Col([
           		 html.H5(counts["Tesla Inc"]),
            		 html.P("Tesla"),
    		      ],className=["comp","text-center"]),
            dbc.Col([
           		 html.H5(counts["apple"]),
            		 html.P("Apple"),
    		      ],className=["comp","text-center"]),
            dbc.Col([
           		 html.H5(counts["Amazon.com"]),
            		 html.P("Amazon"),
    		      ],className=["comp","text-center"]),
           dbc.Col([
           		 html.H5(counts["Microsoft"]),
            		 html.P("Microsoft"),
    		      ],className=["comp","text-center"]),
            ],
         className="countsdiv")
 

#pt the main figure in a div
div_main_figue =html.Div(dcc.Graph(
        id='main_figur',
        figure=main_figure,
        className="maindiv"
    ))
    
div_main_figue_bar=html.Div(dcc.Graph(
        id='main_figuue',
        figure=main_figure_bar,
        className="maindiv"
    ))
    
#main div
main=html.Div(dcc.Graph(id = 'plot'))

#datepickRanger    
datepick=html.Div([dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=date(2015,1,1),
        max_date_allowed=date(2019,12,31),

    )])
    
#num max of tweets to show
max_number= html.Div(dcc.Input(
            id="num",
            type="number",
            min=0,
            placeholder="max tweets to show",
        ))
        
#list of company
list_company=html.Div(dcc.Checklist(
id="select_company",
    options=[
    	
        {'label': 'Apple', 'value': 'apple'},
        {'label': 'Google Inc', 'value': 'Google Inc'},
        {'label': 'Tesla', 'value': 'Tesla Inc'},
        {'label': 'Microsoft', 'value': 'Microsoft'},
        {'label': 'Amazon', 'value': 'Amazon.com'}
    ],
    value=[],
    labelStyle={'display': 'inline-block'}
)  )


#put datepickRanger,num of tweets to show and the company list in one div
div_search= dbc.Row([dbc.Col([datepick]),dbc.Col([max_number]),dbc.Col([list_company])],className="searchdiv")


#Trending Hashtags

# this function to normalize the list of hashtags 
def flatten_list(_2d_list):
    flat_list = []
    # Iterate through the outer list
    for element in _2d_list:
        if type(element) is list:
            # If the element is of type list, iterate through the sublist
            for item in element:
                flat_list.append(item)
        else:
            flat_list.append(element)
    return flat_list

lst_hashtags=flatten_list(df['hashtags'])


# Calculate the frequency of each hashtag
frequency = {}
# iterating over the list
for item in lst_hashtags:
   # checking the element in dictionary
   if item in frequency:
      # incrementing the counr
      frequency[item] += 1
   else:
      # initializing the count
      frequency[item] = 1
      
#sort the list of hashtags 
lst_orders = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
#the first ement is empty, and we want to show the first 10 hashtags
trending_hashtags=lst_orders[1:10]

hashtags=html.Ul([html.Li([html.P("#"+key),html.P(str(v)+" Tweets"),html.Hr()]) for key,v in trending_hashtags])
hashtag_header=html.H3("Trending Hashtags",className="title")
Trending_header=html.H3("Trending Tweets",className="title")
#body contain all the divs
body = html.Div(
    [
    company_count_div,
    dbc.Row([dbc.Col([select_char,main],width=8),
    	     dbc.Col([pie_figu],width=4)]),
    div_search,
    dbc.Row([dbc.Col([Trending_header,html.Div(id='trending_tweets',className="overflow-auto")], width=6),
    			dbc.Col([hashtag_header,html.Div([hashtags],id='trending_hashtags')], width=6)
     			
    ]
)

])




app.layout = html.Div([body],className="container")

#function to show trending tweets by number of followers of the author
def trending_tweets(comp="all",start_date="2015-01-01",end_date="2019-12-31",num_of_tweets=10):
	if(comp=="all" or not comp):
		tweets=df[(df['post_date'] >= start_date)&(df['post_date'] <=end_date)].sort_values(by = 'NbFowers',ascending=False).head(num_of_tweets)
	else:
		tweets=df[(df['post_date'] >= start_date)&(df['post_date'] <=end_date)& (df['company_name'].isin(comp))].sort_values(by = 'NbFowers',ascending=False).head(num_of_tweets)
	
	contents = list() 
	for index,tw in tweets.iterrows():
		
		contents.append(html.Div([html.Div(tw['writer']),html.P("-"),html.Div([tw['body']]),html.Div(tw['post_date']),html.Hr()]))	
		
	return contents
	
	
@app.callback(
    Output(component_id='trending_tweets', component_property='children'),
    Input(component_id='my-date-picker-range', component_property='start_date'),
    Input(component_id='my-date-picker-range', component_property='end_date'),
    Input(component_id='num',component_property= 'value'),
    Input(component_id='select_company',component_property= 'value')
)
def update_output(start_date,end_date,num,select_company):
	if ((start_date is not None) and (end_date is not None)):		   	
		start_date_object = date.fromisoformat(start_date)
		start_date_string = start_date_object.strftime('%Y-%m-%d')
		end_date_object = date.fromisoformat(end_date)
		end_date_string = end_date_object.strftime('%Y-%m-%d')
		return trending_tweets(select_company,start_date_string,end_date_string,num)
	else:
		return trending_tweets()

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port=8081)
