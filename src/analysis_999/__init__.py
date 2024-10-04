import typing
import io
import datetime
import openpyxl

from tempfile import NamedTemporaryFile
from copy import copy

from fastapi import APIRouter, Request, Query, Response, UploadFile
from fastapi.responses import HTMLResponse

def createrouter(prefix: str):
    mainpath = "/vykazy"
    tags = ["vykazy"]

    router = APIRouter(prefix=prefix)
    @router.get(f"{mainpath}", tags=tags)
    async def page():
        content = """
    <body>
    <form action="/uploadfiles/" enctype="multipart/form-data" method="post">
    <input name="files" type="file" multiple>
    <input type="submit">
    </form>
    </body>
        """

        content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <title>Výkazy</title>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</head>
<body>

<div class="container-fluid p-5 bg-primary text-white text-center">
  <h1>Analýzy - výkazy</h1>
  <p>Vložte soubory!</p> 
</div>
  
<div class="container mt-5">
  <div class="row">
    <div class="col">
      <h3>Vstupní soubory</h3>
      <form action=".{mainpath}/uploadfiles" enctype="multipart/form-data" method="post">
        <input class="form-control" name="files" type="file" multiple>
        <br />
        <input class="btn btn-outline-success" type="submit">
    </form>
    </div>
  </div>
</div>

</body>
</html>
        """
        return HTMLResponse(content=content)
    


    @router.post(f"{mainpath}/uploadfiles", tags=tags)
    #async def create_upload_files(files: UploadFile = File(...)):
    #async def create_upload_files(request: Request):
    async def create_upload_files(files: typing.List[UploadFile]):
        
        result = []
        template = None
        resultfilename = "VsechnyVykazy.xlsx"
        for index, file in enumerate(files):
            contents = await file.read()
            memory = io.BytesIO(contents)
            if index == 0:
                resultfilename = file.filename
                template = contents
            wb = openpyxl.load_workbook(filename=memory, read_only=True)
            ws = wb['DataCelyRok']

            for index, row in enumerate(ws.rows):
                if index == 0 : 
                    continue
            
                names = ['name', 'month', 'date', 'desc', 'hours']
                newRow = dict(zip(names, map(lambda item: item.value, row)))
                if newRow['date'] is None:
                    print('has no date', newRow)
                elif not isinstance(newRow['date'], datetime.datetime) :
                    print('date has bad type', newRow)
                else:
                    result.append(newRow)
        
        
        # with open('./src/xlsx/vzor_vykaz.xlsx', 'rb') as f:
        #     template = f.read()
        
        memory = io.BytesIO(template)
        resultFile = openpyxl.load_workbook(filename=memory)

        resultFileCelyRok = resultFile['DataCelyRok']
        resultFileWs = resultFile['ProTisk']

        prevName = None
        prevMonth = None
        rowIndex = 16
        for item in result:
            currentName = item['name']
            currentMonth = item['date'].month
            if (currentName != prevName) or (currentMonth != prevMonth):
                #print(currentName, currentMonth)
                currentWs = resultFile.copy_worksheet(resultFileWs) 
                currentWs.title = f'{currentName}_{currentMonth}'
                rowIndex = 16
                
                print(currentName)
                
                names = currentName.split(' ')
                currentWs[f'C10'] = names[0]
                currentWs[f'C11'] = names[1]
                
                currentWs[f'C12'] = datetime.datetime(year=item['date'].year, month=item['date'].month, day=1)
                if item['date'].month == 12:
                    currentWs[f'E12'] = datetime.datetime(year=item['date'].year+1, month=1, day=1) + datetime.timedelta(days=-1)
                else:
                    currentWs[f'E12'] = datetime.datetime(year=item['date'].year, month=item['date'].month+1, day=1) + datetime.timedelta(days=-1)
                
                prevName = currentName
                prevMonth = currentMonth
                
            #currentWs.insert_rows(rowIndex)
            currentWs[f'A{rowIndex}'] = item['date']
            currentWs[f'B{rowIndex}'] = item['desc']
            currentWs[f'F{rowIndex}'] = item['hours']
            #for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            #    currentWs[f'{col}{rowIndex}']._style = copy(currentWs[f'{col}{rowIndex+1}']._style)
            rowIndex = rowIndex + 1
            
            
            # resultFileCelyRok.insert_rows(2)
            # resultFileCelyRok['A2'] = currentName
            # resultFileCelyRok['B2'] = item['date'].month
            # resultFileCelyRok['C2'] = item['date']
            # resultFileCelyRok['D2'] = item['desc']
            # resultFileCelyRok['E2'] = item['hours']
            # for col in ['A', 'B', 'C', 'D', 'E', 'F']:
            #     resultFileCelyRok[f'{col}2']._style = copy(resultFileCelyRok[f'{col}3']._style)




            #resultFileCelyRok.append([currentName, item['month'], item['date'], item['desc'], item['hours']])
        
        with NamedTemporaryFile() as tmp:
            # resultFile.save(tmp.name)
            resultFile.save(tmp)
            tmp.seek(0)
            stream = tmp.read()
            headers = {
                'Content-Disposition': f'attachment; filename="{resultfilename}"'
            }
            return Response(stream, media_type='application/vnd.ms-excel', headers=headers)
    return router

    pass