from fastapi.responses import HTMLResponse
async def process_df_as_html_table(df):
    classes = 'table table-striped table-bordered table-hover table-sm'

    return HTMLResponse(content=df.to_html(classes=classes))

async def process_df_as_html_page(df):
    classes = 'table table-striped table-bordered table-hover table-sm'
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
    {0}
    </body>
    """    
    short = df.to_html(classes=classes)
    print("short", short, flush=True)
    long = template.replace("{0}", short)
    return HTMLResponse(content=long)

