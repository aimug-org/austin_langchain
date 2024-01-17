from typing import List
from fastapi.routing import APIRoute
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import RedirectResponse
from langserve import add_routes
from rag_chroma import create_chain

app = FastAPI()


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@app.get("/list-folder-routes")
def list_folder_routes():
    routes = set()
    for route in app.routes:
        if isinstance(route, APIRoute):
            if route.name == "invoke" and route.path.startswith(
                "/folders/{folder_id}/"
            ):
                routes.add(route.path)
    return list(routes)


@app.post("/initialize-chain")
async def initialize_chain_endpoint(
    folder_id: str = Body(..., embed=True), name: str = Body(..., embed=True)
):
    try:
        chain = create_chain(folder_id)
        new_path = f"/folders/{folder_id}/{name}"
        add_routes(app, chain, path=new_path)
        return {
            "message": f"Chain initialized successfully at {new_path}",
            "path": f"{new_path}/invoke",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
