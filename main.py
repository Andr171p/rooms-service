from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastauth import AuthMiddleware, CurrentUser

app = FastAPI()


@app.get("/home")
async def home() -> dict[str, str]:
    return {"message": "home"}


@app.get("/hello")
async def root(user: CurrentUser) -> dict[str, str]:
    print(user)
    return {"Hello": "World"}


app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(
    AuthMiddleware,
    realm="messenger",
    base_url="http://localhost:8000/api/v1/",
    public_endpoints=["/home"]
)
