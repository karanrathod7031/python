"""Automation API routes — web, scheduling, workflows."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.automation.web_automation import WebAutomation
from app.automation.workflow import WorkflowEngine

router = APIRouter(prefix="/api/automation", tags=["automation"])

web_auto = WebAutomation()
workflow_engine = WorkflowEngine()


class SearchRequest(BaseModel):
    query: str


class URLRequest(BaseModel):
    url: str
    save_path: str = ""


class WorkflowRequest(BaseModel):
    name: str
    steps: list[dict[str, Any]]


@router.post("/web/search")
async def google_search(request: SearchRequest) -> dict[str, str]:
    return web_auto.google_search(request.query)


@router.post("/web/open")
async def open_url(request: URLRequest) -> dict[str, str]:
    return web_auto.open_url(request.url)


@router.post("/web/youtube")
async def open_youtube(query: str = "") -> dict[str, str]:
    return web_auto.open_youtube(query or None)


@router.post("/web/site")
async def open_site(name: str) -> dict[str, str]:
    return web_auto.open_site(name)


@router.post("/web/scrape")
async def scrape(request: URLRequest) -> dict[str, str]:
    return await web_auto.scrape_text(request.url)


@router.post("/web/download")
async def download(request: URLRequest) -> dict[str, str]:
    if not request.save_path:
        return {"status": "error", "message": "save_path is required"}
    return await web_auto.download_file(request.url, request.save_path)


@router.post("/workflow/create")
async def create_workflow(request: WorkflowRequest) -> dict[str, Any]:
    wf = workflow_engine.create_workflow(request.name, request.steps)
    return {
        "id": wf.id,
        "name": wf.name,
        "steps": len(wf.steps),
        "status": wf.status.value,
    }


@router.post("/workflow/{workflow_id}/execute")
async def execute_workflow(workflow_id: str) -> dict[str, Any]:
    try:
        wf = await workflow_engine.execute(workflow_id)
        return {
            "id": wf.id,
            "name": wf.name,
            "status": wf.status.value,
            "steps": [
                {"name": s.name, "status": s.status.value, "result": s.result, "error": s.error}
                for s in wf.steps
            ],
        }
    except ValueError as exc:
        return {"status": "error", "message": str(exc)}


@router.get("/workflow/list")
async def list_workflows() -> dict[str, Any]:
    workflows = workflow_engine.list_workflows()
    return {
        "workflows": [
            {"id": w.id, "name": w.name, "status": w.status.value, "steps": len(w.steps)}
            for w in workflows
        ]
    }
