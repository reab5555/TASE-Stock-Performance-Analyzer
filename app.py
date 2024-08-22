import gradio as gr
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.colors import n_colors
from datetime import datetime, timedelta


# Load stock data
def load_stocks():
    df = pd.read_csv('TASE_stock_list_2023.csv')
    df['Symbol'] = df['Symbol'] + '.TA'
    return df


# Get stock data and calculate percentage change
def get_stock_data(start_date, end_date, stocks):
    data = {}
    for _, row in stocks.iterrows():
        symbol = row['Symbol']
        name = row['Name']
        stock = yf.Ticker(symbol)
        hist = stock.history(start=start_date, end=end_date)
        if not hist.empty:
            initial_price = hist['Close'].iloc[0]
            final_price = hist['Close'].iloc[-1]
            pct_change = ((final_price - initial_price) / initial_price) * 100
            if pct_change < 100:  # Only include stocks with pct change below 100
                data[symbol] = {
                    'name': name,
                    'initial_price': initial_price,
                    'final_price': final_price,
                    'pct_change': pct_change
                }
    return data


# Create bar chart
def create_chart(data):
    sorted_data = dict(sorted(data.items(), key=lambda x: x[1]['pct_change'], reverse=True)[:80])  # Top 80 stocks

    fig = go.Figure()

    # Generate a color scale from light green to dark green
    colors = n_colors('rgb(144,238,144)', 'rgb(0,100,0)', len(sorted_data), colortype='rgb')

    # Reverse the color order so that higher values get darker colors
    colors = colors[::-1]

    fig.add_trace(go.Bar(
        x=list(sorted_data.keys()),
        y=[v['pct_change'] for v in sorted_data.values()],
        text=[f"{v['pct_change']:.2f}%" for v in sorted_data.values()],
        textposition='inside',
        textfont=dict(color='white'),  # Set text color to white for all bars
        hovertext=[
            f"{v['name']}<br>Symbol: {k}<br>Initial: {v['initial_price']:.2f}<br>Final: {v['final_price']:.2f}<br>Change: {v['pct_change']:.2f}%"
            for k, v in sorted_data.items()],
        hoverinfo='text',
        marker_color=colors
    ))
    title = 'Stocks Performance'
    fig.update_layout(
        title=title,
        xaxis_title='Stocks',
        yaxis_title='Percentage Change',
        hoverlabel=dict(
            bgcolor="black",
            font_size=12,
            font_family="Rockwell",
            font_color="white"  # This ensures all hover text is white
        )
    )
    return fig


# Main function
def analyze_stocks(year, month, day, num_days):
    stocks = load_stocks()
    start_date = datetime(year, month, day)
    end_date = start_date + timedelta(days=num_days)
    data = get_stock_data(start_date, end_date, stocks)

    chart = create_chart(data)

    return chart


# Set up Gradio interface
current_date = datetime.now()

with gr.Blocks() as demo:
    gr.Markdown("# TASE Stock Performance Analyzer")
    gr.Markdown("Analyze stock performances based on date range.")

    with gr.Row():
        year = gr.Dropdown(choices=list(range(2000, 2025)), label="Year", value=current_date.year)
        month = gr.Dropdown(choices=list(range(1, 13)), label="Month", value=current_date.month)
        day = gr.Dropdown(choices=list(range(1, 32)), label="Day", value=1)

    num_days = gr.Slider(minimum=1, maximum=365, step=1, label="Number of Days", value=14)

    submit_btn = gr.Button("Analyze")

    output = gr.Plot()

    submit_btn.click(
        fn=analyze_stocks,
        inputs=[year, month, day, num_days],
        outputs=output
    )

demo.launch()
