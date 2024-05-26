import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from flask import Flask, render_template, request
import plotly.offline as pyo

app = Flask(__name__)

# Load the data
df = pd.read_csv('road_death_2019.csv')
df['road traffic death rate'] = pd.to_numeric(df['road traffic death rate'], errors='coerce')
df['year'] = pd.to_numeric(df['year'], errors='coerce')

# Helper function to create a line plot
def create_line_plot(data, x, y, title, color=None):
    fig = px.line(data, x=x, y=y, color=color, title=title)
    return fig

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/trends')
def trends():
    yearly_trend = df.groupby('year')['road traffic death rate'].mean().reset_index()
    fig = create_line_plot(yearly_trend, 'year', 'road traffic death rate', 'Average Road Traffic Death Rate Over Years')
    graph_html = pyo.plot(fig, include_plotlyjs=False, output_type='div')
    return render_template('trends.html', graph_html=graph_html)

@app.route('/continent_trends')
def continent_trends():
    continent_trend = df.groupby(['year', 'continent'])['road traffic death rate'].mean().reset_index()
    fig = create_line_plot(continent_trend, 'year', 'road traffic death rate', 'Road Traffic Death Rate by Continent Over Years', color='continent')
    graph_html = pyo.plot(fig, include_plotlyjs=False, output_type='div')
    return render_template('continent_trends.html', graph_html=graph_html)

@app.route('/country_comparison')
def country_comparison():
    country_avg = df.groupby('country')['road traffic death rate'].mean().reset_index()
    top_10_countries = country_avg.sort_values(by='road traffic death rate', ascending=False).head(10)
    bottom_10_countries = country_avg.sort_values(by='road traffic death rate', ascending=True).head(10)

    fig = make_subplots(rows=1, cols=2, subplot_titles=("Top 10 Countries", "Bottom 10 Countries"))

    fig.add_trace(
        go.Bar(x=top_10_countries['road traffic death rate'], y=top_10_countries['country'], orientation='h', name='Top 10', marker=dict(color='red')),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(x=bottom_10_countries['road traffic death rate'], y=bottom_10_countries['country'], orientation='h', name='Bottom 10', marker=dict(color='blue')),
        row=1, col=2
    )

    fig.update_layout(title_text="Country Comparison")

    graph_html = pyo.plot(fig, include_plotlyjs=False, output_type='div')
    return render_template('country_comparison.html', graph_html=graph_html)

@app.route('/continent_comparison', methods=['GET', 'POST'])
def continent_comparison():
    continents = df['continent'].unique()
    selected_continents = request.form.getlist('continents')

    if selected_continents:
        filtered_df = df[df['continent'].isin(selected_continents)]
        fig = create_line_plot(filtered_df, 'year', 'road traffic death rate', 'Continent Comparison', color='continent')
    else:
        fig = create_line_plot(df, 'year', 'road traffic death rate', 'Continent Comparison', color='continent')

    graph_html = pyo.plot(fig, include_plotlyjs=False, output_type='div')
    return render_template('continent_comparison.html', graph_html=graph_html, continents=continents, selected_continents=selected_continents)

if __name__ == '__main__':
    app.run(debug=True)
