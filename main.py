from fastapi import FastAPI, Path, HTTPException
from pydantic import BaseModel
from pydantic import Field
from typing import Optional

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Float,
    select,
    delete,
    exists,
)
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

    scene_no: int = Field(ge=1)
    scene_desc: str = Field(min_length=1, max_length=100)
    scene_frames: int = Field(default=0, ge=1)
    scene_length: float = Field(default=0, ge=0.1)
    is_finished: bool = False
    is_rendered: bool = False


# Pydantic Model
class UpdatedScene(BaseModel):
    "defines the data shape of the updated scene entry"

    scene_no: Optional[int] = None
    scene_desc: Optional[str] = None
    scene_frames: Optional[int] = None
    scene_length: Optional[float] = None
    is_finished: Optional[bool] = None
    is_rendered: Optional[bool] = None


# FastAPI
app = FastAPI()


@app.get("/")
def root():
    "ensures the server is running"
    return {"message": "server is running!"}


# FastAPI app
def validate_scene(num):
    "validates scene exists before applying methods"
    with Session(engine) as session:
        exists_stmt = exists().where(Animation.scene_no == num).select()
        exists_bool = session.scalar(exists_stmt)
        if not exists_bool:
            return None
        return num


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
        all_result = {
            f"scene: {scene.scene_no}, description: {scene.scene_desc}"
            for scene in result.scalars()
        }
        return all_result


@app.get("/scenes/{num}")
def get_scene(num: int = Path(gt=0, description="scene no must be greater than 0")):
    "returns the scene number and corresponding description for an individual scene"
    validated_scene_no = validate_scene(num)
    if not validated_scene_no:
        return f"scene: {num} does not exist"

    with Session(engine) as session:
        stmt = select(Animation).where(Animation.scene_no == validated_scene_no)
        result = session.execute(stmt)
        for scene in result.scalars():
            return f"scene: {scene.scene_no}, description: {scene.scene_desc}"
        raise HTTPException(
            status_code=404, detail=f"Scene {validated_scene_no} was not found"
        )


@app.delete("/scenes/{num}")
def delete_scene(num: int = Path(gt=0, description="scene no must be greater than 0")):
    "deletes the entire scene data based on number input"

    validated_scene_no = validate_scene(num)
    if not validated_scene_no:
        return f"scene: {num} does not exist"

    with Session(engine) as session:
        stmt = delete(Animation).where(Animation.scene_no == validated_scene_no)
        session.execute(stmt)
        session.commit()
        return f"scene: {validated_scene_no} has been deleted"


@app.patch("/scenes/{num}")
def update_scene(
    updated_scene: UpdatedScene,
    num: int = Path(gt=0, description="scene no must be greater than 0"),
):
    "updates scene data based on number input"

    validated_scene_no = validate_scene(num)
    if not validated_scene_no:
        return f"scene: {num} does not exist"

    with Session(engine) as session:

        stmt = select(Animation).where(Animation.scene_no == validated_scene_no)
        result = session.execute(stmt)
        updated_scene_dict = updated_scene.model_dump()
        scene = result.scalars().first()

        for k, v in updated_scene_dict.items():
            if v != None:
                setattr(scene, k, v)

        session.commit()
        return {
            "message": "scene has been updated!",
            "scene no.": scene.scene_no,
            "scene description": scene.scene_desc,
            "total frames": scene.scene_frames,
            "approx. length (seconds)": scene.scene_length,
            "finished": scene.is_finished,
            "rendered": scene.is_rendered,
        }
