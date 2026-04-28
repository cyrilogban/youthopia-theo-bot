# AGENTS.md

## Project Overview

This project is a Bible bot that delivers:

- Verse of the Day (VOTD)
- AI-generated reflections
- Scripture on-demand based on user-requested categories

The system is config-driven:

- VOTD is controlled via JSON configuration
- Users can request scriptures by category (e.g., "hope", "peace")

The goal is to ensure outputs feel:

- Intentional
- Spiritually grounded
- Human (not generic AI-generated)

---

## Core Categories (STRICT)

The system MUST use ONLY:

- faith
- love
- peace
- joy
- hope
- patience
- forgiveness

No additional categories allowed unless updated in config.

---

## Embedded Data Configuration (SOURCE OF TRUTH)

The system MUST use the following configuration:

```json
{
  "votd": {
    "mode": "category",
    "category": "peace"
  },

  "categories": {
    "faith": [
      { "book": "Hebrews", "chapter": 11, "verse": 1 },
      { "book": "2 Corinthians", "chapter": 5, "verse": 7 },
      { "book": "Mark", "chapter": 11, "verse": 11 }
    ],
    "love": [
      { "book": "1 Corinthians", "chapter": 13, "verse": 4 },
      { "book": "John", "chapter": 3, "verse": 16 },
      { "book": "Romans", "chapter": 5, "verse": 8 }
    ],
    "peace": [
      { "book": "John", "chapter": 14, "verse": 27 },
      { "book": "Philippians", "chapter": 4, "verse": 6 },
      { "book": "Isaiah", "chapter": 26, "verse": 3 }
    ],
    "joy": [
      { "book": "Nehemiah", "chapter": 8, "verse": 10 },
      { "book": "Psalm", "chapter": 16, "verse": 11 },
      { "book": "Romans", "chapter": 15, "verse": 13 }
    ],
    "hope": [
      { "book": "Jeremiah", "chapter": 29, "verse": 11 },
      { "book": "Romans", "chapter": 15, "verse": 4 },
      { "book": "Psalm", "chapter": 42, "verse": 11 }
    ],
    "patience": [
      { "book": "James", "chapter": 1, "verse": 3 },
      { "book": "Galatians", "chapter": 6, "verse": 9 },
      { "book": "Romans", "chapter": 12, "verse": 12 }
    ],
    "forgiveness": [
      { "book": "Ephesians", "chapter": 4, "verse": 32 },
      { "book": "Colossians", "chapter": 3, "verse": 13 },
      { "book": "Matthew", "chapter": 6, "verse": 14 }
    ]
  }
}
```

---

## Data Rules

- NEVER store full verse text
- ALWAYS use:
  - book
  - chapter
  - verse
- NEVER use string refs like "John 3:16"
- Category names MUST be lowercase
- This configuration is the SINGLE SOURCE OF TRUTH

---

## Verse of the Day (VOTD)

### Definition

- VOTD is determined from config
- Uses: `votd.category`
- Same for all users per day

---

## VOTD Logic Flow

1. Read `votd.category`
2. Access `categories[votd.category]`
3. Select one verse
4. Fetch verse text via API
5. Cache for the day
6. Generate reflection
7. Return structured output

---

## User Request Flow (Category-Based)

Example: "I need hope scripture"

Flow:

1. Normalize input
2. Detect category keyword
3. Match to categories
4. Select verse
5. Fetch verse text
6. Generate reflection
7. Return response

---

## Category Detection Rules

- Match only: faith, love, peace, joy, hope, patience, forgiveness
- Input must be lowercase
- If no match → return fallback response

---

## Bible Verse Retrieval

### API

Use FYIM Bible API (or equivalent)

---

### Format

Book Chapter:Verse

Example: Hebrews 11:1

---

### Rules

- NEVER hardcode verse text
- NEVER fabricate scripture
- ALWAYS fetch from API
- Retry on failure
- Fallback if necessary

---

## Verse Selection Strategy

- Random OR rotational selection
- Must stay within category
- Avoid repetition

---

## Caching Rules (VOTD)

- Cache per day
- Same verse for all users
- Prevent reselection

---

## Reflection Generation (AI API)

### Purpose

Generate:

- Reflection
- Prompt

---

### Rules

- MUST use AI API
- NEVER hardcode reflections
- NEVER output generic text

---

### Tone Requirements

Reflections MUST be:

- Human
- Spiritually grounded
- Emotionally aware
- Concise (2–4 sentences)
- Practical

---

### Anti-Generic Rules

The AI MUST NOT:

- Be robotic
- Use clichés repeatedly
- Be vague
- Repeat structure

---

### Style Guidance

Reflections should feel like:

- A real human writer
- Direct and calm
- Insightful, not preachy

---

## Output Format (STRICT)

📖 Book Chapter:Verse

"Verse text from API"

💭 Reflection:
[AI-generated reflection]

🧠 Prompt:
[Short actionable question]

---

## Abbreviation Rules

- ALWAYS use full book names

Correct: Romans 8:28
Incorrect: Rom 8:28

---

## Architecture Rules

### Separation of Concerns

- Handlers → user interaction
- Services → logic
- Data → config
- API → external calls

---

### Services

1. VOTD Service
2. Verse Service
3. Reflection Service
4. Category Detection Service

---

## Error Handling

- Retry API failures
- Fallback to another verse
- Handle missing category gracefully
- NEVER crash

---

## Strict Prohibitions

- Do NOT hardcode Bible text
- Do NOT fabricate scripture
- Do NOT bypass config
- Do NOT mix responsibilities
- Do NOT return unstructured output

---

## Expected Output Quality

All outputs must:

- Be structured
- Be meaningful
- Match category
- Be consistent
- Feel intentional

---

## Guiding Principle

Deliver the right scripture based on configured intent (VOTD) or user need (category request), supported by meaningful, human-like reflection.
