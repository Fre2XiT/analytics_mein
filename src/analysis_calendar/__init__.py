from src.utils import flatten, queryGQL
import pandas as pd
import datetime
#####################################################################################
#
# https://github.com/Hieulangtu/Pivot-table
#
#####################################################################################
query = """query eventpage($where: EventInputFilter){
  result: eventPage(orderby: "startdate", where: $where) {
    __typename
    id
    name
    startdate
    enddate
    
    duration(unit: HOURS)
    description
    place
    placeId
    
    groups {
      id
      name
    }
    
    users {
      id
      name
      surname
      email
    }
    
  }
}"""

async def resolve_json(variables, cookies):
    assert "where" in variables, f"missing where in parameters"
    jsonresponse = await queryGQL(
        query=query,
        variables=variables,
        cookies=cookies
        )
    
    # print("jsonresponse", jsonresponse, flush=True)
    data = jsonresponse.get("data", {"result": None})
    result = data.get("result", None)
    assert result is not None, f"got {jsonresponse}"

    return result

async def resolve_flat_json(variables, cookies):
    jsonData = await resolve_json(variables=variables, cookies=cookies)
    mapper = {
        "event_id": "id",
        "event_name": "name",
        "event_startdate": "startdate",
        "event_enddate": "enddate",
        "event_duration": "duration",
        "user_id": "users.id",
        "user_email": "users.email",
        "user_fullname": "users.fullname",
        "group_name": "groups.name",
        "group_id": "groups.id",
        "place_id": "placeId"
    }
    # print(jsonData, flush=True)
    pivotdata = list(flatten(jsonData, {}, mapper))
    return pivotdata

async def resolve_df_pivot(variables, cookies):
    pivotdata = await resolve_flat_json(variables=variables, cookies=cookies)

    # print(pivotdata)
    df = pd.DataFrame(pivotdata)

    pdf = pd.pivot_table(df, values="user_fullname", index="group_name", columns=["event_duration"], aggfunc="sum")

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
from fastapi.responses import HTMLResponse
from ..utils import process_df_as_html_page
import json
import re
import io

def createRouter(prefix):
    mainpath = "/events"
    tags = ["Kalendář"]

    router = APIRouter(prefix=prefix)
    WhereDescription = "filtr omezující vybrané skupiny"
    @router.get(f"{mainpath}/table", tags=tags, summary="HTML tabulka s daty pro výpočet kontingenční tabulky")
    async def events_html(
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
    
    @router.get(f"{mainpath}/flatjson", tags=tags, summary="Data ve formátu JSON transformována do podoby vstupu pro kontingenční tabulku")
    async def events_flat_json(
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

    @router.get(f"{mainpath}/json", tags=tags, summary="Data ve formátu JSON (stromová struktura) nevhodná pro kontingenční tabulku")
    async def events_json(
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

    @router.get(f"{mainpath}/xlsx", tags=tags, summary="Xlsx soubor doplněný o data v záložce 'data' (podle xlsx vzoru)")
    async def events_xlsx(
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


    @router.get(f"{mainpath}/timetable", tags=tags, summary="Xlsx soubor doplněný o data v záložce 'data' (podle xlsx vzoru)")
    async def events_timetable_html(
        request: Request, 
        where: str = Query(description=WhereDescription), 
    ):
        "html fragment"
        wherevalue = None if where is None else re.sub(r'{([^:"]*):', r'{"\1":', where) 
        wherejson = json.loads(wherevalue)
        tree_json = await resolve_json(
            variables={
                "where": wherejson
            },
            cookies=request.cookies
        )
        tree_json = [{
            **event, 
            "_startdate": datetime.datetime.fromisoformat(event["startdate"]),
            "_enddate": datetime.datetime.fromisoformat(event["enddate"])
            } for event in tree_json]
        
        index = {}
        for event in tree_json:
            key = event["startdate"][:10]
            l = index.get(key, None)
            if l is None:
                l = []
                index[key] = l
            l.append(event)

        days = [day for day in index.keys()]
        days.sort()
        # print("days", days, flush=True)
        result = ["""<div style="width: 100%">"""]

        def events_overlap(eventA, eventB):
            # print("eventA", eventA, flush=True)
            # print("eventB", eventB, flush=True)
            if eventA["_startdate"] <= eventB["_startdate"] <= eventA["_enddate"]:
                return True
            if eventB["_startdate"] <= eventA["_startdate"] <= eventB["_enddate"]:
                return True
            return False
            
        for day in days:
            events_in_day = index[day]
            collections = [list() for event in events_in_day]
            # print("events_in_day", events_in_day, flush=True)
            for event in events_in_day:
                # print("event", event, flush=True)
                for collection in collections:
                    overlaptest = filter(lambda item: item, map(lambda item: events_overlap(event, item), collection))
                    overlaps = next(overlaptest, None)
                    if overlaps is None:
                        break
                collection.append(event)
            dayfragments = []
            for collection in collections:
                rowfragments = []    
                currentleft = 0
                for event in collection:
                    starttime = event["_startdate"].time()
                    endtime = event["_enddate"].time()
                    position = (
                        datetime.datetime.combine(datetime.date.min, starttime) - datetime.datetime.combine(datetime.date.min, datetime.time(hour=7))) / datetime.timedelta(hours=1) / (18 - 7) * 100
                    width = ((datetime.datetime.combine(datetime.date.min, endtime) - datetime.datetime.combine(datetime.date.min, starttime)) / datetime.timedelta(hours=1)) / (18 - 7) * 100
                    # eventfragment = f"""<div class="d-" style="margin-left: {position}%; width: {width}%; background-color: rgb(0,100,0, 0.3); border:solid 1px rgb(0,100,0, 0.5);">
                    # <div class="" >{event["name"]}</div>
                    # <div class="d-" >{starttime} - {endtime}</div>
                    # <div class="d-" >M</div>
                    # <div class="d-" >O</div>
                    # <div class="d-" >G</div>
                    # </div>"""
                    # eventfragment = f"""<div class="d-inline" style="margin-left: {position}%; width: {width}%; background-color: rgb(0,100,0, 0.3); border:solid 1px rgb(0,100,0, 0.5);">
                    # {event["name"]}</br>
                    # {starttime} - {endtime}</br>
                    # M</br>
                    # O</br>
                    # G</br>
                    # </div>"""
                    if currentleft < position:
                        spacewidth = position - currentleft
                        eventfragment = f"""<div style="width: {spacewidth}%; "></div>"""
                        rowfragments.append(eventfragment)
                        currentleft = position
                    currentleft = position + width
                    eventfragment = f"""<div class="" style="width: {width}%; background-color: rgb(0,100,0, 0.3); border:solid 1px rgb(0,100,0, 0.5);">
                    {event["name"]}<br />
                    {starttime} - {endtime}<br />
                    M{event["id"]}<br />
                    O{event["startdate"]}<br />
                    G
                    </div>"""
                    rowfragments.append(eventfragment)
                if len(rowfragments) > 0:
                    rowfragments = "".join(rowfragments)
                    dayfragments.append(
                        f"""
                                    <div class="d-flex">
                                        {rowfragments}                                    
                                    </div>
                        """
                    )
            dayfragments = "".join(dayfragments)
            result.append(f"""
                            <div class="row">
                                <div class="col col-2" style="border: solid 1px grey;">
                                        {day}                                    
                                </div>
                                <div class="col col-10" style="border: solid 1px grey;">
                                        {dayfragments}                                    
                                </div>
                            </div>
                        """)
        result.append("</div>")


        pre="""<!DOCTYPE html>
<html lang="en">
<head>
  <title>Bootstrap 5 Example</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</head>
<body class="">
 
<div class="container-fluid mt-5">"""
        post="""</div>

</body>
</html>"""



        return HTMLResponse(pre+"".join(result)+post)

    return router