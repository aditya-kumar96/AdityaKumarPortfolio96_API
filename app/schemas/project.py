from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class ProjectCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    slug: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=10)
    tech_stack: str = Field(min_length=2, max_length=500)
    github_url: HttpUrl | None = None
    live_url: HttpUrl | None = None
    featured: bool = False
    is_published: bool = False


class ProjectResponse(BaseModel):
    id: int
    title: str
    slug: str
    description: str
    tech_stack: str
    github_url: str | None = None
    live_url: str | None = None
    featured: bool
    is_published: bool

    model_config = ConfigDict(from_attributes=True)


class ProjectUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=150)
    slug: str | None = Field(default=None, min_length=3, max_length=160)
    description: str | None = Field(default=None, min_length=10)
    tech_stack: str | None = Field(default=None, min_length=2, max_length=500)
    github_url: HttpUrl | None = None
    live_url: HttpUrl | None = None
    featured: bool | None = None
    is_published: bool | None = None
