# -*- coding: utf-8 -*-
# #############################################################################
# Copyright (C) 2025 manatlan manatlan[at]gmail(dot)com
#
# MIT licence
#
# https://github.com/manatlan/RQ
# #############################################################################
import httpx
import logging
logger = logging.getLogger(__name__)

KNOWNVERBS = set([
    "GET",
    "POST",
    "DELETE",
    "PUT",
    "HEAD",
    "OPTIONS",
    "TRACE",
    "PATCH",
    "CONNECT",
])

jar=httpx.Cookies()
# AHTTP = httpx.AsyncClient(follow_redirects=True,verify=False,cookies=jar)
# AHTTP = httpx.Client(follow_redirects=True,verify=False,cookies=jar)

class ResponseError(httpx.Response):
    def __init__(self,error):
        self.error = error
        super().__init__(0,headers={},content=error.encode())
        
    def __repr__(self):
        return f"<{self.__class__.__name__} {self.error}>"

class ResponseTimeout(ResponseError):
    def __init__(self):
        ResponseError.__init__(self,"Timeout")

class ResponseUnreachable(ResponseError):
    def __init__(self):
        ResponseError.__init__(self,"Unreachable")

class ResponseInvalid(ResponseError):
    def __init__(self,url):
        ResponseError.__init__(self,f"Invalid {url}")

async def call(method, url:str,body:bytes|None=None, headers:httpx.Headers = httpx.Headers(), timeout:int=60_000, proxies=None) -> httpx.Response:
    logger.debug(f"CALL {method} {url} with body={body} headers={headers} timeout={timeout} proxies={proxies}")
    # Simule une réponse HTTP
    if method == "GET" and url.startswith("/testdict"):
        return httpx.Response(
            status_code=200,
            headers={"content-type": "application/json"},
            json={
                "coco": "VAL",
                "liste": [1, 2, {"key": "val"}]
            },
            request=httpx.Request(method, url, headers=headers, content=body and str(body))
        )
    elif method == "GET" and url.startswith("/testlist"):
        return httpx.Response(
            status_code=200,
            headers={"content-type": "application/json"},
            json=[1, 2, {"key": "val"}]
            ,
            request=httpx.Request(method, url, headers=headers, content=body and str(body))
        )
    elif method == "POST" and url.startswith("/test"):
        return httpx.Response(
            status_code=201,
            headers={"content-type": "application/json"},
            json=dict(result=body),
            request=httpx.Request(method, url, headers=headers, content=body and str(body))
        )
    else:
        return httpx.Response(
            status_code=404,
            headers={"content-type": "plain/text"},
            content="not found"
            ,
            request=httpx.Request(method, url, headers=headers, content=body and str(body))
        )


    assert method in KNOWNVERBS, f"Unknown HTTP verb {method}"
    try:

        AHTTP._get_proxy_map(proxies, False)

        return await AHTTP.request(
            method,
            url,
            data=body,
            headers=headers,
            timeout=timeout,   # sec to millisec
        )

        # info = "%s %s %s" % (r.http_version, int(r.status_code), r.reason_phrase)

    except (httpx.TimeoutException):
        return ResponseTimeout()
    except (httpx.ConnectError):
        return ResponseUnreachable()
    except (httpx.InvalidURL,httpx.UnsupportedProtocol,ValueError):
        return ResponseInvalid(url)

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    import asyncio
    async def main():
        x=await call("GET", "https://tools-httpstatus.pickup-services.com/200", proxies="http://77.232.100.132")
        print(x)
        # print(42)
    asyncio.run(main())

