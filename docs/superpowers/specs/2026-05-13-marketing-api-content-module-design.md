# Marketing API — Content & Creative Production Module (v1)

**Date:** 2026-05-13  
**Status:** Approved  
**Scope:** Module 1 of 8 in the Marketing Agency AI Platform

---

## Overview

A standalone REST API that generates marketing content for any product or audience. Designed to be sold to agencies as an integration layer — agencies call the API from their own tools and bill their clients for the output.

---

## Architecture

**Tech stack:** Python 3.11+, FastAPI, Anthropic SDK (Claude Sonnet 4.6)  
**Pattern:** Stateless — no database. Every request is self-contained.  
**Auth:** API key via `Authorization: Bearer <key>` header  
**Deployment:** Railway (GitHub push-to-deploy)

```
marketing-api/
  main.py                  # FastAPI app + auth middleware
  config.py                # Env vars and settings
  routers/
    content.py             # All content generation routes
  services/
    content_service.py     # Claude calls + prompt assembly
  models/
    content.py             # Pydantic request/response schemas
  prompts/
    blog.md                # System prompt: blog posts
    social.md              # System prompt: social media
    ad_copy.md             # System prompt: ad copy
    email.md               # System prompt: email campaigns
    video_script.md        # System prompt: video scripts
    infographic.md         # System prompt: infographic briefs
  requirements.txt
  .env.example
  README.md
```

---

## API Endpoints

| Method | Path | Output |
|--------|------|--------|
| POST | `/content/blog` | Long-form blog post (title, intro, body, CTA) |
| POST | `/content/social` | Posts for LinkedIn, Twitter/X, Instagram |
| POST | `/content/ad-copy` | Ad variants for Google Ads + Meta Ads |
| POST | `/content/email` | Email campaign (subject lines + body) |
| POST | `/content/video-script` | Video script (hook, body, CTA, b-roll notes) |
| POST | `/content/infographic` | Infographic brief (headline, stats, sections) |
| GET | `/health` | Health check |

---

## Request Schema

All endpoints share the same base request body:

```json
{
  "product": "SaaS project management tool",
  "audience": "startup founders",
  "tone": "professional",
  "goal": "drive free trial signups",
  "keywords": ["productivity", "team collaboration"],
  "variants": 3,
  "brand_voice": "Optional brand guidelines or persona description",
  "word_count": 800
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `product` | string | Yes | What is being marketed |
| `audience` | string | Yes | Target audience description |
| `tone` | string | No | professional / casual / bold / friendly (default: professional) |
| `goal` | string | No | Desired user action (default: general awareness) |
| `keywords` | string[] | No | SEO or focus keywords |
| `variants` | int | No | Number of versions to generate, 1–5 (default: 1) |
| `brand_voice` | string | No | Brand guidelines or voice description |
| `word_count` | int | No | Target word count for applicable content types |

---

## Response Schema

All endpoints return the same envelope:

```json
{
  "type": "blog",
  "variants": [
    {
      "index": 1,
      "content": {},
      "word_count": 847,
      "confidence": 0.91
    }
  ],
  "model": "claude-sonnet-4-6",
  "usage": {
    "input_tokens": 312,
    "output_tokens": 1204
  }
}
```

### Content shapes per type

**blog:** `{ title, meta_description, intro, sections: [{heading, body}], cta }`  
**social:** `{ linkedin, twitter_x, instagram, hashtags }`  
**ad_copy:** `{ google: {headline, description, cta}, meta: {primary_text, headline, cta} }`  
**email:** `{ subject_lines: [string], preview_text, body, cta }`  
**video_script:** `{ hook, body, cta, broll_notes, duration_estimate }`  
**infographic:** `{ headline, subheadline, sections: [{title, stat, description}], cta }`

---

## Auth

API keys are stored in `.env` as a comma-separated list:

```
VALID_API_KEYS=mk_live_abc123,mk_live_xyz456
```

Every request must include:
```
Authorization: Bearer mk_live_abc123
```

Invalid or missing keys return `401 Unauthorized`. Keys are added/revoked manually for v1.

---

## Deployment

1. Push to GitHub (`Joshuavdp24/marketing-api-`)
2. Connect repo to Railway
3. Set environment variables in Railway dashboard:
   - `ANTHROPIC_API_KEY`
   - `VALID_API_KEYS`
4. Railway auto-deploys on every push to `main`

FastAPI auto-generates interactive API docs at `/docs` — use this as the agency sales demo.

---

## Out of Scope for v1

- Database / persistence
- Usage metering / billing per agency
- Webhook callbacks for async generation
- Rate limiting (add in v2)
- Modules 2–8 (Brand Management, Market Research, etc.)

---

## Success Criteria

- All 6 content endpoints return structured JSON in under 15 seconds
- API key auth rejects invalid keys with 401
- `/docs` renders correctly for agency demos
- Deployed and accessible via public Railway URL
