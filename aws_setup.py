import boto3
import json
import time
import zipfile

print("--- AWS MAPREDUCE KURULUMU BAŞLIYOR ---")
try:
    session = boto3.Session(profile_name='MapReduce-admin')
except Exception:
    session = boto3.Session()

REGION = session.region_name or 'eu-central-1'

iam = session.client('iam', region_name=REGION)
s3 = session.client('s3', region_name=REGION)
lambda_client = session.client('lambda', region_name=REGION)

BUCKET_NAME = "steam-mapreduce-tolga-2026-v2"
ROLE_NAME = "SteamMapReduceRole"

print(f"Bölge: {REGION}")
print("1. S3 Bucket oluşturuluyor...")
try:
    if REGION == 'us-east-1':
        s3.create_bucket(Bucket=BUCKET_NAME)
    else:
        s3.create_bucket(Bucket=BUCKET_NAME, CreateBucketConfiguration={'LocationConstraint': REGION})
except Exception as e:
    print(f"Bucket zaten var veya atlandı: {e}")

print("2. IAM Rolü oluşturuluyor...")
trust_policy = {
    "Version": "2012-10-17",
    "Statement": [{"Action": "sts:AssumeRole", "Principal": {"Service": "lambda.amazonaws.com"}, "Effect": "Allow"}]
}
try:
    iam.create_role(RoleName=ROLE_NAME, AssumeRolePolicyDocument=json.dumps(trust_policy))
    iam.attach_role_policy(RoleName=ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess")
    iam.attach_role_policy(RoleName=ROLE_NAME, PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole")
    print("IAM yetkilerinin AWS sistemine yayılması için 10 saniye bekleniyor...")
    time.sleep(10)
except Exception as e:
    print(f"Rol zaten var veya atlandı.")

role_arn = iam.get_role(RoleName=ROLE_NAME)['Role']['Arn']

print("3. Lambda fonksiyonları zip'leniyor...")
with zipfile.ZipFile('mapper.zip', 'w') as z:
    z.write('cloud_functions/mapper_lambda.py', 'lambda_function.py')
with zipfile.ZipFile('reducer.zip', 'w') as z:
    z.write('cloud_functions/reducer_lambda.py', 'lambda_function.py')

print("4. steam-mapper Lambda yükleniyor...")
with open('mapper.zip', 'rb') as f:
    zip_bytes = f.read()

try:
    lambda_client.create_function(
        FunctionName='steam-mapper',
        Runtime='python3.11',
        Role=role_arn,
        Handler='lambda_function.lambda_handler',
        Code={'ZipFile': zip_bytes},
        Timeout=60,
        MemorySize=128
    )
except Exception as e:
    print(f"Mapper zaten var veya hata: {e}")

print("5. steam-reducer Lambda yükleniyor...")
with open('reducer.zip', 'rb') as f:
    zip_bytes_red = f.read()

try:
    lambda_client.create_function(
        FunctionName='steam-reducer',
        Runtime='python3.11',
        Role=role_arn,
        Handler='lambda_function.lambda_handler',
        Code={'ZipFile': zip_bytes_red},
        Timeout=180,
        MemorySize=512,
        Environment={'Variables': {'BUCKET_NAME': BUCKET_NAME}}
    )
except Exception as e:
    print(f"Reducer zaten var veya hata: {e}")

print("6. S3 Tetikleyicisi (Trigger) ekleniyor...")
try:
    mapper_arn = lambda_client.get_function(FunctionName='steam-mapper')['Configuration']['FunctionArn']
    try:
        lambda_client.add_permission(
            FunctionName='steam-mapper',
            StatementId='s3-trigger',
            Action='lambda:InvokeFunction',
            Principal='s3.amazonaws.com',
            SourceArn=f"arn:aws:s3:::{BUCKET_NAME}"
        )
    except:
        pass
        
    s3.put_bucket_notification_configuration(
        Bucket=BUCKET_NAME,
        NotificationConfiguration={
            'LambdaFunctionConfigurations': [
                {
                    'LambdaFunctionArn': mapper_arn,
                    'Events': ['s3:ObjectCreated:Put'],
                    'Filter': {'Key': {'FilterRules': [{'Name': 'prefix', 'Value': 'raw-reviews/'}, {'Name': 'suffix', 'Value': '.json'}]}}
                }
            ]
        }
    )
except Exception as e:
    print(f"Tetikleyici hatası: {e}")

print("\n--- KURULUM BAŞARIYLA TAMAMLANDI! ---")
print(f"Sistem hazır. Bucket Adı: {BUCKET_NAME}")
