import json
import os
import uuid
from datetime import datetime
from io import BytesIO

import boto3

# Need to add layer for PIL via dependency injection
from PIL import Image, ImageOps

s3 = boto3.client("s3")
IMAGE_SIZE = int(os.environ["THUMBNAIL_SIZE"])
DB_TABLE = str(os.environ["DYNAMODB_TABLE"])
DYNAMODB = boto3.resource(
    'dynamodb', region_name=str(os.environ['REGION_NAME']))

def thumbnail_generator(event, context):
    """Generate thumbnail for image in s3 bucket

    Args:
        event : data passed to the function upon execution
        context : info about current execution environment

    Returns:
       json response
    """

    print("EVENT INFO:::", event)

    bucket_name = event["Records"][0]["s3"]["bucket"]["name"]
    key = event["Records"][0]["s3"]["object"]["key"]
    image_size = event["Records"][0]["s3"]["object"]["size"]

    # Only want an image that isn't already a thumbnail
    if not key.endswith("_thumbnail.png"):
        image = get_image(bucket_name, key)
        thumbnail = resize_image(image)
        thumbnail_key = generate_thumbnail_file_name(key)

        url = upload_thumbnail_to_s3(bucket_name, thumbnail_key, thumbnail, image_size)

        return url

    body = {
        "message": "Go Serverless v3.0! Your function executed successfully!",
        "input": event,
    }

    return {"statusCode": 200, "body": json.dumps(body)}

def get_image(bucket_name, key):
    """Get the image from the s3 bucket.

    Args:
        bucket_name (string): Name of bucket we want to access
        key (string): Key of object to get

    Returns:
        (BinaryIO): image
    """
    response = s3.get_object(Bucket=bucket_name, Key=key)
    image_content = response["Body"].read()

    image_data = BytesIO(image_content)
    return Image.open(image_data)

def resize_image(image):
    """Generate thumbnail from image

    Args:
        image (BinaryIO): image in binary format

    Returns:
        BinaryIO: image in binary format
    """
    thumbnail = ImageOps.fit(
        image, (IMAGE_SIZE, IMAGE_SIZE), Image.Resampling.LANCZOS
    )
    return thumbnail

def generate_thumbnail_file_name(key):
    """Isolate the image name and add the thumbnail ending.

    Args:
        key (string): Key of object to get

    Returns:
        string: Name of thumbnail
    """
    # Split off .png file extension
    image_name = key.rsplit(".", 1)
    thumbnail_name = image_name[0] + "_thumbnail.png"
    return thumbnail_name

def upload_thumbnail_to_s3(bucket_name, thumbnail_key, image, image_size):
    """Upload image to s3 bucket as a BytesIO object.

    Args:
        bucket_name (string): Name of bucket we want to access
        key (string): Key of object to get
        image (BinaryIO): image in binary format
        image_size (int): size of image

    Returns:
        dict: status code and body
    """

    out_thumbnail = BytesIO()

    image.save(out_thumbnail, "PNG")
    # Get back to beginning of the file
    out_thumbnail.seek(0)

    response = s3.put_object(
        # Access Control List
        ACL="public-read",
        Body=out_thumbnail,
        Bucket=bucket_name,
        ContentType="image/png",
        Key=thumbnail_key,
    )
    print(response)

    url = "{}/{}/{}".format(s3.meta.endpoint_url, bucket_name, thumbnail_key)

    #  save the url of the image to our DB
    save_thumbnail_url_to_db(url, image_size)

    return url

def save_thumbnail_url_to_db(path, image_size):
    """_summary_

    Args:
        path (_type_): _description_
        image_size (_type_): _description_
    """

    toint = float(image_size * 0.53) / 1000
    table = DYNAMODB.Table(DB_TABLE)

    response = table.put_item(
        Item={
            # Generate a unique random id
            "id": str(uuid.uuid4()),
            "url": str(path),
            "approxReducedSize": str(toint) + str(" KB"),
            "createdAt": str(datetime.now()),
            "updatedAt": str(datetime.now()),
        }
    )

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response)
    }