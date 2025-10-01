from pydantic import BaseModel, computed_field


class TestModel(BaseModel):
    first_name: str
    last_name: str

    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"


model = TestModel(first_name="John", last_name="Doe")

print(TestModel.model_validate({"first_name": "John", "last_name": "Doe"}))
