from fastapi import FastAPI, UploadFile, File, Form, Request
from pydantic import BaseModel
from src.Statistics import statistics_generator
from src.CountryDefiner import identify_country_by_prefix
from src.FindAbonnent import find_abonnent
from src.ChartsCreation import chart_generation
from src.Similarities import group_similar_values_across_sources
from src.HtmlReport import generate_html_report
from typing import List, Optional
import json
import math
import time

app = FastAPI(debug=True, port=8030)

def sanitize_data(data):
    if isinstance(data, dict):
        return {k: sanitize_data(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_data(item) for item in data]
    elif isinstance(data, float):
        if math.isinf(data) or math.isnan(data):
            return None  # or any valid replacement
        return data
    else:
        return data

class Filters(BaseModel):
    type: Optional[str] = None
    app: Optional[str] = None
    phone_number: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class Call(BaseModel):
    type: Optional[str] = None
    app: Optional[str] = None
    number: Optional[str] = None
    duration: Optional[float] = None
    timestamp: Optional[str] = None
    status: Optional[str] = None
    name: Optional[str] = None

class CallHistory(BaseModel):
    call_history: List[Call]
    filters: Optional[Filters] = None
    language: Optional[str] = 'ru'

class SimilaritySource(BaseModel):
    source: str
    call_history: List[Call]

class SimilarityRequest(BaseModel):
    sources: List[SimilaritySource]
    target_field: Optional[str] = None
    target_value: Optional[str] = None

# @app.middleware("http")
# async def log_request_time(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     elapsed_time = time.time() - start_time
#     print(f"Request {request.url.path} processed in {elapsed_time:.4f} seconds")
#     return response

@app.post("/")
def read_root(data: CallHistory):
    calls = data.model_dump().get("call_history")
    language = data.model_dump().get("language")
    statistics = statistics_generator(calls)
    chart_generation(statistics, language)
    generate_html_report()
    return statistics

@app.post("/filters/")
def filtered_data(data: CallHistory):
    test_database_path = 'test_database.json'
    with open(test_database_path, 'r', encoding='utf-8') as file:
        test_database = json.load(file)
    with open('test_operator_database.json', 'r', encoding='utf-8') as file:
        operator_data = json.load(file)
    abonnents = operator_data["abonnents"]
    calls = data.model_dump().get("call_history")
    filters = data.model_dump().get("filters")
    language = data.model_dump().get("language")
    abonnent = None
    country = None
    prefix = None
    if filters.get("phone_number") is not None:
        abonnent = find_abonnent(abonnents, filters.get("phone_number"))
    if abonnent:
        print(abonnent.get("phoneNumber", ""), "|", abonnent.get("lastName", ""), "|", abonnent.get("firstName", ""))
    if filters.get("phone_number") is not None:
        country = identify_country_by_prefix(filters.get("phone_number"))
    if country:
        operator = "test"
        print(country, "|", operator)
    statistics = statistics_generator(calls, filters)
    chart_generation(statistics, language)
    sanitized_statistics = sanitize_data(statistics)
    return sanitized_statistics

@app.post("/upload_json/")
async def upload_json(file: UploadFile = File(...)):
    # Optional: Check if the file has a .json extension
    if not file.filename.endswith(".json"):
        return {"error": "Only JSON files are accepted."}

    try:
        # Read the file content (this is asynchronous)
        contents = await file.read()
        # Decode bytes to string and parse JSON
        json_data = json.loads(contents.decode("utf-8"))
    except Exception as e:
        return {"error": f"Failed to read/parse the JSON file: {e}"}

    try:
        # Validate the JSON structure using your CallHistory model
        call_history_data = CallHistory.model_validate(json_data)
        call_history_dict = call_history_data.model_dump().get("call_history")
        language = call_history_data.model_dump().get("language")
        filters = call_history_data.model_dump().get("filters")
    except Exception as e:
        return {"error": f"JSON data does not match the required schema: {e}"}
    # Process the data as you do in your other endpoints
    statistics = statistics_generator(call_history_dict, filters)
    chart_generation(statistics, language)
    generate_html_report()

    # Optionally sanitize the output before returning
    sanitized_statistics = sanitize_data(statistics)
    return sanitized_statistics

@app.post("/similarities/")
def find_similarities(data: SimilarityRequest):
    """
    Accepts multiple JSON sources (each with its own call_history),
    annotates each call with its source, finds any similarities
    (shared key–value pairs across calls from different sources),
    and optionally filters the result by a specific field.
    """
    all_calls = []
    for source_item in data.sources:
        source = source_item.source
        # Convert each Call (Pydantic model) to a dict and add its 'source'
        for call in source_item.call_history:
            call_dict = call.model_dump()
            call_dict["source"] = source
            all_calls.append(call_dict)
    
    result = group_similar_values_across_sources(all_calls)
    
    # Filter result by target_field if provided
    if data.target_field:
        result = [group for group in result if group["field"] == data.target_field]
    
    # (Optional) Write the result to a file
    # write_result_to_file(result)
    
    return result

@app.post("/similarities_files/")
async def find_similarities_from_files(
    sources: List[UploadFile] = File(...),
    target_field: Optional[str] = Form(None),
    target_value: Optional[str] = Form(None)
):
    """
    Accepts multiple JSON files (each containing a 'call_history') as file uploads.
    Each call is annotated with the source (the file name). Then, calls are grouped by similar
    key–value pairs that appear in calls from at least two different sources.
    
    Optional form fields 'target_field' and 'target_value' can be used to filter the results.
    """
    all_calls = []
    for source_file in sources:
        contents = await source_file.read()
        try:
            data = json.loads(contents.decode('utf-8'))
        except Exception as e:
            return {"error": f"Error parsing JSON in file {source_file.filename}: {e}"}
        if "call_history" in data:
            for call in data["call_history"]:
                call["source"] = source_file.filename
                all_calls.append(call)
        else:
            return {"error": f"File {source_file.filename} does not contain 'call_history'"}
    result = group_similar_values_across_sources(all_calls)
    if target_field:
        result = [group for group in result if group["field"] == target_field]
    if target_value:
        result = [group for group in result if str(group["value"]) == target_value]
    # (Optional) write_result_to_file(result)
    return result