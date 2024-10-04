from fastapi.responses import HTMLResponse, StreamingResponse, Response
from io import BytesIO

async def process_df_as_excel(df):
    with BytesIO() as f:
        df.to_excel(f)
        bytesresult = f.getvalue()
    headers = {'Content-Disposition': 'attachment; filename="analyza001.xlsx"'}
    media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    return Response(bytesresult, media_type=media_type, headers=headers)

