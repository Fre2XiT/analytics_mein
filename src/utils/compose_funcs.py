def compose(*funcs):
    [first, *others] = funcs
    async def result(variables, cookies):
        partialresult = await first(variables, cookies)
        for f in others:
            partialresult = await f(partialresult)
        return partialresult
    return result