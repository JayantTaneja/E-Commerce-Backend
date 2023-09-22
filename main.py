from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List
import time

from credentials import uri

#----------------Setup and Connections----------
app = FastAPI()
mongo_client = MongoClient(uri)
db = mongo_client["mydb"]

#--------------------Products----------------------

@app.get('/products')
async def get_all_products():
    '''
    Returns all the products in the database
    '''
    response = list(db.products.find({}))
    
    products = []

    for document in response:
        products.append({
            key:value for key, value in document.items() if key != "_id"    # exclude mongodb _id Object
        })
    return products


@app.post('/products/{productId}/{newQty}')
async def update_product_qty(productID : str, newQty : int):
    '''
    Updated the available quantity of product with ```productId``` to ```newQty```

    Params:
    - productId : The product id of the product to be updated 
    - newQty : New available quantity for the product to be updated 
    '''

    db.products.update_one(
        {"id" : productID},
        {"$set" : {"avl_qty" : newQty}}
    )

    return "Product Updated"


#--------------------Orders----------------------

class Item(BaseModel):
    productId : str
    boughtQuantity : int

class Address(BaseModel):
    city : str
    country : str
    zipCode : int

class Order(BaseModel):
    orderId : str
    items : List[Item]
    totalAmount : int
    userAddress : Address

@app.post('/orders')
async def create_order(order : Order):
    '''
    Creates and stores a new order with following info:

    - Timestamp : The current time
    - orderId : The order's Order Id
    - items : A list containing Item objects (productId, boughtQuantity)
    - totalAmount : The total amount to be paid
    - Address : An ```Address``` object containing City, Country, ZipCode
    '''
    timestamp = time.time()

    order_data = {
        "timestamp" : timestamp,
        "orderId" : order.orderId,
        "items" : [
            {
                "productId" : i.productId, 
                "boughtQuantity" : i.boughtQuantity
            } 
            for i in order.items
        ],
        "totalAmount" : order.totalAmount,
        "userAddress" : {
            "city" : order.userAddress.city,
            "country" : order.userAddress.country,
            "zipCode" : order.userAddress.zipCode
        } 
    }

    db.orders.insert_one(order_data)

    return "Order Placed"


@app.get('/orders')
async def get_all_orders(page_no : int = 1, page_size : int = 10):
    '''
    
    Fetches ```page_size``` number of orders on the ```page_no``` 'th page

    Params:
    - page_no : The current page no. for pagination
    - page_size : The number of items to be displayed

    
    Returns:
    - ```list``` of ```dict```s containing the order details

    '''
    response = list(db.orders.find({}).skip((page_no - 1) * page_size).limit(page_size))
    
    orders = []

    for document in response:
        orders.append({
            key:value for key, value in document.items() if key != "_id"    # exclude mongodb _id Object
        })
    return orders

@app.get('/orders/{order_id}')
async def get_order(order_id : str):
    '''
    Returns the order with order id = ```order_id```

    Params:
    - order_id : The orderId of the order to be returned

    Returns:
    - The order with the requested orderId (if exists)
    '''
    response = list(db.orders.find({"orderId":order_id}))
    
    orders = []

    for document in response:
        orders.append({
            key:value for key, value in document.items() if key != "_id"    # exclude mongodb _id Object
        })
    return orders
