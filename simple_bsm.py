import json
import os
import requests

API_KEY = os.getenv("OPENROUTER_API_KEY", "your-openrouter-key")
MODEL = "meta-llama/llama-3.1-70b-instruct"


def call_llm(prompt: str) -> str:
    res = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
        },
    )
    return res.json()["choices"][0]["message"]["content"].strip()


# Branch generates both criterion name and custom evaluation rubric
def branch_impact_rubric(ticker: str, article: str) -> list[dict]:
    prompt = f"""
You are a financial analyst.
Ticker: {ticker}
News: {article}

Propose an evaluation plan of up to 4 distinct criteria/dimensions to assess the stock price impact.
For each criterion, provide:
1. "name": The short dimension title (e.g. "Revenue Risk", "Public Relations")
2. "rubric": A concrete description specifying what factors to examine for this article.

Return ONLY a valid JSON list of objects in this format:
[
  {{"name": "Dimension Name", "rubric": "Evaluate whether..."}}
]
"""
    raw = call_llm(prompt)
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)


# Solve conditions on both the criterion name AND the rubric instruction
def solve_criterion(ticker: str, article: str, criterion: dict) -> dict:
    prompt = f"""
Ticker: {ticker}
News: {article}

[Evaluation Dimension]
Name: {criterion["name"]}
Rubric / Instructions: {criterion["rubric"]}
[End of Evaluation Dimension]

Evaluate the stock impact SOLELY according to the rubric above.
Assign an impact score on a scale from -5 to +5:
 -5 = Catastrophic negative impact for the future
  0 = Neutral / negligible / already priced in / currently has no effect
 +5 = Transformative positive impact for the future

Provide an integer score and a brief rationale.
Return ONLY valid JSON in this exact format:
{{"score": -3, "rationale": "Short explanation..."}}
"""
    raw = call_llm(prompt)
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    return json.loads(cleaned)


# Merge aggregates scores across all rubric branches
def analyze_stock_news_impact(ticker: str, article: str) -> dict:
    criteria_rubric = branch_impact_rubric(ticker, article)

    breakdown = []
    total_score = 0

    for crit in criteria_rubric:
        eval_result = solve_criterion(ticker, article, crit)
        score = int(eval_result["score"])
        total_score += score

        breakdown.append(
            {
                "dimension": crit["name"],
                "rubric": crit["rubric"],
                "score": score,
                "rationale": eval_result["rationale"],
            }
        )

    avg_score = round(total_score / len(breakdown), 2) if breakdown else 0.0

    if avg_score >= 1.5:
        sentiment = "Bullish"
    elif avg_score <= -1.5:
        sentiment = "Bearish"
    else:
        sentiment = "Neutral"

    return {
        "ticker": ticker,
        "sentiment": sentiment,
        "average_impact_score": avg_score,
        "rubric_evaluations": breakdown,
    }


if __name__ == "__main__":
    ticker_symbol = "NVDA"
    news_text = (
        "The U.S. government announced sudden, expanded export restrictions "
        "barring sales of advanced accelerator chip architectures to several foreign markets. "
        "The company noted these regions contributed approximately 15% of data center segment revenue."
    )

    result = analyze_stock_news_impact(ticker_symbol, news_text)
    print(json.dumps(result, indent=2))
