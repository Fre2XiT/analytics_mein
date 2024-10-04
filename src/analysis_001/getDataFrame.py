from src.utils import flatten, queryGQL, compose
import pandas as pd

async def ResolveA01(variables, cookies):
    assert "where" in variables, f"missing where in parameters"
    assert "startdate" in variables, f"missing startdate in parameters"
    assert "enddate" in variables, f"missing enddate in parameters"

#     q="""
# query analysis($user_id: UUID!, $startdate: DateTime, $enddate: DateTime) {
#   result: userById(id: $user_id) {
#     id
#     email
#     fullname
#     presences(where: {_and: [{event: {startdate: {_ge: $startdate}}}, {event:{enddate:{_le: $enddate}}}]}) {
#       id
#       presenceType { id name }
#       invitationType { id name }
#       event {
#         id
#         name
#         startdate
#         enddate
#         duration(unit: HOURS)
        
#         eventType {
#           id
#           name
#         }
        
#       }
#     }
#   }
# }
# """
    q = """
query analysis($where: UserInputWhereFilter!, $startdate: DateTime, $enddate: DateTime) {
  result: userPage(where: $where) {
    id
    fullname
    email
    presences(where: {_and: [{event: {startdate: {_ge: $startdate}}}, {event:{enddate:{_le: $enddate}}}]}) {
      id
      presenceType { id name }
      invitationType { id name }
      event {
        id
        name
        startdate
        enddate
        duration(unit: HOURS)
        
        eventType {
          id
          name
        }
        
      }
    }
  }
}"""
    jsonresponse = await queryGQL(
        query=q,
        variables=variables,
        cookies=cookies
        )
    
    data = jsonresponse.get("data", {"result": None})
    result = data.get("result", None)
    assert result is not None, f"got {jsonresponse}"
    # print(result, flush=True)

    # mapped = [{**group} for group in result]
    mapped = result
    # print(mapped, flush=True)
    mapper = {
        "user_id": "id",
        "user_email": "email",
        "user_fullname": "fullname",
        "event_id": "presences.event.id",
        "event_name": "presences.event.name",
        "event_duration": "presences.event.duration",
        "event_startdate": "presences.event.startdate",
        "event_enddate": "presences.event.enddate",
        "event_type_id": "presences.event.eventType.id",
        "event_type_name": "presences.event.eventType.name",
        "presence_type_id": "presences.presenceType.id",
        "presence_type_name": "presences.presenceType.name",
        "invitation_type_id": "presences.invitationType.id",
        "invitation_type_name": "presences.invitationType.name",
    }

    pivotdata = list(flatten(mapped, {}, mapper))
    print(pivotdata[0])
    df = pd.DataFrame(pivotdata)

    pdf = pd.pivot_table(df, values="event_duration", index="user_email", columns=["event_type_name"], aggfunc="count")

    return pdf


query = """
query analysis($where: UserInputWhereFilter!, $startdate: DateTime, $enddate: DateTime) {
  result: userPage(where: $where) {
    id
    fullname
    email
    presences(where: {_and: [{event: {startdate: {_ge: $startdate}}}, {event:{enddate:{_le: $enddate}}}]}) {
      id
      presenceType { id name }
      invitationType { id name }
      event {
        id
        name
        startdate
        enddate
        duration(unit: HOURS)
        
        eventType {
          id
          name
        }
        
      }
    }
  }
}"""

async def read_json(variables, cookies):
    assert "where" in variables, f"missing where in parameters"
    assert "startdate" in variables, f"missing startdate in parameters"
    assert "enddate" in variables, f"missing enddate in parameters"
    jsonresponse = await queryGQL(
        query=query,
        variables=variables,
        cookies=cookies
        )
    
    data = jsonresponse.get("data", {"result": None})
    result = data.get("result", None)
    assert result is not None, f"got {jsonresponse}"

    return result

async def flatten_data(jsonData):
    mapper = {
        "user_id": "id",
        "user_email": "email",
        "user_fullname": "fullname",
        "event_id": "presences.event.id",
        "event_name": "presences.event.name",
        "event_duration": "presences.event.duration",
        "event_startdate": "presences.event.startdate",
        "event_enddate": "presences.event.enddate",
        "event_type_id": "presences.event.eventType.id",
        "event_type_name": "presences.event.eventType.name",
        "presence_type_id": "presences.presenceType.id",
        "presence_type_name": "presences.presenceType.name",
        "invitation_type_id": "presences.invitationType.id",
        "invitation_type_name": "presences.invitationType.name",
    }
    # print(jsonData, flush=True)
    pivotdata = list(flatten(jsonData, {}, mapper))
    return pivotdata

async def as_data_frame(pivotdata):
    df = pd.DataFrame(pivotdata)
    return df
    
async def get_pivot_data(jsonData):
    mapper = {
        "user_id": "id",
        "user_email": "email",
        "user_fullname": "fullname",
        "event_id": "presences.event.id",
        "event_name": "presences.event.name",
        "event_duration": "presences.event.duration",
        "event_startdate": "presences.event.startdate",
        "event_enddate": "presences.event.enddate",
        "event_type_id": "presences.event.eventType.id",
        "event_type_name": "presences.event.eventType.name",
        "presence_type_id": "presences.presenceType.id",
        "presence_type_name": "presences.presenceType.name",
        "invitation_type_id": "presences.invitationType.id",
        "invitation_type_name": "presences.invitationType.name",
    }
    # print(jsonData, flush=True)
    pivotdata = list(flatten(jsonData, {}, mapper))
    # print(pivotdata[0], flush=True)
    df = pd.DataFrame(pivotdata)
    return df
    
  
async def get_pivot(df):
    pdf = pd.pivot_table(df, values="event_duration", index="user_email", columns=["event_type_name"], aggfunc="count")
    return pdf
    
     
from typing import Callable, Awaitable, Any
resolve: Callable[[dict, dict], Awaitable[Any]] = compose(read_json, flatten_data)
resolve_df: Callable[[dict, dict], Awaitable[Any]] = compose(read_json, flatten_data, as_data_frame)
resolve_df_pivot: Callable[[dict, dict], Awaitable[Any]] = compose(read_json, flatten_data, as_data_frame, get_pivot)
# resolve_flat: Callable[[dict, dict], Awaitable[Any]] = compose(read_json, flatten_data)
ResolveA01: Callable[[dict, dict], Awaitable[Any]] = resolve_df