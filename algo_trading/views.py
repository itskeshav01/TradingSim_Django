import pandas as pd
import traceback
import logging
import os
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.conf import settings

# Set up logging
logger = logging.getLogger(__name__)

def upload_and_run(request):
    trades = []
    total_profit = 0.0
    error_message = None
    debug_info = {}
    file_info = {}
    
    # Debug request method
    debug_info['request_method'] = request.method
    
    if request.method == "POST":
        try:
            # Check if the request contains a file
            if 'csv_file' not in request.FILES:
                error_message = "No file uploaded. Please select a CSV file."
                debug_info['file_present'] = False
                return render(request, "algo_trading/upload.html", {
                    'error_message': error_message,
                    'debug_info': debug_info,
                })
            
            debug_info['file_present'] = True
            file = request.FILES['csv_file']
            
            # Debug file information
            file_info = {
                'name': file.name,
                'size': file.size,
                'content_type': file.content_type,
            }
            debug_info['file_info'] = file_info
            
            # Save file to a temporary location for debugging
            temp_file_path = os.path.join(settings.MEDIA_ROOT, 'temp', file.name)
            os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)
            
            with open(temp_file_path, 'wb+') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
            
            debug_info['temp_file_saved'] = temp_file_path
            
            # Read the file
            try:
                # First try to read a sample for debugging
                sample_lines = []
                with open(temp_file_path, 'r') as f:
                    for i, line in enumerate(f):
                        if i < 5:  # Get the first 5 lines
                            sample_lines.append(line.strip())
                        else:
                            break
                
                debug_info['sample_content'] = sample_lines
                
                # Now read the full file with pandas
                df = pd.read_csv(temp_file_path)
                debug_info['dataframe_loaded'] = True
                debug_info['row_count'] = len(df)
                debug_info['columns'] = list(df.columns)
                
                # Validate required columns
                required_columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    error_message = f"CSV file is missing required columns: {', '.join(missing_columns)}"
                    debug_info['missing_columns'] = missing_columns
                    return render(request, "algo_trading/upload.html", {
                        'error_message': error_message,
                        'debug_info': debug_info,
                        'file_info': file_info,
                    })
                
                # Process date column
                try:
                    df['Date'] = pd.to_datetime(df['Date'])
                    debug_info['date_conversion'] = 'success'
                except Exception as e:
                    error_message = f"Error converting dates: {str(e)}"
                    debug_info['date_conversion'] = f'error: {str(e)}'
                    return render(request, "algo_trading/upload.html", {
                        'error_message': error_message,
                        'debug_info': debug_info,
                        'file_info': file_info,
                    })
                
                # Sort data
                df.sort_values('Date', inplace=True)
                
                # Check data size for moving averages
                if len(df) < 200:
                    error_message = f"Not enough data points. Need at least 200 rows for 200-day MA, but got {len(df)}."
                    debug_info['data_size_issue'] = True
                    return render(request, "algo_trading/upload.html", {
                        'error_message': error_message,
                        'debug_info': debug_info,
                        'file_info': file_info,
                    })
                
                # Calculate moving averages
                debug_info['calculation_step'] = 'starting MA calculations'
                df['MA_50'] = df['Close'].rolling(window=50).mean()
                df['MA_200'] = df['Close'].rolling(window=200).mean()
                debug_info['ma_calculated'] = True
                
                # Remove NaN values
                df = df.dropna()
                debug_info['nan_removed'] = True
                debug_info['rows_after_nan_removal'] = len(df)
                
                # Add a column to detect crossovers
                df['Signal'] = 0
                df.loc[df['MA_50'] > df['MA_200'], 'Signal'] = 1
                
                # Create a crossover signal
                df['Crossover'] = df['Signal'].diff()
                
                # Start trading logic
                debug_info['trading_logic'] = 'starting'
                position = None
                buy_price = 0
                buy_date = None
                
                for i in range(len(df)):
                    # Golden Cross: MA_50 crosses above MA_200
                    if df['Crossover'].iloc[i] == 1:
                        position = 'buy'
                        buy_price = df['Close'].iloc[i]
                        buy_date = df['Date'].iloc[i]
                        
                    # Death Cross: MA_50 crosses below MA_200
                    elif df['Crossover'].iloc[i] == -1 and position == 'buy':
                        sell_price = df['Close'].iloc[i]
                        sell_date = df['Date'].iloc[i]
                        profit = sell_price - buy_price
                        total_profit += profit
                        
                        trades.append({
                            'buy_date': buy_date.strftime('%Y-%m-%d'),
                            'buy_price': round(buy_price, 2),
                            'sell_date': sell_date.strftime('%Y-%m-%d'),
                            'sell_price': round(sell_price, 2),
                            'profit': round(profit, 2),
                            'profit_percentage': round((profit / buy_price) * 100, 2),
                            'ma_50': round(df['MA_50'].iloc[i], 2),
                            'ma_200': round(df['MA_200'].iloc[i], 2),
                        })
                        
                        position = None
                
                # Handle open position at the end
                if position == 'buy':
                    last_price = df['Close'].iloc[-1]
                    last_date = df['Date'].iloc[-1]
                    unrealized_profit = last_price - buy_price
                    
                    trades.append({
                        'buy_date': buy_date.strftime('%Y-%m-%d'),
                        'buy_price': round(buy_price, 2),
                        'sell_date': 'Open Position',
                        'sell_price': round(last_price, 2),
                        'profit': round(unrealized_profit, 2),
                        'profit_percentage': round((unrealized_profit / buy_price) * 100, 2),
                        'ma_50': round(df['MA_50'].iloc[-1], 2),
                        'ma_200': round(df['MA_200'].iloc[-1], 2),
                    })
                
                debug_info['trades_found'] = len(trades)
                debug_info['total_profit'] = round(total_profit, 2)
                
                # Store trades in session for download
                request.session['trades'] = trades
                request.session['total_profit'] = round(total_profit, 2)
                
                # Check if there were any trades
                if not trades:
                    debug_info['no_trades'] = 'No crossover signals detected in the provided data'
                
                # Return result
                return render(request, "algo_trading/upload.html", {
                    'trades': trades,
                    'total_profit': round(total_profit, 2),
                    'total_trades': len(trades),
                    'winning_trades': len([t for t in trades if t['profit'] > 0]),
                    'losing_trades': len([t for t in trades if t['profit'] < 0]),
                    'debug_info': debug_info,
                    'processing_complete': True,
                })
                
            except pd.errors.EmptyDataError:
                error_message = "The CSV file is empty."
                debug_info['empty_file'] = True
            except pd.errors.ParserError as e:
                error_message = f"Error parsing CSV: {str(e)}"
                debug_info['parser_error'] = str(e)
            
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}"
            debug_info['exception'] = str(e)
            debug_info['traceback'] = traceback.format_exc()
            logger.error(f"Error in upload_and_run: {str(e)}", exc_info=True)
    
    # Default response
    return render(request, "algo_trading/upload.html", {
        'error_message': error_message,
        'debug_info': debug_info,
        'file_info': file_info,
    })

def download_report(request):
    trades = request.session.get('trades', [])
    total_profit = request.session.get('total_profit', 0)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="trading_report.csv"'
    
    # Write header
    response.write("Buy Date,Buy Price,Sell Date,Sell Price,Profit,Profit %,50 MA,200 MA\n")
    
    # Write trade data
    for trade in trades:
        row = f"{trade['buy_date']},{trade['buy_price']},{trade['sell_date']},{trade['sell_price']},{trade['profit']},{trade.get('profit_percentage', 0)},{trade['ma_50']},{trade['ma_200']}\n"
        response.write(row)
    
    # Write summary at the end
    response.write(f"\nTotal Profit/Loss,{total_profit}\n")
    response.write(f"Total Trades,{len(trades)}\n")
    response.write(f"Winning Trades,{len([t for t in trades if t['profit'] > 0])}\n")
    response.write(f"Losing Trades,{len([t for t in trades if t['profit'] < 0])}\n")
    
    return response