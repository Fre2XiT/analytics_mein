import aiohttp
import os

gqlurl = os.getenv("GQL_PROXY", "http://localhost:33001/api/gql")
async def queryGQL(query, variables, cookies):
    # gqlurl = "http://host.docker.internal:33001/api/gql"
    # gqlurl = "http://localhost:33001/api/gql"
    
    payload = {"query": query, "variables": variables}
    print("Query payload", payload, flush=True)
    async with aiohttp.ClientSession() as session:
        # print(headers, cookies)
        async with session.post(gqlurl, json=payload, cookies=cookies) as resp:
            # print(resp.status)
            if resp.status != 200:
                text = await resp.text()
                print(text, flush=True)
                raise Exception(f"Unexpected GQL response", text)
            else:
                text = await resp.text()
                # print(text, flush=True)
                response = await resp.json()
                # print(response, flush=True)
                return response

