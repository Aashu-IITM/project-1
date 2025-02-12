from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
from typing import Optional, Dict, Any
from tasks import execute_task

app = FastAPI(
    title="Task Execution API",
    description="API for executing various tasks using natural language descriptions",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TaskRequest(BaseModel):
    task: str = Field(
        ..., description="Natural language description of the task to execute"
    )
    params: Optional[Dict[str, Any]] = Field(
        None, description="Optional parameters for task execution"
    )

    class Config:
        schema_extra = {
            "example": {
                "task": "Count the number of Wednesdays in /data/dates.txt and write to /data/wednesdays.txt",
                "params": {"additional_param": "value"},
            }
        }


@app.post("/run", response_model=Dict[str, Any])
async def run_task(request: TaskRequest):
    """
    Execute a task based on a natural language description.

    The task description is processed by an AI model to understand the requirements
    and execute the appropriate function.
    """
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task description missing")

    try:
        result = execute_task(request.task, request.params)
        return {
            "status": "success",
            "message": "Task executed successfully",
            "result": result,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid task description or parameters",
                "message": str(e),
            },
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal Server Error", "message": str(e)},
        )


@app.get("/read", response_class=FileResponse)
async def read_file(path: str = Query(..., description="Path of the file to read")):
    """
    Read and return the contents of a file.

    Parameters:
    - path: The path to the file, relative to the application root

    Returns:
    - The file contents as a response
    """
    # Security check: Prevent directory traversal
    normalized_path = os.path.normpath(path.lstrip("/"))
    if ".." in normalized_path or normalized_path.startswith("data"):
        raise HTTPException(
            status_code=400,
            detail="Invalid file path. Access to data directory and parent directories is not allowed",
        )

    absolute_path = os.path.join(os.getcwd(), normalized_path)

    if not os.path.exists(absolute_path):
        raise HTTPException(
            status_code=404, detail=f"File not found: {normalized_path}"
        )

    if not os.path.isfile(absolute_path):
        raise HTTPException(status_code=400, detail="Path does not point to a file")

    return FileResponse(absolute_path)


@app.get("/health")
async def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
