from pydantic import BaseModel,ConfigDict

class ProjectResponse(BaseModel):
    id:int
    title:str
    slug:str
    description:str
    tech_stack:str
    github_url:str|None=None
    live_url:str | None = None
    featured:bool
    is_published:bool
    
    model_config = ConfigDict(from_attributes=True)