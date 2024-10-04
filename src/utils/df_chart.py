from io import BytesIO
import matplotlib.pyplot as plt

from fastapi.responses import HTMLResponse
async def process_df_as_svg_chart(df):
    df.plot.pie(
        figsize=(40, 20), 
        subplots=True,
        legend=False,
        rotatelabels=True
        )
    with BytesIO() as f:
        plt.savefig(f, format="svg")
        svgresult = f.getvalue().decode()
    return HTMLResponse(content=svgresult)

