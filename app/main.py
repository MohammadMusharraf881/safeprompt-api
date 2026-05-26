from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import re
import time

app = FastAPI(
    title="SafePrompt API",
    description="Prompt injection detection and sanitization service",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prompt injection patterns
INJECTION_PATTERNS = [
    r"ignore\b.{0,30}(instructions?|prompts?|rules?|constraints?)",
    r"disregard (all |previous |prior |above )?(instructions?|prompts?|rules?)",
    r"forget (everything|all|your instructions?|what you were told)",
    r"you are now (a |an )?(different|new|unrestricted|jailbroken)",
    r"act as (if you are|a |an )?(different|evil|unrestricted|DAN)",
    r"do anything now",
    r"jailbreak",
    r"bypass (your |all )?(safety|restrictions?|guidelines?|filters?)",
    r"pretend (you are|to be) (a |an )?(different|unrestricted|evil)",
    r"(system|admin|root) (prompt|override|access)",
    r"\\n\\n(human|assistant|system):",
    r"<\|im_start\|>",
    r"\[INST\]|\[/INST\]",
    r"### (instruction|system|human|assistant)",
]

class PromptRequest(BaseModel):
    prompt: str
    strict_mode: Optional[bool] = False

class PromptResponse(BaseModel):
    safe: bool
    risk_score: float
    threats_detected: list[str]
    sanitized_prompt: Optional[str]
    processing_time_ms: float

class HealthResponse(BaseModel):
    status: str
    version: str

def analyze_prompt(prompt: str, strict_mode: bool = False) -> dict:
    threats = []
    text_lower = prompt.lower()

    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            threats.append(pattern)

    # Heuristic checks
    if len(prompt) > 10000:
        threats.append("excessive_length")
    if prompt.count('\n') > 50:
        threats.append("excessive_newlines")
    if strict_mode and any(kw in text_lower for kw in ["override", "unlock", "unrestricted"]):
        threats.append("suspicious_keywords_strict")

    risk_score = min(1.0, len(threats) * 0.25)
    sanitized = re.sub(r'[<>{}]', '', prompt) if threats else prompt

    return {
        "threats": threats,
        "risk_score": risk_score,
        "sanitized": sanitized,
    }

@app.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok", "version": "1.0.0"}

@app.post("/analyze", response_model=PromptResponse)
def analyze(req: PromptRequest):
    start = time.time()
    if not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    result = analyze_prompt(req.prompt, req.strict_mode or False)
    elapsed = (time.time() - start) * 1000

    return PromptResponse(
        safe=len(result["threats"]) == 0,
        risk_score=result["risk_score"],
        threats_detected=result["threats"],
        sanitized_prompt=result["sanitized"],
        processing_time_ms=round(elapsed, 2),
    )

@app.get("/")
def root():
    return {"message": "SafePrompt API is running", "docs": "/docs"}
