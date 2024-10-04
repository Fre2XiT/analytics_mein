import json
import re
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt

from .getDataFrame import ResolveA01

async def table(variables, cookies):
    df = await ResolveA01(variables, cookies)
    # print(pivotdata, flush=True)

    classes = 'table table-striped table-bordered table-hover table-sm'
    return df.to_html(classes=classes)

async def chart(variables, cookies):
    df = await ResolveA01(variables, cookies)

    df.plot.pie(
        figsize=(40, 20), 
        subplots=True,
        legend=False,
        rotatelabels=True
        )
    with BytesIO() as f:
        plt.savefig(f, format="svg")
        svgresult = f.getvalue().decode()

    return svgresult

async def build_data_frame(variables, cookies):
    df = await ResolveA01(variables=variables, cookies=cookies)
    return df

async def process_df_as_html_table(df):
    classes = 'table table-striped table-bordered table-hover table-sm'
    return df.to_html(classes=classes)


def extendapp(app, prefix):
    pass

import datetime
from fastapi import APIRouter, Request, Query
from src.utils import process_df_as_html_page, process_df_as_excel, process_df_as_json, process_df_as_svg_chart
from .getDataFrame import read_json, resolve_df_pivot
def createRouter(prefix):
    from .getDataFrame import resolve_df, resolve
    router = APIRouter(prefix=prefix)
    WhereDescription = "Where filter for query (see UserInputFilter in GQL endpoint)"
    StartdateDescription = "Start date of time interval (included)"
    EnddateDescription = "End date of time interval (included)"

    tags = ["Přítomnost"]
    @router.get("/users/events", tags=tags)
    async def users_events_html(
        request: Request, 
        where: str = Query(description=WhereDescription), 
        startdate: datetime.datetime = Query(description=StartdateDescription), 
        enddate: datetime.datetime = Query(description=EnddateDescription)
    ):
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        pd = await resolve_df(
            variables={
                "where": wherejson, 
                "startdate": f"{startdate}", 
                "enddate": f"{enddate}"},
            cookies = request.cookies
        )
        return await process_df_as_html_page(pd)
    
    @router.get("/users/events/excel", tags=tags)
    async def user_events_excel(
        request: Request, 
        where: str = Query(description=WhereDescription), 
        startdate: datetime.datetime = Query(description=StartdateDescription), 
        enddate: datetime.datetime = Query(description=EnddateDescription)
    ):
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        pd = await resolve_df(
            variables={
                "where": wherejson, 
                "startdate": f"{startdate}", 
                "enddate": f"{enddate}"},
            cookies = request.cookies
        )
        return await process_df_as_excel(pd)

    @router.get("/users/events/flatjson", tags=tags)
    async def user_events_flat_json(
        request: Request, 
        where: str = Query(description=WhereDescription), 
        startdate: datetime.datetime = Query(description=StartdateDescription), 
        enddate: datetime.datetime = Query(description=EnddateDescription)
    ):
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        result = await resolve(
            variables={
                "where": wherejson, 
                "startdate": f"{startdate}", 
                "enddate": f"{enddate}"},
            cookies = request.cookies
        )
        return result

    @router.get("/users/events/json", tags=tags)
    async def user_events_json(
        request: Request, 
        where: str = Query(description=WhereDescription), 
        startdate: datetime.datetime = Query(description=StartdateDescription), 
        enddate: datetime.datetime = Query(description=EnddateDescription)
    ):
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        result = await read_json(
            variables={
                "where": wherejson, 
                "startdate": f"{startdate}", 
                "enddate": f"{enddate}"},
            cookies = request.cookies
        )
        return result

    @router.get("/users/events/chart", tags=tags)
    async def user_events_chart(
        request: Request, 
        where: str = Query(description=WhereDescription), 
        startdate: datetime.datetime = Query(description=StartdateDescription), 
        enddate: datetime.datetime = Query(description=EnddateDescription)
    ):
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        pd = await resolve_df_pivot(
            variables={
                "where": wherejson, 
                "startdate": f"{startdate}", 
                "enddate": f"{enddate}"},
            cookies = request.cookies
        )
        # return await process_df_as_html_page(pd)
        return await process_df_as_svg_chart(pd)


    return router