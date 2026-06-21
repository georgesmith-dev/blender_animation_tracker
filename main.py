from fastapi import FastAPI, Path, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic import Field
from typing import Optional, Literal

from sqlalchemy import create_engine, String, Integer, Float, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


# Database
class Base(DeclarativeBase):
    pass


class Animation(Base):
    """defines the database entry shape"""

    __tablename__ = "animation"
    id: Mapped[int] = mapped_column(primary_key=True)
    scene_no: Mapped[int] = mapped_column(Integer, nullable=False)
    scene_desc: Mapped[str] = mapped_column(String, nullable=False)
    is_finished: Mapped[bool] = mapped_column(default=False)
    is_rendered: Mapped[bool] = mapped_column(default=False)


engine = create_engine("sqlite:///animation.db")
Base.metadata.create_all(engine)


# Pydantic Model
class NewScene(BaseModel):
    "defines the data shape of the new scene entry"

    scene_no: int
    scene_desc: str = Field(min_length=1, max_length=50)
    is_finished: bool = False
    is_rendered: bool = False


# FastAPI
app = FastAPI()


# Local Server Check
@app.get("/")
def root():
    "ensures the server is running"
    return {"message": "server is running!"}


# FastAPI app
@app.post("/scenes")
def post_new_scene(scene: NewScene):
    """posts a new scene entry"""
    with Session(engine) as session:
        new_scene = Animation(
            scene_no=scene.scene_no,
            scene_desc=scene.scene_desc,
            is_finished=scene.is_finished,
            is_rendered=scene.is_rendered,
        )
        session.add(new_scene)
        session.commit()
        session.refresh(new_scene)

    return {
        "message": "new scene added!",
        "scene no.": scene.scene_no,
        "scene description": scene.scene_desc,
        "finished": scene.is_finished,
        "rendered": scene.is_rendered,
    }


@app.get("/scenes/all")
def get_all_scenes(): # Need this to work properly
    with Session(engine) as session:
        result = session.execute(select(Animation))
        for scene in result.scalars():
            print(scene.scene_no, scene.scene_desc)

# Update individual columns ; change finished, rendered method
# Delete individual columns method
# Retrieve all rows and columns (above, need to fix)

# Add way to create new table for inidivudal animations?
# Don't allow duplicate entries for "scene.no"

