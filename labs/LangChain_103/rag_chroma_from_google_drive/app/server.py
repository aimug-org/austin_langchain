from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import RedirectResponse
from langserve import add_routes
from rag_chroma import create_chain

app = FastAPI()
rag_chroma_chain = None


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")


@app.post("/initialize-chain")
async def initialize_chain_endpoint(folder_id: str = Body(..., embed=True)):
    global rag_chroma_chain
    try:
        rag_chroma_chain = create_chain(folder_id)

        # After initializing, add the routes for the chain
        add_routes(app, rag_chroma_chain, path="/rag-chroma")
        return {"message": "Chain initialized successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
