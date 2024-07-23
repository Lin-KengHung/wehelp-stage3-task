from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import mysql.connector
from mysql.connector import Error
import boto3
import uuid
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')
S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_DEFAULT_REGION = os.getenv('AWS_DEFAULT_REGION')
CLOUDFRONT_DOMAIN = os.getenv('CLOUDFRONT_DOMAIN')

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_DEFAULT_REGION
)

def get_db_connection():
    connection = mysql.connector.connect(
        host=DATABASE_HOST,
        user=DATABASE_USER,
        password=DATABASE_PASSWORD,
        database=DATABASE_NAME
    )
    return connection

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def index():
    return FileResponse("./static/index.html", media_type="text/html")

@app.post("/messages")
async def upload_message(message: str = Form(...), photo: UploadFile = File(...)):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Upload photo to S3
        photo_key = f"{uuid.uuid4()}.{photo.filename.split('.')[-1]}"
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=photo_key,
            Body=photo.file,
            ContentType=photo.content_type
        )
        photo_url = f"https://{CLOUDFRONT_DOMAIN}/{photo_key}"

        # Save message and photo URL to database
        cursor.execute("INSERT INTO messages (text, photo_url) VALUES (%s, %s)", (message, photo_url))
        connection.commit()
        cursor.close()
        connection.close()

        return JSONResponse(content={"message": "Success"})
    except Error as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.get("/messages")
def get_messages():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM messages ORDER BY id DESC")
        messages = cursor.fetchall()
        cursor.close()
        connection.close()
        return messages
    except Error as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
