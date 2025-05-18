import logging
from flask import Blueprint, render_template, request
from sqlalchemy import func, extract
from sqlalchemy.orm import aliased
from app.models import Inventory, Sales
from app import db
from app.arima_forecast import arima_forecast
from app.linear_regression import linear_regression_forecast
from app.ets_model import ets_forecast
from collections import defaultdict
import pandas as pd

main = Blueprint('main', __name__)

@main.route('/dashboard')
def dashboard():
    # Get timeframe filter from query params: monthly (default), quarterly, yearly
    timeframe = request.args.get('timeframe', 'monthly').lower()
    if timeframe == 'monthly':
        group_func = extract('month', Sales.sales_date)
    elif timeframe == 'quarterly':
        group_func = extract('quarter', Sales.sales_date)
    elif timeframe == 'yearly':
        group_func = extract('year', Sales.sales_date)
    else:
        group_func = extract('month', Sales.sales_date)

    # Get filter parameters for dynamic filtering
    selected_region = request.args.get('region', None)
    selected_item = request.args.get('item', None)
    search_text = request.args.get('search', None)

    # Base queries
    sales_query = db.session.query(Sales)
    inventory_query = db.session.query(Inventory)

    # Apply filters
    if selected_region:
        sales_query = sales_query.filter(Sales.region == selected_region)

    if selected_item:
        inventory_query = inventory_query.filter(Inventory.item_name == selected_item)

    if search_text:
        search_like = f"%{search_text}%"
        sales_query = sales_query.filter(Sales.region.ilike(search_like))
        inventory_query = inventory_query.filter(Inventory.item_name.ilike(search_like))

    # Debug print counts
    print(f"Filters applied - Region: {selected_region}, Item: {selected_item}, Search: {search_text}")
    print(f"Filtered sales count: {sales_query.count()}")
    print(f"Filtered inventory count: {inventory_query.count()}")

    # Calculate shortage and overstock risk items
    shortage_items = inventory_query.filter(
        Inventory.quantity <= Inventory.reorder_level
    ).all()

    overstock_items = inventory_query.filter(
        Inventory.quantity >= Inventory.reorder_level * 2
    ).all()

    # --- FIXED: Sales grouped by region and period ---
    sales_by_region_period = sales_query.with_entities(
        Sales.region,
        group_func.label('period'),
        func.sum(Sales.sales_amount)
    ).group_by(Sales.region, group_func).order_by(Sales.region, group_func).all()

    region_sales_trends = defaultdict(list)
    for region, period, total_sales in sales_by_region_period:
        region_sales_trends[region].append((period, float(total_sales)))
    region_sales_trends = dict(region_sales_trends)

    # Total stock and value from filtered inventory
    total_stock = inventory_query.with_entities(func.sum(Inventory.quantity)).scalar() or 0
    total_value = inventory_query.with_entities(func.sum(Inventory.quantity * Inventory.price)).scalar() or 0.0

    # Stock reorder frequency
    stock_reorder_freq = inventory_query.filter(
        Inventory.quantity <= Inventory.reorder_level
    ).with_entities(func.count(Inventory.id)).scalar() or 0

    # Top regions by sales (aggregate)
    sales_by_region = sales_query.with_entities(
        Sales.region,
        func.sum(Sales.sales_amount)
    ).group_by(Sales.region).order_by(func.sum(Sales.sales_amount).desc()).all()

    sales_by_region = [(row[0], row[1]) for row in sales_by_region]

    # Distribution stock usage by item_name
    distribution_stock_usage = inventory_query.with_entities(
        Inventory.item_name,
        func.sum(Inventory.quantity)
    ).group_by(Inventory.item_name).all()

    distribution_stock_usage = [(row[0], row[1]) for row in distribution_stock_usage]

    # --- FIXED: Historical stock levels over time ---
    # Inventory likely doesn't have a date column to group by month/quarter/year, so:
    # You need a timestamp or date column in Inventory to group properly.
    # If no date column, just sum total quantity without grouping.
    # Here, returning total stock as fallback:
    stock_levels_over_time = [(None, total_stock)]

    # Example stock in/out static values (adjust if you have real data)
    stock_in = total_stock + 500
    stock_out = 700

    # --- FIXED: Stock reorder frequency trend (grouping) ---
    # Again, only possible if Inventory has a date field; else just count
    reorder_hits_over_time = [(None, stock_reorder_freq)]

    # Price trend over time (requires date in inventory)
    price_trend_data = [(None, 0.0)]  # fallback if no date column

    # Historical sales grouped by sales_date for forecasting
    sales_data = sales_query.with_entities(
        Sales.sales_date,
        func.sum(Sales.sales_amount)
    ).group_by(Sales.sales_date).order_by(Sales.sales_date).all()

    forecast_steps = 4  # Number of future points to forecast

    # Initialize forecast variables to None
    arima_mae = arima_rmse = lr_mae = lr_rmse = lr_mape = lr_r2 = ets_mae = ets_rmse = None

    if sales_data:
        try:
            df = pd.DataFrame(sales_data, columns=['date', 'sales_amount'])
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df = df.asfreq('D', fill_value=0)
            series = pd.Series(df['sales_amount'].values, index=df.index)

            try:
                arima_forecast_data = arima_forecast(series, order=(1, 1, 1), steps=forecast_steps)
            except Exception as e:
                logging.error(f"ARIMA forecasting failed: {e}")
                arima_forecast_data = [0] * forecast_steps

            try:
                lr_forecast_data, lr_mae, lr_rmse, lr_mape, lr_r2 = linear_regression_forecast(series, steps=forecast_steps)
            except Exception as e:
                logging.error(f"Linear Regression forecasting failed: {e}")
                lr_forecast_data, lr_mae, lr_rmse, lr_mape, lr_r2 = [0] * forecast_steps, None, None, None, None

            try:
                ets_forecast_data, ets_mae, ets_rmse = ets_forecast(series, steps=forecast_steps)
            except Exception as e:
                logging.error(f"ETS forecasting failed: {e}")
                ets_forecast_data, ets_mae, ets_rmse = [0] * forecast_steps, None, None

        except Exception as e:
            logging.error(f"Error processing sales data for forecasting: {e}")
            arima_forecast_data = lr_forecast_data = ets_forecast_data = [0] * forecast_steps
            arima_mae = arima_rmse = None
            lr_mae = lr_rmse = lr_mape = lr_r2 = None
            ets_mae = ets_rmse = None
    else:
        arima_forecast_data = lr_forecast_data = ets_forecast_data = [0] * forecast_steps
        arima_mae = arima_rmse = None
        lr_mae = lr_rmse = lr_mape = lr_r2 = None
        ets_mae = ets_rmse = None

    # --- Demand Trend by Region Forecasting ---
    region_forecast_results = {}

    # Group sales data by region for forecast
    for region in set(row[0] for row in sales_by_region_period):
        region_data = [(row[1], float(row[2])) for row in sales_by_region_period if row[0] == region]
        if not region_data:
            continue

        periods, sales = zip(*region_data)
        series = pd.Series(sales, index=pd.Index(periods))

        try:
            forecast = arima_forecast(series, order=(1, 1, 1), steps=forecast_steps)
        except Exception as e:
            logging.error(f"Forecast failed for region {region}: {e}")
            forecast = [0] * forecast_steps

        region_forecast_results[region] = {
            'historical': series.tolist(),
            'forecast': forecast
        }

    # Fetch unique regions and items for filters
    regions = [r[0] for r in db.session.query(Sales.region).distinct().order_by(Sales.region).all()]
    items = [i[0] for i in db.session.query(Inventory.item_name).distinct().order_by(Inventory.item_name).all()]

    # Render template
    return render_template('dashboard.html',
                           total_stock=total_stock,
                           total_value=total_value,
                           stock_reorder_freq=stock_reorder_freq,
                           top_regions=sales_by_region,
                           distribution_stock_usage=distribution_stock_usage,
                           stock_levels_over_time=stock_levels_over_time,
                           stock_in=stock_in,
                           stock_out=stock_out,
                           reorder_hits_over_time=reorder_hits_over_time,
                           forecast_data_arima=arima_forecast_data,
                           forecast_data_lr=lr_forecast_data,
                           lr_mae=lr_mae,
                           lr_rmse=lr_rmse,
                           lr_mape=lr_mape,
                           lr_r2=lr_r2,
                           forecast_data_ets=ets_forecast_data,
                           ets_mae=ets_mae,
                           ets_rmse=ets_rmse,
                           region_sales_trends=region_sales_trends,
                           shortage_items=shortage_items,
                           overstock_items=overstock_items,
                           region_forecast_results=region_forecast_results,
                           price_trend_data=price_trend_data,
                           regions=regions,
                           items=items,
                           selected_region=selected_region,
                           selected_item=selected_item,
                           search_text=search_text,
                           timeframe=timeframe)

@main.route('/inventory')
def inventory():
    return render_template('inventory.html')

@main.route('/sdg-zero-hunger')
def sdg_zero_hunger():
    return render_template('sdg-zero-hunger.html')
