from contextlib import asynccontextmanager
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field
from api.service import get_service
from api.schemas import PredictionResponse


@asynccontextmanager
async def lifespan(app):
    service = get_service()
    # Compile SHAP's masking kernel and cache a real held-out opening prediction
    # before readiness, rather than making the first visitor pay that cold cost.
    opening_case = service.cases[2]
    service.predict(opening_case['features'], opening_case['id'])
    yield


app = FastAPI(title='VesselRisk',version='1.0',lifespan=lifespan,
              description='Leakage-audited coronary risk research. Not for clinical diagnosis.')


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra='forbid',strict=True)
    features: dict[str, int | float | str] = Field(description='All 55 eligible clinical inputs, keyed by source column name')
    case_id: str | None = Field(default=None,description='Optional held-out demo case. Its row remains excluded even if inputs are edited.')


@app.get('/health')
def health():
    s = get_service()
    return {'status':'ready','version':s.registry['version'],'targets':list(s.bundles),'artifact_integrity':'verified'}


@app.get('/schema')
def schema():
    return {'features':get_service().schema,'required_inputs':55}


@app.get('/cases')
def cases():
    return {'cases':get_service().cases,'note':'Selected to demonstrate contrasting outputs, not a representative performance sample. All predictions use models that excluded the case.'}


@app.get('/model-info')
def model_info():
    return get_service().registry


@app.get('/evidence')
def evidence():
    return get_service().evidence


@app.post('/predict',response_model=PredictionResponse)
@app.post('/explain',response_model=PredictionResponse)
def predict(request: PredictionRequest):
    try:
        return get_service().predict(request.features,request.case_id)
    except ValueError as error:
        raise HTTPException(status_code=422,detail=str(error)) from error


@app.get('/report')
def report():
    path = Path(__file__).resolve().parents[1]/'report/VesselRisk-Track-A.pdf'
    if not path.exists():
        raise HTTPException(status_code=404,detail='Report file is unavailable')
    return FileResponse(path,media_type='application/pdf',filename=path.name)
