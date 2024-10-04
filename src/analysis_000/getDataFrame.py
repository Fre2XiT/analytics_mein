from src.utils import flatten, queryGQL
import pandas as pd

async def resolve_json(variables, cookies):

    q="""
query ($where: GroupInputWhereFilter) {
  result: groupPage(limit: 10000, where: $where) {
    id
    name
    grouptype {
      id
      name
    }
    memberships(limit: 1000) {
      user {
        id
        email
      }
    }
  }
}
"""

    jsonresponse = await queryGQL(
        query=q,
        variables=variables,
        cookies=cookies
        )
    
    data = jsonresponse.get("data", {"result": None})
    result = data.get("result", None)
    assert result is not None, f"got {jsonresponse}"
    # print(result, flush=True)
    return result

async def resolve_flat_json(variables, cookies):
    result = await resolve_json(variables=variables, cookies=cookies)
    mapped = [{**group} for group in result]
    # print(mapped, flush=True)
    mapper = {
        "group_name": "name",
        "group_id": "id",
        "user": "memberships.user.email"
    }

    pivotdata = list(flatten(mapped, {}, mapper))
    # print(pivotdata)
    
    return pivotdata

async def resolve_df_pivot(variables, cookies):
    pivotdata = await resolve_flat_json(variables=variables, cookies=cookies)

    # print(pivotdata)
    df = pd.DataFrame(pivotdata)

    pdf = pd.pivot_table(df, values="user", index="group_name", columns=[], aggfunc="count")

    return pdf

ResolveA01 = resolve_df_pivot