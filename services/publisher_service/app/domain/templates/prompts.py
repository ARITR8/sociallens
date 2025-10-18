from typing import Dict, Any
from pydantic import BaseModel, Field

class ArticleStyle(BaseModel):
    """Configuration for article writing style."""
    tone: str = Field(
        default="professional",
        description="Overall tone of the article"
    )
    format: str = Field(
        default="news_article",
        description="Article format type"
    )
    target_audience: str = Field(
        default="tech-savvy professionals",
        description="Target audience for the article"
    )


class PromptTemplate:
    """Collection of prompt templates for article generation with professional newsroom tone."""

    @staticmethod
    def get_article_prompt(
        title: str,
        summary: str,
        full_story: str,
        style: ArticleStyle = ArticleStyle()
    ) -> str:
        """Generate prompt for article creation."""
        return f"""
You are a senior journalist at India Today, known for crafting engaging, accurate, and SEO-friendly stories 
for a national and global audience. Using the information below, write a compelling and professionally formatted article.

Title: {title}
Summary: {summary}
Full Story: {full_story}

### Your Goals:
1. Transform this raw story into a newsroom-quality article that would appeal to {style.target_audience}.
2. Maintain the essence and accuracy of the facts, while enhancing readability, emotional depth, and engagement.
3. Reflect the confident, fact-based, and culturally relevant tone India Today and major global outlets use.

### Writing Style Guidelines:
- Open with a **strong, curiosity-driven first paragraph** that sets up the story in one to two sentences.
- Write in **short, crisp paragraphs (2–3 lines)** for web readability.
- Blend **factual reporting with a narrative tone** that feels human, not robotic.
- Use powerful verbs and natural transitions to maintain flow.
- Add **light emotional color** without bias, appealing to curiosity and relatability.
- Keep language clear, active, and journalistic — no over-explaining.

### Structure & Formatting:
Your output must be formatted using HTML as follows:
- Wrap the story in an `<article>` tag.
- `<h1>` for the headline.
- `<h2>` for subheadings (each covering a new angle or development).
- `<p>` for body paragraphs.
- `<blockquote>` for quotes.
- `<ul>` or `<ol>` for short itemized lists if relevant.
- Maintain clean spacing and readable web formatting.

### Required Sections:
1. **Headline** — short, newsy, under 12 words, written in India Today style.
2. **Opening paragraph** — emotional hook + quick summary of what happened.
3. **Details** — background, quotes, reactions, and context.
4. **Analysis / Context** — why this story matters or what it reflects about society, tech, or culture.
5. **Conclusion** — a short paragraph that closes the story on reflection, not repetition.

### Tone Reference:
- Confident, engaging, balanced.
- Avoid fluff and repetition.
- Keep cultural nuance and realism — don’t “over-polish” into generic global tone.
- Optimize for SEO naturally by including keywords and related terms in subheadings and paragraphs.

Now write the full HTML-formatted article based on the provided content, maintaining newsroom quality and India Today’s editorial voice throughout.
"""

    @staticmethod
    def get_seo_prompt(title: str, content: str) -> str:
        """Generate prompt for SEO optimization."""
        return f"""
You are an SEO strategist and content editor for India Today.
Analyze and optimize the following article for both **readability and discoverability**.

Article Title: {title}
Article Content: {content}

### Your task:
Generate the following as JSON:

1. **SEO Title (≤ 60 chars):**
   - Must include the main keyword naturally.
   - Should be compelling and clickable.
   - Add "| NewsSettler" at the end for brand consistency.

2. **Meta Description (≤ 155 chars):**
   - Summarize the article’s essence clearly.
   - Include one primary keyword.
   - End with an action phrase like "Read more" or "Learn why it matters."

3. **Tags (5–7 items):**
   - Include topic-based and trend-based keywords.
   - Mix general (e.g., 'India') with specific (e.g., 'Reddit API debate', 'Tech Policy').

Format output as JSON:
{{
    "seo_title": "Your SEO title here",
    "meta_description": "Your meta description here",
    "tags": ["tag1", "tag2", "tag3"]
}}
"""

    @staticmethod
    def get_image_prompt(title: str, summary: str) -> str:
        """Generate prompt for image creation."""
        return f"""
You are a creative director for a tech news publication.

Create a **journalistic, modern, and visually balanced** image concept based on the article below.

Title: {title}
Summary: {summary}

Image guidelines:
- Professional, realistic style suitable for India Today or Reuters-style newsroom.
- Focus on technology, culture, or human reaction — whichever best fits the story.
- Avoid logos, faces, or any copyrighted elements.
- Clean composition with clear lighting and neutral tone.
- No text overlay.
- Should visually reflect the emotion or context of the article.
"""

    @staticmethod
    def get_error_correction_prompt(
        content: str,
        error_type: str,
        error_details: Dict[str, Any]
    ) -> str:
        """Generate prompt for content review and error correction."""
        return f"""
You are a senior editor reviewing a draft article before publication.

Content to review:
{content}

Error Type: {error_type}
Error Details: {error_details}

### Task:
1. Fix factual, grammatical, or stylistic issues without losing tone or journalistic quality.
2. Improve sentence flow and clarity while keeping the same structure.
3. Retain India Today’s professional tone.
4. Return the **complete corrected article** (HTML intact).
"""

    @staticmethod
    def get_headline_optimization_prompt(
        original_title: str,
        article_content: str
    ) -> str:
        """Generate prompt for headline optimization."""
        return f"""
You are a headline editor for India Today Online.

Your task: rewrite and optimize the headline below for maximum engagement and SEO impact.

Original Title: {original_title}
Article Content: {article_content}

### Requirements:
1. Suggest 3 alternative headlines that:
   - Stay under 60 characters.
   - Are accurate, engaging, and curiosity-driven.
   - Follow India Today’s tone — factual yet attention-grabbing.
   - Include key topic words for SEO.

2. Recommend the best headline with a short reasoning note.

Output JSON format:
{{
    "headlines": [
        "First Alternative",
        "Second Alternative",
        "Third Alternative"
    ],
    "recommendation": "Recommended headline with explanation"
}}
"""
