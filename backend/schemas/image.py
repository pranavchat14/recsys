from pydantic import BaseModel

class ImageBase(BaseModel):
    title: str
    url: str

class ImageCreate(ImageBase):
    pass  # Additional fields can be added as needed for image creation

class Image(ImageBase):
    id: int

    class Config:
        from_attributes = True