from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel


class Lesson(BaseModel):
    number: int
    room: str
    teacher: str
    start: str
    end: str
    name: str
    info: Optional[str]
    

class Class(BaseModel):
    plan: List[Lesson]
    name: str   
    

class School(BaseModel):
    classes: Dict[str, Class]
    id: int
