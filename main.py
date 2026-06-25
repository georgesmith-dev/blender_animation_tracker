from fastapi import FastAPI, Path, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic import Field
from typing import Optional, Literal

from sqlalchemy import create_engine, String, Integer, Float, select, delete, exists, update
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session


# Database
class Base(DeclarativeBase):
    pass


class Animation(Base):
    """defines the database entry shape"""

    __tablename__ = "animation"
    id: Mapped[int] = mapped_column(primary_key=True)
    scene_no: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    scene_desc: Mapped[str] = mapped_column(String, nullable=False)
    scene_frames: Mapped[int] = mapped_column(Integer, nullable=False)
    scene_length: Mapped[float] = mapped_column(Float, nullable=False)
    is_finished: Mapped[bool] = mapped_column(default=False)
    is_rendered: Mapped[bool] = mapped_column(default=False)


engine = create_engine("sqlite:///animation.db")
Base.metadata.create_all(engine)
 

# Pydantic Model
class NewScene(BaseModel):
    "defines the data shape of the new scene entry"

    scene_no: int
    scene_desc: str = Field(min_length=1, max_length=50)
    scene_frames: int = False
    scene_length: float = False
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
            scene_frames=scene.scene_frames,
            scene_length=scene.scene_length,
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
        "total frames": scene.scene_frames,
        "approx. length (seconds)": scene.scene_length,
        "finished": scene.is_finished,
        "rendered": scene.is_rendered,
    }


@app.get("/scenes/all")
def get_all_scenes():
    "returns a list of all scene numbers and corresponding description"
    with Session(engine) as session:
        result = session.execute(select(Animation))
        # Returns an entire list, maybe I should change it to a list of dicts?
        all_result = [
            f"scene: {scene.scene_no}, description: {scene.scene_desc}"
            for scene in result.scalars()
        ]
        return all_result


@app.get("/scenes/{num}")
def get_scene(num: int = Path(gt=0, description="scene no must be greater than 0")):
    "returns the scene number and corresponding description for an individual scene"
    with Session(engine) as session:
        stmt = select(Animation).where(Animation.scene_no == num)
        result = session.execute(stmt)
        for scene in result.scalars():
            return f"scene: {scene.scene_no}, description: {scene.scene_desc}"  # I need to add a clause for duplicate scene_no
        raise HTTPException(status_code=404, detail=f"Scene {num} was not found")


@app.delete("/scenes/{num}")
def delete_scene(num: int = Path(gt=0, description="scene no must be greater than 0")):
    "deletes the entire scene data based on number input"
    with Session(engine) as session:
        exists_stmt = exists().where(Animation.scene_no == num).select()
        exists_bool = session.scalar(exists_stmt)
        if not exists_bool:
            return f"scene {num} does not exist"

        stmt = delete(Animation).where(Animation.scene_no == num)
        session.execute(stmt)
        session.commit()
        return f"scene: {num} has been deleted"  # It is still 'deleting' even if nothing is there. Should query if it actually exists first


@app.patch("/scenes/{num}")
def update_scene(num: int = Path(gt=0, description="scene no must be greater than 0")):
    "updates scene data based on number input"
    with Session(engine) as session:
        pass


# Update individual columns ; change finished, rendered method
# get all scenes should filter by scene_no incrementing

# shoiuld I add a default value of 0 to scene_frames, scene_length?
# should I move the scene query validation to it's own function and call it to prevent re-using code?

# Need to add more defensive clauses within the functions
# Add way to create new table for inidivudal animations?
