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

import string
import openpyxl
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, Request, Query, Response
from .getDataFrame import resolve_flat_json, resolve_json
from ..utils import process_df_as_html_page
def createRouter(prefix):
    mainpath = "/groups/memberships"
    tags = ["Členství ve skupinách"]

    router = APIRouter(prefix=prefix)
    WhereDescription = "filtr omezující vybrané skupiny"
    @router.get(f"{mainpath}/table", tags=tags)
    async def group_membership_html(
        request: Request,
        where: str = Query(description=WhereDescription)
    ):
        "HTML tabulka s daty pro výpočet kontingenční tabulky"
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        pd = await resolve_flat_json(
            variables={
                "where": wherejson
            },
            cookies=request.cookies
        )
        df = pd.DataFrame(pd)
        return await process_df_as_html_page(df)
    
    @router.get(f"{mainpath}/flatjson", tags=tags)
    async def _flat_json(
        request: Request, 
        where: str = Query(description=WhereDescription), 
    ):
        "Data ve formátu JSON transformována do podoby vstupu pro kontingenční tabulku"
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        pd = await resolve_flat_json(
            variables={
                "where": wherejson
            },
            cookies=request.cookies
        )
        return pd

    @router.get(f"{mainpath}/json", tags=tags)
    async def _json(
        request: Request, 
        where: str = Query(description=WhereDescription), 
    ):
        "Data ve formátu JSON (stromová struktura) nevhodná pro kontingenční tabulku"
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        pd = await resolve_json(
            variables={
                "where": wherejson
            },
            cookies=request.cookies
        )
        return pd

    @router.get(f"{mainpath}/xlsx", tags=tags)
    async def _xlsx(
        request: Request, 
        where: str = Query(description=WhereDescription), 
    ):
        "Xlsx soubor doplněný o data v záložce 'data' (podle xlsx vzoru)"
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        flat_json = await resolve_flat_json(
            variables={
                "where": wherejson
            },
            cookies=request.cookies
        )

        with open('./src/xlsx/vzor2.xlsx', 'rb') as f:
            content = f.read()
        
        memory = BytesIO(content)
        resultFile = openpyxl.load_workbook(filename=memory)
        
        resultFileData = resultFile['data']
        
        for (rid, item) in enumerate(flat_json):
            for col, value in zip(string.ascii_uppercase, item.values()):
                cellname = f"{col}{rid+2}"
                resultFileData[cellname] = value

        with NamedTemporaryFile() as tmp:
            # resultFile.save(tmp.name)
            resultFile.save(tmp)
            tmp.seek(0)
            stream = tmp.read()
            headers = {
                'Content-Disposition': 'attachment; filename="Analyza.xlsx"'
            }
            return Response(stream, media_type='application/vnd.ms-excel', headers=headers)
        
    return router

