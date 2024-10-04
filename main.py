from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import HTMLResponse, Response
from contextlib import asynccontextmanager
import aiohttp
import json

import pandas as pd
import re

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    # app.
    yield
    # Clean up the ML models and release the resources
       


from src.analysis_000 import (
    table as table001,
    chart as chart001
)

from src.analysis_001 import (
    table as table002,
    chart as chart002
)

template = """
<link href="https://stackpath.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-Vkoo8x4CGsO3+Hhxv8T/Q5PaXtkKtu6ug5TOeNV6gBiFeWPGFN9MuhOf23Q9Ifjh" crossorigin="anonymous">
<style>
th {
    background: #2d2d71;
    color: white;
    text-align: left;
}
</style>
<body>
%s
</body>
"""

register = [
    {
        "uri": "/group/table",
        "name": "tabulka",
        "description": "Tabulka počtu členů skupin",
        "resolver": table001,
        
    },
{
        "uri": "/group/chart",
        "name": "Graf",
        "description": "Graf počtu členů skupin",
        "resolver": chart001,
        
    },            
    {
        "uri": "/user/presence/chart",
        "name": "Graf",
        "description": "Graf počtu hodin",
        "resolver": chart002,
        
    },    
    {
        "uri": "/user/presence/table",
        "name": "tabulka",
        "description": "Tabulka počtu hodin",
        "resolver": table002,
    },
    
]

def cookieExtract(request):
    return request.cookies

def variablesExtract(request):
    params = request.query_params
    variables = dict(params)
    if "where" in variables:
        wherevalue = variables["where"]
        wherevalue = re.sub(r'{([^:"]*):', r'{"\1":', wherevalue)
        print(wherevalue, flush=True)
        variables["where"] = json.loads(wherevalue)
    return variables

def createhtmlresolver(registereditem):
    resolver = registereditem["resolver"]
    cookieExtractor = registereditem.get("cookieExtractor", cookieExtract)
    variablesExtractor = registereditem.get("variablesExtractor", variablesExtract)

    async def resolveashtml(request: Request):
        cookies = cookieExtractor(request)
        variables = variablesExtractor(request)

        result = await resolver(variables, cookies) 
        response = HTMLResponse(result)
        return response
    resolveashtml.__doc__ = resolver.__doc__
    description = registereditem.get("description", None)
    if description not in [None, ""]:
        resolveashtml.__doc__ = description

    return resolveashtml    

app = FastAPI(lifespan=lifespan)

for registereditem in register:
    app.get(f'/analysis{registereditem["uri"]}', name=registereditem.get("name", None))(
        createhtmlresolver(registereditem)
    )
from src.analysis_001 import createRouter

app.include_router(createRouter(prefix="/analysis"))

from src.analysis_000 import createRouter as createRouter000
app.include_router(createRouter000(prefix="/analysis"))

from src.analysis_002 import createRouter as createRouter002
app.include_router(createRouter002(prefix="/analysis"))

from src.analysis_004 import createRouter as createRouter004
app.include_router(createRouter004(prefix="/analysis"))

from src.analysis_005 import createRouter as createRouter005
app.include_router(createRouter005(prefix="/analysis"))

from src.analysis_006 import createRouter as createRouter006
app.include_router(createRouter006(prefix="/analysis"))

from src.analysis_007 import createRouter as createRouter007
app.include_router(createRouter007(prefix="/analysis"))

from src.analysis_008 import createRouter as createRouter008
app.include_router(createRouter008(prefix="/analysis"))

from src.analysis_009 import createRouter as createRouter009
app.include_router(createRouter009(prefix="/analysis"))

from src.analysis_011 import createRouter as createRouter011
app.include_router(createRouter011(prefix="/analysis"))

from src.analysis_999 import createrouter as createRouter999
app.include_router(createRouter999(prefix="/analysis"))

from src.analysis_calendar import createRouter as createRouter_calendar
app.include_router(createRouter_calendar(prefix="/analysis"))