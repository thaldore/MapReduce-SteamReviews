import boto3
import os

try:
    session = boto3.Session(profile_name='MapReduce-admin')
except Exception:
    session = boto3.Session()

s3 = session.client('s3', region_name='eu-central-1')
BUCKET_NAME = 'steam-mapreduce-tolga-2026-v2'

print("100 oyun dosyasi AWS S3'e yukleniyor...")
print("Her yuklenen dosya aninda bir AWS Lambda (Map) tetikleyecek!")

count = 0
for filename in os.listdir('s3_ready/raw-reviews'):
    if filename.endswith('.json'):
        file_path = os.path.join('s3_ready/raw-reviews', filename)
        s3.upload_file(file_path, BUCKET_NAME, f'raw-reviews/{filename}')
        count += 1
        if count % 20 == 0:
            print(f"{count} dosya yuklendi (Arka planda {count} adet sunucu ayaga kalkti bile!)...")

print("--------------------------------------------------")
print(f"ISLEM TAMAM! {count} dosyanin tamami S3'e yuklendi.")
print("Su anda AWS uzerinde 100 farkli islemci paralel olarak Map islemi yapiyor.")
