import csv
import boto3
import os
import tempfile
from datetime import datetime
from django.core.management.base import BaseCommand
from tradingSim_app.models import Trade

# AWS S3 Configuration
AWS_S3_BUCKET_NAME = "tradingsim"

class Command(BaseCommand):
    help = "Export trade data to CSV and upload it to AWS S3"

    def handle(self, *args, **kwargs):
        today = datetime.today()
        folder_path = f"{today.year}/{today.month:02d}/{today.day:02d}"
        filename = "trades.csv"

        # Use a temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False, newline="", suffix=".csv") as temp_file:
            csv_path = temp_file.name  # Get the temp file path
            writer = csv.writer(temp_file)
            writer.writerow(["ticker", "price", "quantity", "side", "timestamp"])

            trades = Trade.objects.all()
            for trade in trades:
                writer.writerow([trade.ticker, trade.price, trade.quantity, trade.side, trade.timestamp])

        # Upload to S3
        self.upload_to_s3(csv_path, folder_path, filename)

        # Remove temporary file after uploading
        os.remove(csv_path)

    def upload_to_s3(self, file_path, folder_path, filename):
        """Uploads file to S3"""
        s3_client = boto3.client("s3")
        s3_key = f"{folder_path}/{filename}"
        try:
            s3_client.upload_file(file_path, AWS_S3_BUCKET_NAME, s3_key)
            self.stdout.write(self.style.SUCCESS(f"Uploaded {filename} to S3 at {s3_key}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to upload to S3: {e}"))
