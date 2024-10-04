from fastapi.responses import JSONResponse
async def process_df_as_json(df):
    jsondata = df.to_json(orient="records")
    return JSONResponse(content=jsondata)
