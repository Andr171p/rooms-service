from pydantic import BaseModel


class TestModel(BaseModel):
    number: int
    text: str = ""


model = TestModel.model_validate(number=4)

print(model)
