import boto3
import csv
import json
from datetime import datetime

# Initialize S3 client
s3_client = boto3.client("s3")

# Your S3 bucket name
S3_BUCKET_NAME = "tradingsim"  # Replace with your actual bucket name

def get_trade_file_by_date(date):
    """Fetch the latest trade CSV file from S3 for the given date."""
    year, month, day = date.split("-")
    file_key = f"{year}/{month}/{day}/trades.csv"

    try:
        response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=file_key)
        return response["Body"].read().decode("utf-8")  # Convert to string
    except Exception as e:
        print(f"Error fetching trade file: {str(e)}")
        return None  # Return None if file not found

def process_trade_data(csv_data):
    """Process trade data to calculate total volume and average price per stock."""
    stock_data = {}

    reader = csv.reader(csv_data.splitlines())
    headers = next(reader)  # Skip headers (assuming first row has headers)

    for row in reader:
        stock, price, volume = row[0], float(row[1]), int(row[2])
        if stock not in stock_data:
            stock_data[stock] = {"total_volume": 0, "total_price": 0, "trade_count": 0}

        stock_data[stock]["total_volume"] += volume
        stock_data[stock]["total_price"] += price * volume
        stock_data[stock]["trade_count"] += 1

    # Calculate average price
    for stock, data in stock_data.items():
        data["average_price"] = data["total_price"] / data["total_volume"]

    return stock_data

def save_analysis_to_s3(stock_data, date):
    """Save analysis results back to S3."""
    year, month, day = date.split("-")
    analysis_key = f"{year}/{month}/{day}/analysis_{date}.csv"

    # Convert dictionary to CSV format
    csv_output = "Stock,Total Volume,Average Price\n"
    for stock, data in stock_data.items():
        csv_output += f"{stock},{data['total_volume']},{data['average_price']:.2f}\n"

    # Upload to S3
    try:
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=analysis_key,
            Body=csv_output.encode("utf-8"),
            ContentType="text/csv"
        )
        print(f"Analysis saved to S3: {analysis_key}")
    except Exception as e:
        print(f"Error saving analysis file: {str(e)}")

def lambda_handler(event, context):
    """AWS Lambda entry point"""
    # Get date from API Gateway Query Parameters
    query_params = event.get("queryStringParameters", {})
    date = query_params.get("date", datetime.today().strftime('%Y-%m-%d'))
    
    csv_data = get_trade_file_by_date(date)
    
    if csv_data:
        stock_data = process_trade_data(csv_data)
        save_analysis_to_s3(stock_data, date)
        return {"statusCode": 200, "message": f"Analysis saved for {date}"}
    
    return {"statusCode": 500, "message": "No trade data found"}
