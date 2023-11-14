# Importing AWS SDK for Python and other helper libraries

import boto3
from decimal import Decimal
import json
from boto3.dynamodb.conditions import Key
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from fastapi.responses import JSONResponse

app = FastAPI()

origins = [
    "http://10.182.149.211:8000",
    "https://10.182.149.211:8000",
    "exp://10.182.149.211:8000",  # This is for Expo
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


dynamoDB = boto3.resource('dynamodb')
table = dynamoDB.Table('Investor')


class LoginCredential(BaseModel):
    email: str
    password: str

# Check for login credential validity
@app.post('/login', response_model=bool)
async def receive_data(credential: LoginCredential):
    # Process the data
    table = dynamoDB.Table('Investor')
    print("backend hit!!")
    query_key = 'Email'  # The key you want to query on
    query_value = credential.email.lower()  # The value to query for
    
    key_condition_expression = Key(query_key).eq(query_value)

    # Execute the query
    response = table.query(
        KeyConditionExpression=key_condition_expression
    )

    # return True
    # Process the results
    if len(response['Items']) > 0:
        if credential.password == response['Items'][0]['Password']:
            # return True 
            return JSONResponse(content=[1,2,3,4], status_code=200)
    # return False
    return JSONResponse(content=False, status_code=400)


class SignUpCredential(BaseModel):
    phone_number: int
    email: str
    password: str
    repeat_password: str

# Add Sign Up details to DynamoDB
@app.post('/signup', response_model=bool)
async def signup(credential: SignUpCredential):
    # if credential.password != credential.repeat_password:
    #     return False
    
    # if credential.email.split('@')[-1] not in ['gmail.com', 'yahoo.com', 'hotmail.com', 'icloud.com']:
    #     return False
    
    
    item = {
        'Email': credential.email.lower(),
        'Password': credential.password,
        'Phone_Number': credential.phone_number
    }

    try:
        response = table.put_item(Item=item)
    # if email is not unique or some other issue
    except Exception as e:
        print(f'DynamoDb Error: {e}')
        return False
    
    print("Successfully Signed Up!")
    return True
    


class UserEmail(BaseModel):
    email: str
    
# Handle Delete User Request
@app.post('/delete_user', response_model=bool)
async def delete(user: UserEmail):
    
    primary_key = {'Email': user.email.lower()}
    
    try:
        response = table.delete_item(
            Key = primary_key
        )
    except Exception as e:
        print(f'DynamoDB Error: {e}')    
        return False
    
    return True


# Receive the Investor's (User's) email id, get the preferences, sort ALL property listings based on preferences, return order of properties by ID


@app.post('/property_swipe_list')

async def get_property_swipe_list(investor: UserEmail):

    # get minimum investment preference of the investor
    key_condition_expression = Key('Email').eq(email)
    table = dynamoDB.Table('Investor')
    response = table.query(
        KeyConditionExpression=key_condition_expression
    )
    min_investment = response['Items'][0]['Min_Investment']

    # sort property listings by min investment asc and return 
