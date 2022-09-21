from typing import Dict

from aiohttp import ClientSession
from bs4 import BeautifulSoup
from fastapi import FastAPI, Header, HTTPException

from app.models import Class, Lesson, School

app = FastAPI()


class vplan:
    cached_plan: Dict[int, BeautifulSoup] = {}
    etag: str = ""
    last_modified: str = ""

    async def get_plan(self, _school: int, auth: str) -> BeautifulSoup | HTTPException:
        async with ClientSession(headers={
                "Authorization": auth}) as session: #! Change this, a ClientSession should not be created that often.
            resp = await session.get(f"https://www.stundenplan24.de/{_school}/mobil/mobdaten/Klassen.xml",
                                     headers={
                                         "ETag": self.etag,
                                         "If-Modified-Since": self.last_modified
                                     }
                                     )
            if resp.status not in [401, 302, 304]:
                self.last_modified, self.etag = resp.headers["last-modified"], resp.headers["etag"]
                self.cached_plan[_school] = BeautifulSoup(await resp.text(), features="xml")
            elif resp.status == 401:
                return HTTPException(401, "Invalid authorization Header")
            return self.cached_plan[_school]


_plan = vplan()


@app.get("/school/{school}/", responses={
    200: {
        "model": School,
        "description": "Class in school requested"
    },
    401: {
        "type": HTTPException,
        "description": "Authorization failed, check Authorization Header",
        "content": {
            "application/json": {
                "example": {"status_code":401,"detail":"Invalid authorization Header","headers":None}
            }
        },
    },
})
async def get_school_plan(school: int, authorization: str = Header(...)):
    """Scrapes the plan for a given school, returns `HTTPException` if Auth fails or a 404 is hit

    Path Parameters
    ---------------
    `school : int`  
        the school code used on stundenplan24
    
    Headers
    -------
    `Authorization : str`  
        Authorization header to authenticate with stundenplan24.
        This is Basic Auth e.g. generated by `aiohttp.BasicAuth()`

    Returns
    -------
    `School`  
        Returns the requested School plan
    """
    plan = await _plan.get_plan(school, authorization)
    if isinstance(plan, HTTPException): return plan
    return School(
        id=school,
        classes={_class.find("Kurz").string:
                 Class(
            name=_class.find("Kurz").string,
            plan=[(Lesson(
                room=lesson.find("Ra").string or "---",
                teacher=lesson.find("Le").string or "---",
                number=lesson.find("St").string,
                start=lesson.find("Beginn").string,
                end=lesson.find("Ende").string,
                name=lesson.find("Fa").string,
                info=lesson.find("If").string,
            ))
                for lesson in _class.find("Pl").find_all("Std")]
        ) for _class in plan.findAll("Kl")}
    )


@app.get("/school/{school}/class/{_class}", responses={
    200: {
        "model": Class,
        "description": "Class in school requested"
    },
    401: {
        "type": HTTPException,
        "description": "Authorization failed, check Authorization Header",
        "content": {
            "application/json": {
                "example": {"status_code":401,"detail":"Invalid authorization Header","headers":None}
            }
        },
    },
    404: {
        "type": HTTPException,
        "description": "School or class not find, check path parameters",
        "content": {
            "application/json": {
                "example": {"status_code":404,"detail":"Class 05-4 not found for school 12121434","headers":None}
            }
        },
    }
})
async def get_class_plan(school: int, _class: str, authorization: str = Header(...)):
    """Scrapes the plan for a given class, returns `HTTPException` if Auth fails or a 404 is hit

    Path Parameters
    ---------------
    `school : int`  
        the school code used on stundenplan24  
    `_class : str`  
        the class to search for  
        for classes containing a `/` replace it with a `-`  
        e.g. `05-4` instead of `05/4`
    
    Headers
    -------
    `Authorization : str`  
        Authorization header to authenticate with stundenplan24.  
        This is Basic Auth e.g. generated by `aiohttp.BasicAuth()`

    Returns
    -------
    Class
        Returns a class schema containing all the lessons
    """
    _class = _class.replace("-", "/")
    plan = await _plan.get_plan(school, authorization)
    if isinstance(plan, HTTPException) or not plan.find("Kurz", string=_class):
        return (HTTPException(status_code=404, detail=f"Class {_class} not found for school {school}")
                if not isinstance(plan, HTTPException)
                else plan
                )
    _class = plan.find("Kurz", string=_class).parent
    return Class(
        name=_class.find("Kurz").string,
        plan=[(Lesson(
            room=lesson.find("Ra").string or "---",
            teacher=lesson.find("Le").string or "---",
            number=lesson.find("St").string,
            start=lesson.find("Beginn").string,
            end=lesson.find("Ende").string,
            name=lesson.find("Fa").string,
            info=lesson.find("If").string,
        ))
            for lesson in _class.find("Pl").find_all("Std")]
    )
