from src.utils import flatten, queryGQL
import pandas as pd

#####################################################################################
#
# https://github.com/
#
#####################################################################################
query = """
query($where: GroupInputWhereFilter){
  result: groupPage(where:$where){
    memberships {
      group {
        id
        name
      }
      user {
        id
        fullname
        events(
          where: {_and: [{startdate: {_ge: "2021-03-19T08:00:00"}}, {enddate: {_le: "2025-05-19T08:00:00"}}]}
        ) {
          id
          name
          startdate
          enddate
          presences {
            id
            invitationType {
              id
            }
          }
        }
      }
    }
  }
}
"""

async def resolve_json(variables, cookies):
    assert "where" in variables, f"missing where in parameters"
    jsonresponse = await queryGQL(
        query=query,
        variables=variables,
        cookies=cookies
        )
    
    data = jsonresponse.get("data", {"result": None})
    result = data.get("result", None)
    assert result is not None, f"got {jsonresponse}"

    return result

async def resolve_flat_json(variables, cookies):
    jsonData = await resolve_json(variables=variables, cookies=cookies)
    mapper = {
        "groupID": "memberships.group.id",
        "groupName": "memberships.group.name",
        "userID": "memberships.user.id",
        "userFullname": "memberships.user.fullname",
        "eventID": "memberships.user.events.id",
        #event typeid
        "eventName": "memberships.user.events.name",
        "startdate": "memberships.user.events.startdate",
        "eventEndDate": "memberships.user.events.enddate",
        "presenceID": "memberships.user.events.presences.id",
        "invitationTypeID": "memberships.user.events.presences.invitationType.id",
}
    # print(jsonData, flush=True)
    pivotdata = list(flatten(jsonData, {}, mapper))
    return pivotdata

async def resolve_df_pivot(variables, cookies):
    pivotdata = await resolve_flat_json(variables=variables, cookies=cookies)

    # print(pivotdata)
    df = pd.DataFrame(pivotdata)

    pdf = pd.pivot_table(df, values="presenceID", index="userFullname", columns=["eventName"], aggfunc="count")

    return pdf


#####################################################################################
#
# 
#
#####################################################################################
import string
import openpyxl
from tempfile import NamedTemporaryFile
from fastapi import APIRouter, Request, Query, Response
from ..utils import process_df_as_html_page
import json
import re
import io
import datetime

def createRouter(prefix):
    mainpath = "/userpresence"
    tags = ["Počet odučených hodin"]

    router = APIRouter(prefix=prefix)
    WhereDescription = "filtr omezující vybrané skupiny"
    @router.get(f"{mainpath}/table", tags=tags, summary="HTML tabulka s daty pro výpočet kontingenční tabulky")
    async def user_classes_html(
        request: Request,
        where: str = Query(description=WhereDescription),
        startdate: datetime.datetime = Query(description=""),
        enddate: datetime.datetime = Query(description="")
    ):
        "HTML tabulka s daty pro výpočet kontingenční tabulky"
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        data = await resolve_flat_json(
            variables={
                "where": wherejson,
                "startdate": f"{startdate}",
                "enddate": f"{enddate}"
            },
            cookies=request.cookies
        )
        df = pd.DataFrame(data)
        return await process_df_as_html_page(df)
    
    @router.get(f"{mainpath}/pivot", tags=tags, summary="HTML kontingenční tabulka")
    async def user_classes_html(
        request: Request,
        where: str = Query(description=WhereDescription),
        startdate: datetime.datetime = Query(description=""),
        enddate: datetime.datetime = Query(description="")
    ):
        "pivot table"
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        data = await resolve_df_pivot(
            variables={
                "where": wherejson,
                "startdate": f"{startdate}",
                "enddate": f"{enddate}"
            },
            cookies=request.cookies
        )
        
        return await process_df_as_html_page(data)
    
    @router.get(f"{mainpath}/flatjson", tags=tags, summary="Data ve formátu JSON transformována do podoby vstupu pro kontingenční tabulku")
    async def user_classification_flat_json(
        request: Request, 
        where: str = Query(description=WhereDescription),
        startdate: datetime.datetime = Query(description=""),
        enddate: datetime.datetime = Query(description="") 
    ):
        "Data ve formátu JSON transformována do podoby vstupu pro kontingenční tabulku"
        print(where, flush=True)
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where)
        print(wherevalue, flush=True) 
        wherejson = json.loads(wherevalue)
        pd = await resolve_flat_json(
            variables={
                "where": wherejson,
                "startdate": f"{startdate}",
                "enddate": f"{enddate}"
            },
            cookies=request.cookies
        )
        return pd

    @router.get(f"{mainpath}/json", tags=tags, summary="Data ve formátu JSON (stromová struktura) nevhodná pro kontingenční tabulku")
    async def user_classification_json(
        request: Request, 
        where: str = Query(description=WhereDescription),
        startdate: datetime.datetime = Query(description=""),
        enddate: datetime.datetime = Query(description="") 
    ):
        "Data ve formátu JSON (stromová struktura) nevhodná pro kontingenční tabulku"
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        pd = await resolve_json(
            variables={
                "where": wherejson,
                "startdate": f"{startdate}",
                "enddate": f"{enddate}"
            },
            cookies=request.cookies
        )
        return pd

    @router.get(f"{mainpath}/xlsx", tags=tags, summary="Xlsx soubor doplněný o data v záložce 'data' (podle xlsx vzoru)")
    async def user_classification_xlsx(
        request: Request, 
        where: str = Query(description=WhereDescription),
        startdate: datetime.datetime = Query(description=""),
        enddate: datetime.datetime = Query(description="") 
    ):
        "Xlsx soubor doplněný o data v záložce 'data' (podle xlsx vzoru)"
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        flat_json = await resolve_flat_json(
            variables={
                "where": wherejson,
                "startdate": f"{startdate}",
                "enddate": f"{enddate}"
            },
            cookies=request.cookies
        )

        with open('./src/xlsx/vzor2.xlsx', 'rb') as f:
            content = f.read()
        
        memory = io.BytesIO(content)
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