import asyncio
import json

from ..schemas import RunDetail


async def stream_recommendation(run: RunDetail):
    stages = ["retrieve", "assemble", "synthesise", "verify"]
    for stage in stages:
        yield f"event: stage\ndata: {json.dumps({'stage': stage, 'status': 'running'})}\n\n"
        await asyncio.sleep(0.5)
        yield f"event: stage\ndata: {json.dumps({'stage': stage, 'status': 'complete'})}\n\n"

    recommendation = {
        "text": f"Based on the analysis of run {run.id}, we recommend optimizing power mix...",
        "citations": [{"article": "Perpres 98/2021 Pasal 3"}],
        "confidence": 0.84,
    }
    yield f"event: recommendation\ndata: {json.dumps(recommendation)}\n\n"
    yield f"event: done\ndata: {json.dumps({'run_id': run.id})}\n\n"
