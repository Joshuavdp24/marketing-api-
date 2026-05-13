# Marketing API — Content Module Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a deployable FastAPI service with 6 AI-powered content generation endpoints, API key auth, and Railway deployment config.

**Architecture:** Stateless FastAPI app — each request loads a system prompt, calls Claude via the Anthropic Async SDK, and returns structured JSON. No database. Auth is a middleware that validates Bearer tokens against a comma-separated env var.

**Tech Stack:** Python 3.11+, FastAPI, Anthropic SDK (`anthropic`), Pydantic v2, pydantic-settings, pytest

---

## File Map

| File | Responsibility |
|------|---------------|
| `requirements.txt` | All dependencies pinned |
| `.env.example` | Template for required env vars |
| `config.py` | Loads and validates env vars via pydantic-settings |
| `models/content.py` | All Pydantic request/response schemas |
| `main.py` | FastAPI app, auth middleware, health endpoint, router registration |
| `prompts/blog.md` | System prompt for blog generation |
| `prompts/social.md` | System prompt for social post generation |
| `prompts/ad_copy.md` | System prompt for ad copy generation |
| `prompts/email.md` | System prompt for email generation |
| `prompts/video_script.md` | System prompt for video script generation |
| `prompts/infographic.md` | System prompt for infographic brief generation |
| `services/content_service.py` | Loads prompts, calls Claude, parses JSON response |
| `routers/content.py` | 6 POST endpoints delegating to content_service |
| `tests/conftest.py` | TestClient fixture, mock Claude response fixture |
| `tests/test_auth.py` | Auth middleware tests |
| `tests/test_content.py` | Content endpoint tests with mocked Claude |
| `Procfile` | Railway process declaration |
| `README.md` | Agency-facing API documentation |

---

## Task 1: Project Bootstrap

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `models/__init__.py`
- Create: `routers/__init__.py`
- Create: `services/__init__.py`
- Create: `prompts/` (directory)
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
fastapi==0.111.0
uvicorn[standard]==0.29.0
anthropic==0.28.0
pydantic-settings==2.2.1
httpx==0.27.0
pytest==8.0.0
pytest-asyncio==0.23.0
pytest-mock==3.14.0
```

- [ ] **Step 2: Create .env.example**

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
VALID_API_KEYS=mk_live_key1,mk_live_key2
MODEL=claude-sonnet-4-6
```

- [ ] **Step 3: Create pytest.ini**

```ini
[pytest]
asyncio_mode = auto
```

Without this, async tests using `@pytest.mark.asyncio` will not run correctly.

- [ ] **Step 4: Create package init files and directories**

Run:
```bash
mkdir -p models routers services prompts tests
touch models/__init__.py routers/__init__.py services/__init__.py tests/__init__.py
cp .env.example .env
```

- [ ] **Step 5: Install dependencies**

Run:
```bash
pip install -r requirements.txt
```

Expected: All packages install without errors.

- [ ] **Step 6: Commit**

```bash
git add requirements.txt .env.example pytest.ini models/ routers/ services/ prompts/ tests/
git commit -m "feat: project bootstrap — deps, structure, env template"
```

---

## Task 2: Config

**Files:**
- Create: `config.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_config.py`:
```python
import os
import pytest

def test_settings_loads_required_vars(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("VALID_API_KEYS", "mk_live_abc,mk_live_xyz")
    
    import importlib
    import config
    importlib.reload(config)
    
    assert config.settings.anthropic_api_key == "test-anthropic-key"

def test_get_api_keys_returns_set(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("VALID_API_KEYS", "mk_live_abc,mk_live_xyz")
    
    import importlib
    import config
    importlib.reload(config)
    
    keys = config.settings.get_api_keys()
    assert "mk_live_abc" in keys
    assert "mk_live_xyz" in keys
    assert len(keys) == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_config.py -v
```

Expected: `ModuleNotFoundError: No module named 'config'`

- [ ] **Step 3: Create config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    anthropic_api_key: str
    valid_api_keys: str
    model: str = "claude-sonnet-4-6"

    def get_api_keys(self) -> set[str]:
        return {k.strip() for k in self.valid_api_keys.split(",")}

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_config.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add config.py tests/test_config.py
git commit -m "feat: config — settings with API key parsing"
```

---

## Task 3: Pydantic Models

**Files:**
- Create: `models/content.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_models.py`:
```python
from models.content import ContentRequest, ContentResponse, ContentVariant


def test_content_request_defaults():
    req = ContentRequest(product="My SaaS", audience="startup founders")
    assert req.tone == "professional"
    assert req.goal == "general awareness"
    assert req.keywords == []
    assert req.variants == 1
    assert req.brand_voice is None
    assert req.word_count is None


def test_content_request_variants_clamped():
    from pydantic import ValidationError
    with pytest.raises(ValidationError):
        ContentRequest(product="p", audience="a", variants=10)


def test_content_response_shape():
    variant = ContentVariant(index=1, content={"title": "Hello"}, word_count=1)
    response = ContentResponse(
        type="blog",
        variants=[variant],
        model="claude-sonnet-4-6",
        usage={"input_tokens": 10, "output_tokens": 20}
    )
    assert response.type == "blog"
    assert len(response.variants) == 1
    assert response.variants[0].index == 1


import pytest
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_models.py -v
```

Expected: `ImportError: cannot import name 'ContentRequest'`

- [ ] **Step 3: Create models/content.py**

```python
from pydantic import BaseModel, Field


class ContentRequest(BaseModel):
    product: str
    audience: str
    tone: str = "professional"
    goal: str = "general awareness"
    keywords: list[str] = []
    variants: int = Field(default=1, ge=1, le=5)
    brand_voice: str | None = None
    word_count: int | None = None


class ContentVariant(BaseModel):
    index: int
    content: dict
    word_count: int


class ContentResponse(BaseModel):
    type: str
    variants: list[ContentVariant]
    model: str
    usage: dict
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_models.py -v
```

Expected: 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add models/content.py tests/test_models.py
git commit -m "feat: pydantic models — ContentRequest, ContentVariant, ContentResponse"
```

---

## Task 4: Auth Middleware + Health Endpoint

**Files:**
- Create: `main.py`
- Create: `tests/conftest.py`
- Create: `tests/test_auth.py`

- [ ] **Step 1: Create tests/conftest.py**

```python
import os
import pytest

os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
os.environ.setdefault("VALID_API_KEYS", "mk_test_valid123")
os.environ.setdefault("MODEL", "claude-sonnet-4-6")

from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=True)


@pytest.fixture
def valid_headers():
    return {"Authorization": "Bearer mk_test_valid123"}
```

- [ ] **Step 2: Write the failing test**

Create `tests/test_auth.py`:
```python
def test_health_check_requires_no_auth(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_missing_auth_header_returns_401(client):
    response = client.post("/content/blog", json={"product": "test", "audience": "test"})
    assert response.status_code == 401


def test_invalid_api_key_returns_401(client):
    response = client.post(
        "/content/blog",
        json={"product": "test", "audience": "test"},
        headers={"Authorization": "Bearer invalid_key_xyz"}
    )
    assert response.status_code == 401


def test_malformed_auth_header_returns_401(client):
    response = client.post(
        "/content/blog",
        json={"product": "test", "audience": "test"},
        headers={"Authorization": "mk_test_valid123"}
    )
    assert response.status_code == 401


def test_valid_api_key_passes_auth(client, valid_headers):
    # /docs is public — valid key should also work on protected routes
    # We test a real protected route later; here just confirm key is accepted
    # (will get 404 until router is registered — that's fine)
    response = client.post(
        "/content/blog",
        json={"product": "test", "audience": "test"},
        headers=valid_headers
    )
    assert response.status_code != 401
```

- [ ] **Step 3: Run test to verify it fails**

Run:
```bash
pytest tests/test_auth.py -v
```

Expected: `ImportError: cannot import name 'app' from 'main'`

- [ ] **Step 4: Create main.py**

```python
from fastapi import FastAPI, HTTPException, Request, status

from config import settings

app = FastAPI(
    title="Marketing API",
    description="AI-powered content generation for marketing agencies",
    version="1.0.0",
)

_PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.url.path in _PUBLIC_PATHS:
        return await call_next(request)

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    key = auth.removeprefix("Bearer ").strip()
    if key not in settings.get_api_keys():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await call_next(request)


@app.get("/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Run test to verify it passes**

Run:
```bash
pytest tests/test_auth.py -v
```

Expected: 5 tests PASS. (The `valid_api_key_passes_auth` test will get 404 — that's correct, router not yet registered.)

- [ ] **Step 6: Commit**

```bash
git add main.py tests/conftest.py tests/test_auth.py
git commit -m "feat: FastAPI app with API key auth middleware and health endpoint"
```

---

## Task 5: System Prompts

**Files:**
- Create: `prompts/blog.md`
- Create: `prompts/social.md`
- Create: `prompts/ad_copy.md`
- Create: `prompts/email.md`
- Create: `prompts/video_script.md`
- Create: `prompts/infographic.md`

- [ ] **Step 1: Create prompts/blog.md**

```markdown
You are an expert marketing copywriter specializing in long-form SEO content.

Generate a blog post based on the inputs. Return ONLY valid JSON — no markdown fences, no explanation, no preamble.

If variants > 1, return a JSON array with that many blog post objects.
If variants = 1, return a single JSON object (not an array).

Each object must follow this exact structure:
{
  "title": "compelling, SEO-optimized headline under 70 characters",
  "meta_description": "SEO meta description between 150-160 characters",
  "intro": "engaging opening paragraph (2-3 sentences) that hooks the reader",
  "sections": [
    {"heading": "section heading", "body": "2-3 paragraph section body"},
    {"heading": "section heading", "body": "2-3 paragraph section body"},
    {"heading": "section heading", "body": "2-3 paragraph section body"}
  ],
  "cta": "clear, specific call to action sentence"
}

Rules:
- Include 3-5 sections
- Write in the specified tone
- Incorporate provided keywords naturally — never force them
- Honor the target word count if specified (distribute across sections)
- Focus on the specified goal throughout
```

- [ ] **Step 2: Create prompts/social.md**

```markdown
You are a social media marketing expert who writes high-engagement posts.

Generate social media posts based on the inputs. Return ONLY valid JSON — no markdown fences, no explanation, no preamble.

If variants > 1, return a JSON array with that many social post objects.
If variants = 1, return a single JSON object (not an array).

Each object must follow this exact structure:
{
  "linkedin": "LinkedIn post (150-300 words, professional, can use line breaks for readability)",
  "twitter_x": "Twitter/X post (max 280 characters, punchy, no hashtags in body)",
  "instagram": "Instagram caption (100-200 words, engaging, emoji-friendly)",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3", "hashtag4", "hashtag5"]
}

Rules:
- Each platform has a distinct voice appropriate to that platform
- LinkedIn: thought leadership, professional insight
- Twitter/X: bold, punchy, conversation-starting
- Instagram: visual storytelling, community-focused
- Hashtags: mix of broad (2) and niche (3), no # symbol in the strings
- Write in the specified tone
- Drive toward the specified goal
```

- [ ] **Step 3: Create prompts/ad_copy.md**

```markdown
You are a direct-response advertising copywriter with expertise in Google Ads and Meta Ads.

Generate ad copy based on the inputs. Return ONLY valid JSON — no markdown fences, no explanation, no preamble.

If variants > 1, return a JSON array with that many ad copy objects.
If variants = 1, return a single JSON object (not an array).

Each object must follow this exact structure:
{
  "google": {
    "headline": "Google Ads headline (max 30 characters)",
    "description": "Google Ads description (max 90 characters)",
    "cta": "call to action button text (2-4 words, e.g. Start Free Trial)"
  },
  "meta": {
    "primary_text": "Meta Ads primary text (125 characters shown before 'see more', write for this limit)",
    "headline": "Meta Ads headline (max 40 characters, shown below image)",
    "cta": "call to action button text (2-4 words)"
  }
}

Rules:
- Google headline: must fit 30 chars — count carefully
- Google description: must fit 90 chars — count carefully
- Meta primary text: optimise for first 125 chars
- Use benefit-driven language, not feature-driven
- Write in the specified tone
- Every variant must use a different angle or hook
```

- [ ] **Step 4: Create prompts/email.md**

```markdown
You are an email marketing specialist who writes high-converting campaigns.

Generate an email campaign based on the inputs. Return ONLY valid JSON — no markdown fences, no explanation, no preamble.

If variants > 1, return a JSON array with that many email objects.
If variants = 1, return a single JSON object (not an array).

Each object must follow this exact structure:
{
  "subject_lines": [
    "Subject line option 1 (max 60 characters)",
    "Subject line option 2 (max 60 characters)",
    "Subject line option 3 (max 60 characters)"
  ],
  "preview_text": "Preview/preheader text shown after subject in inbox (max 90 characters)",
  "body": "Full email body in plain text. Use double newlines for paragraphs. Keep under 300 words.",
  "cta": "Call to action button text (3-6 words)"
}

Rules:
- Always provide exactly 3 subject line options per email object
- Subject lines: mix curiosity, benefit, and urgency angles
- Preview text must complement (not repeat) the subject line
- Body: clear problem → solution → proof → action structure
- Write in the specified tone
- Optimize for the specified goal
```

- [ ] **Step 5: Create prompts/video_script.md**

```markdown
You are a video content strategist and scriptwriter for marketing videos.

Generate a video script based on the inputs. Return ONLY valid JSON — no markdown fences, no explanation, no preamble.

If variants > 1, return a JSON array with that many video script objects.
If variants = 1, return a single JSON object (not an array).

Each object must follow this exact structure:
{
  "hook": "Opening 5-10 seconds of spoken script — must grab attention immediately",
  "body": "Main content spoken script — clear sections with [PAUSE] markers where appropriate",
  "cta": "Closing 5-10 seconds — specific action for viewer to take",
  "broll_notes": "Suggested B-roll footage or visuals to accompany each section, as a single descriptive paragraph",
  "duration_estimate": "Estimated video duration (e.g. '60-90 seconds' or '2-3 minutes')"
}

Rules:
- Hook must start with a question, bold statement, or surprising fact
- Body uses conversational language — write how people actually speak
- [PAUSE] marks natural breaks for editing
- B-roll notes reference actual visual footage ideas, not abstract concepts
- Duration estimate based on average speaking pace (~130 words/minute)
- Write in the specified tone
```

- [ ] **Step 6: Create prompts/infographic.md**

```markdown
You are a content strategist specializing in visual content and infographics for marketing.

Generate an infographic brief based on the inputs. Return ONLY valid JSON — no markdown fences, no explanation, no preamble.

If variants > 1, return a JSON array with that many infographic brief objects.
If variants = 1, return a single JSON object (not an array).

Each object must follow this exact structure:
{
  "headline": "Main infographic headline (max 10 words, bold and scannable)",
  "subheadline": "Supporting subheadline that adds context (max 20 words)",
  "sections": [
    {"title": "section label", "stat": "key number or fact", "description": "1-2 sentence explanation"},
    {"title": "section label", "stat": "key number or fact", "description": "1-2 sentence explanation"},
    {"title": "section label", "stat": "key number or fact", "description": "1-2 sentence explanation"},
    {"title": "section label", "stat": "key number or fact", "description": "1-2 sentence explanation"},
    {"title": "section label", "stat": "key number or fact", "description": "1-2 sentence explanation"}
  ],
  "cta": "Bottom call to action (max 10 words)"
}

Rules:
- Always include exactly 5 sections
- Stats should be specific and credible — use realistic figures relevant to the industry
- Each section title is short (2-4 words)
- Descriptions expand on the stat with context
- Write for scannability — infographics are read quickly
```

- [ ] **Step 7: Commit**

```bash
git add prompts/
git commit -m "feat: system prompts for all 6 content types"
```

---

## Task 6: Content Service

**Files:**
- Create: `services/content_service.py`
- Create: `tests/test_content_service.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_content_service.py`:
```python
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from models.content import ContentRequest


@pytest.fixture
def blog_request():
    return ContentRequest(
        product="SaaS project management tool",
        audience="startup founders",
        goal="drive free trial signups",
        variants=1
    )


@pytest.fixture
def mock_anthropic_message():
    msg = MagicMock()
    msg.content = [MagicMock(text='{"title":"Test Title","meta_description":"Test desc","intro":"Test intro","sections":[{"heading":"H1","body":"Body text"}],"cta":"Sign up"}')]
    msg.usage.input_tokens = 100
    msg.usage.output_tokens = 200
    return msg


@pytest.mark.asyncio
async def test_generate_content_returns_content_response(blog_request, mock_anthropic_message):
    with patch("services.content_service.client") as mock_client:
        mock_client.messages.create = AsyncMock(return_value=mock_anthropic_message)
        
        from services.content_service import generate_content
        result = await generate_content("blog", blog_request)
    
    assert result.type == "blog"
    assert len(result.variants) == 1
    assert result.variants[0].index == 1
    assert result.variants[0].content["title"] == "Test Title"
    assert result.usage["input_tokens"] == 100
    assert result.usage["output_tokens"] == 200


@pytest.mark.asyncio
async def test_generate_content_returns_multiple_variants(mock_anthropic_message):
    request = ContentRequest(product="App", audience="users", variants=2)
    mock_anthropic_message.content[0].text = '[{"title":"V1","meta_description":"d","intro":"i","sections":[{"heading":"h","body":"b"}],"cta":"c"},{"title":"V2","meta_description":"d","intro":"i","sections":[{"heading":"h","body":"b"}],"cta":"c"}]'
    
    with patch("services.content_service.client") as mock_client:
        mock_client.messages.create = AsyncMock(return_value=mock_anthropic_message)
        
        from services.content_service import generate_content
        result = await generate_content("blog", request)
    
    assert len(result.variants) == 2
    assert result.variants[0].index == 1
    assert result.variants[1].index == 2
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_content_service.py -v
```

Expected: `ImportError: cannot import name 'generate_content'`

- [ ] **Step 3: Create services/content_service.py**

```python
import json
from pathlib import Path

from anthropic import AsyncAnthropic

from config import settings
from models.content import ContentRequest, ContentResponse, ContentVariant

client = AsyncAnthropic(api_key=settings.anthropic_api_key)

_PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    return (_PROMPTS_DIR / f"{name}.md").read_text()


def _build_user_message(request: ContentRequest) -> str:
    lines = [
        f"Product: {request.product}",
        f"Audience: {request.audience}",
        f"Tone: {request.tone}",
        f"Goal: {request.goal}",
        f"Variants: {request.variants}",
    ]
    if request.keywords:
        lines.append(f"Keywords: {', '.join(request.keywords)}")
    if request.brand_voice:
        lines.append(f"Brand Voice: {request.brand_voice}")
    if request.word_count:
        lines.append(f"Target Word Count: {request.word_count}")
    lines.append("Return ONLY valid JSON. No markdown. No explanation.")
    return "\n".join(lines)


def _count_words(content: dict) -> int:
    return len(json.dumps(content).split())


async def generate_content(content_type: str, request: ContentRequest) -> ContentResponse:
    system_prompt = _load_prompt(content_type)
    user_message = _build_user_message(request)

    message = await client.messages.create(
        model=settings.model,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = message.content[0].text.strip()
    parsed = json.loads(raw)

    items = parsed if isinstance(parsed, list) else [parsed]

    variants = [
        ContentVariant(index=i + 1, content=item, word_count=_count_words(item))
        for i, item in enumerate(items[: request.variants])
    ]

    return ContentResponse(
        type=content_type,
        variants=variants,
        model=settings.model,
        usage={
            "input_tokens": message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        },
    )
```

- [ ] **Step 4: Run test to verify it passes**

Run:
```bash
pytest tests/test_content_service.py -v
```

Expected: 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add services/content_service.py tests/test_content_service.py
git commit -m "feat: content service — Claude async calls with prompt loading and JSON parsing"
```

---

## Task 7: Content Router

**Files:**
- Create: `routers/content.py`
- Create: `tests/test_content.py`

- [ ] **Step 1: Write the failing test**

Create `tests/test_content.py`:
```python
import pytest
from unittest.mock import AsyncMock, patch
from models.content import ContentResponse, ContentVariant


def _make_response(content_type: str):
    return ContentResponse(
        type=content_type,
        variants=[ContentVariant(index=1, content={"key": "value"}, word_count=5)],
        model="claude-sonnet-4-6",
        usage={"input_tokens": 10, "output_tokens": 50},
    )


ENDPOINTS = [
    ("blog", "/content/blog"),
    ("social", "/content/social"),
    ("ad_copy", "/content/ad-copy"),
    ("email", "/content/email"),
    ("video_script", "/content/video-script"),
    ("infographic", "/content/infographic"),
]

VALID_BODY = {"product": "SaaS tool", "audience": "startup founders"}


@pytest.mark.parametrize("content_type,path", ENDPOINTS)
def test_endpoint_returns_200_with_valid_request(client, valid_headers, content_type, path):
    with patch(
        "routers.content.generate_content",
        new=AsyncMock(return_value=_make_response(content_type)),
    ):
        response = client.post(path, json=VALID_BODY, headers=valid_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["type"] == content_type
    assert len(data["variants"]) == 1
    assert data["variants"][0]["index"] == 1


@pytest.mark.parametrize("content_type,path", ENDPOINTS)
def test_endpoint_returns_401_without_auth(client, content_type, path):
    response = client.post(path, json=VALID_BODY)
    assert response.status_code == 401


def test_endpoint_returns_422_when_product_missing(client, valid_headers):
    with patch("routers.content.generate_content", new=AsyncMock()):
        response = client.post(
            "/content/blog",
            json={"audience": "startup founders"},
            headers=valid_headers,
        )
    assert response.status_code == 422


def test_variants_capped_at_5(client, valid_headers):
    with patch(
        "routers.content.generate_content",
        new=AsyncMock(return_value=_make_response("blog")),
    ):
        response = client.post(
            "/content/blog",
            json={**VALID_BODY, "variants": 10},
            headers=valid_headers,
        )
    assert response.status_code == 422
```

- [ ] **Step 2: Run test to verify it fails**

Run:
```bash
pytest tests/test_content.py -v
```

Expected: Tests fail with 404 — router not yet registered.

- [ ] **Step 3: Create routers/content.py**

```python
from fastapi import APIRouter

from models.content import ContentRequest, ContentResponse
from services.content_service import generate_content

router = APIRouter(prefix="/content", tags=["Content"])


@router.post("/blog", response_model=ContentResponse)
async def blog(request: ContentRequest):
    return await generate_content("blog", request)


@router.post("/social", response_model=ContentResponse)
async def social(request: ContentRequest):
    return await generate_content("social", request)


@router.post("/ad-copy", response_model=ContentResponse)
async def ad_copy(request: ContentRequest):
    return await generate_content("ad_copy", request)


@router.post("/email", response_model=ContentResponse)
async def email(request: ContentRequest):
    return await generate_content("email", request)


@router.post("/video-script", response_model=ContentResponse)
async def video_script(request: ContentRequest):
    return await generate_content("video_script", request)


@router.post("/infographic", response_model=ContentResponse)
async def infographic(request: ContentRequest):
    return await generate_content("infographic", request)
```

- [ ] **Step 4: Run test to verify it fails (router not registered yet)**

Run:
```bash
pytest tests/test_content.py -v
```

Expected: Still 404 — router not registered in main.py yet.

- [ ] **Step 5: Commit router before wiring**

```bash
git add routers/content.py tests/test_content.py
git commit -m "feat: content router — 6 endpoints delegating to content_service"
```

---

## Task 8: Wire Router Into main.py

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Add router registration to main.py**

Open `main.py` and add these two lines at the bottom (after the health endpoint):

```python
from routers.content import router as content_router

app.include_router(content_router)
```

The full `main.py` should now look like:

```python
from fastapi import FastAPI, HTTPException, Request, status

from config import settings
from routers.content import router as content_router

app = FastAPI(
    title="Marketing API",
    description="AI-powered content generation for marketing agencies",
    version="1.0.0",
)

_PUBLIC_PATHS = {"/health", "/docs", "/openapi.json", "/redoc"}


@app.middleware("http")
async def verify_api_key(request: Request, call_next):
    if request.url.path in _PUBLIC_PATHS:
        return await call_next(request)

    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")

    key = auth.removeprefix("Bearer ").strip()
    if key not in settings.get_api_keys():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")

    return await call_next(request)


@app.get("/health")
async def health():
    return {"status": "ok"}


app.include_router(content_router)
```

- [ ] **Step 2: Run all tests**

Run:
```bash
pytest -v
```

Expected: All tests PASS. (test_auth.py, test_config.py, test_models.py, test_content_service.py, test_content.py)

- [ ] **Step 3: Smoke test locally**

Run the server:
```bash
uvicorn main:app --reload
```

In a second terminal, verify health and docs:
```bash
curl http://localhost:8000/health
# Expected: {"status":"ok"}

curl http://localhost:8000/docs
# Expected: HTML page (FastAPI Swagger UI)
```

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: wire content router into app — all endpoints live"
```

---

## Task 9: Deployment Files

**Files:**
- Create: `Procfile`
- Create: `README.md`

- [ ] **Step 1: Create Procfile**

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

- [ ] **Step 2: Create README.md**

```markdown
# Marketing API

AI-powered content generation API for marketing agencies. Built on Claude (Anthropic).

## Authentication

All endpoints require an API key:

```
Authorization: Bearer YOUR_API_KEY
```

## Base URL

```
https://your-railway-url.up.railway.app
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (no auth required) |
| GET | `/docs` | Interactive API docs (no auth required) |
| POST | `/content/blog` | Generate blog post |
| POST | `/content/social` | Generate social media posts |
| POST | `/content/ad-copy` | Generate ad copy |
| POST | `/content/email` | Generate email campaign |
| POST | `/content/video-script` | Generate video script |
| POST | `/content/infographic` | Generate infographic brief |

## Request Body (all endpoints)

```json
{
  "product": "Your product name or description",
  "audience": "Target audience description",
  "tone": "professional",
  "goal": "What action you want the audience to take",
  "keywords": ["keyword1", "keyword2"],
  "variants": 1,
  "brand_voice": "Optional brand guidelines",
  "word_count": 800
}
```

| Field | Required | Default | Notes |
|-------|----------|---------|-------|
| `product` | Yes | — | What you are marketing |
| `audience` | Yes | — | Who you are targeting |
| `tone` | No | `professional` | professional / casual / bold / friendly |
| `goal` | No | `general awareness` | Desired user action |
| `keywords` | No | `[]` | SEO or focus keywords |
| `variants` | No | `1` | 1–5 versions returned |
| `brand_voice` | No | `null` | Brand guidelines or persona |
| `word_count` | No | `null` | Target length |

## Response Body

```json
{
  "type": "blog",
  "variants": [
    {
      "index": 1,
      "content": {},
      "word_count": 847
    }
  ],
  "model": "claude-sonnet-4-6",
  "usage": {
    "input_tokens": 312,
    "output_tokens": 1204
  }
}
```

## Quick Start Example

```bash
curl -X POST https://your-url.up.railway.app/content/blog \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "product": "Project management SaaS",
    "audience": "startup founders",
    "goal": "drive free trial signups",
    "variants": 2
  }'
```

## Local Development

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY and VALID_API_KEYS
uvicorn main:app --reload
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | Yes | From console.anthropic.com |
| `VALID_API_KEYS` | Yes | Comma-separated API keys for your agency clients |
| `MODEL` | No | Defaults to `claude-sonnet-4-6` |

## Deploy to Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Select this repo
4. Add environment variables: `ANTHROPIC_API_KEY`, `VALID_API_KEYS`
5. Railway auto-deploys. Your API is live.
```

- [ ] **Step 3: Run full test suite one final time**

Run:
```bash
pytest -v
```

Expected: All tests PASS.

- [ ] **Step 4: Commit and push**

```bash
git add Procfile README.md
git commit -m "feat: Railway deployment config and agency-facing README"
git push origin main
```

---

## Task 10: Deploy to Railway

- [ ] **Step 1: Go to railway.app and sign up / log in**

- [ ] **Step 2: Create new project from GitHub**

- New Project → Deploy from GitHub repo → Select `Joshuavdp24/marketing-api-`

- [ ] **Step 3: Add environment variables in Railway dashboard**

Add these two variables:
```
ANTHROPIC_API_KEY = your_real_anthropic_api_key
VALID_API_KEYS = mk_live_agency1
```

- [ ] **Step 4: Wait for deploy (2-3 minutes), then verify**

```bash
curl https://YOUR-RAILWAY-URL.up.railway.app/health
# Expected: {"status":"ok"}
```

- [ ] **Step 5: Test a live endpoint**

```bash
curl -X POST https://YOUR-RAILWAY-URL.up.railway.app/content/blog \
  -H "Authorization: Bearer mk_live_agency1" \
  -H "Content-Type: application/json" \
  -d '{
    "product": "My SaaS product",
    "audience": "small business owners",
    "goal": "book a demo",
    "variants": 1
  }'
```

Expected: JSON response with `type: "blog"` and `variants` array containing a full blog post.

- [ ] **Step 6: Share `/docs` URL with agencies**

```
https://YOUR-RAILWAY-URL.up.railway.app/docs
```

This is your live interactive demo — agencies can test every endpoint in the browser.
