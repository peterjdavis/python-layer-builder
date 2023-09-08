import requests

def lambda_handler(event, context):
    
    url = 'https://www.amazon.co.uk'
    response = requests.get(url)

    return {"statusCode": 200,
            "body": response.text}
