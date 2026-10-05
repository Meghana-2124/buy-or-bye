import os
import requests
import streamlit as st
from dotenv import load_dotenv
import serpapi

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Buy or Bye",
    page_icon="🛍️",
    layout="centered"
)

st.title("🛍️ Buy or Bye")
st.subheader("Your Personal Purchase Reality Check")
st.write("Before you buy it, find out whether it actually makes sense for you.")

st.divider()

# -----------------------------
# User Inputs
# -----------------------------

product_name = st.text_input(
    "What are you thinking of buying?",
    value="",
    placeholder="e.g. headphones, laptop, shoes"
)

price = st.number_input(
    "Product price (₹)",
    min_value=0.0,
    value=5000.0,
    step=500.0
)

budget = st.number_input(
    "What is your comfortable spending budget? (₹)",
    min_value=0.0,
    value=10000.0,
    step=500.0
)

uses_per_month = st.number_input(
    "Expected uses per month",
    min_value=0,
    value=15,
    step=1
)

need_score = st.slider(
    "How much do you need this product? (1 = Not needed, 5 = Very needed)",
    min_value=1,
    max_value=5,
    value=4
)

similar_product = st.radio(
    "Do you already own something similar?",
    ["No", "Yes"],
    horizontal=True
)

impulse_score = st.slider(
    "How impulsive does this purchase feel? (1 = Not impulsive, 5 = Very impulsive)",
    min_value=1,
    max_value=5,
    value=2
)

cheaper_alternative = st.radio(
    "Is there a cheaper alternative that meets your needs?",
    ["No", "Yes"],
    horizontal=True
)


# -----------------------------
# SerpApi: Current Web Information
# -----------------------------

def search_product(product):

    if not SERPAPI_KEY:
        return []

    try:

        client = serpapi.Client(
            api_key=SERPAPI_KEY
        )

        results = client.search({
            "engine": "google",
            "q": f"{product} price India reviews alternatives",
            "gl": "in",
            "hl": "en"
        })

        organic_results = results.get(
            "organic_results",
            []
        )

        search_results = []

        for result in organic_results[:5]:

            search_results.append({
                "title": result.get("title", ""),
                "snippet": result.get("snippet", ""),
                "link": result.get("link", "")
            })

        return search_results

    except Exception:
        return []


# -----------------------------
# Python Purchase Decision Engine
# -----------------------------

def calculate_purchase_signals(
    price,
    budget,
    uses_per_month,
    need_score,
    similar_product,
    impulse_score,
    cheaper_alternative
):

    signals = []

    # Budget signal
    if price <= budget:
        signals.append("within_budget")
    else:
        signals.append("over_budget")

    # Need signal
    if need_score >= 4:
        signals.append("strong_need")

    elif need_score == 3:
        signals.append("moderate_need")

    else:
        signals.append("low_need")

    # Usage signal
    if uses_per_month >= 12:
        signals.append("frequent_use")

    elif uses_per_month >= 5:
        signals.append("moderate_use")

    else:
        signals.append("low_use")

    # Similar product signal
    if similar_product == "Yes":
        signals.append("similar_product_owned")

    else:
        signals.append("no_similar_product")

    # Impulse signal
    if impulse_score >= 4:
        signals.append("high_impulse")

    elif impulse_score == 3:
        signals.append("moderate_impulse")

    else:
        signals.append("low_impulse")

    # Cheaper alternative signal
    if cheaper_alternative == "Yes":
        signals.append("cheaper_alternative_exists")

    else:
        signals.append("no_cheaper_alternative")

    # -------------------------
    # Final verdict
    # -------------------------

    if price > budget:

        verdict = "BYE"

    elif need_score <= 2 and impulse_score >= 4:

        verdict = "BYE"

    elif similar_product == "Yes" and need_score <= 3:

        verdict = "BYE"

    elif cheaper_alternative == "Yes":

        verdict = "WAIT"

    elif impulse_score >= 4:

        verdict = "WAIT"

    elif need_score == 3:

        verdict = "WAIT"

    elif uses_per_month < 5:

        verdict = "WAIT"

    else:

        verdict = "BUY"

    return verdict, signals


# -----------------------------
# Gemma Explanation
# -----------------------------

def ask_gemma(prompt):

    try:

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "gemma3:1b",
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        return response.json().get(
            "response",
            ""
        ).strip()

    except Exception as e:

        return f"Gemma could not generate an explanation: {e}"


# -----------------------------
# Buy or Bye Button
# -----------------------------

if st.button(
    "🔎 Check My Purchase",
    use_container_width=True
):

    if not product_name.strip():

        st.warning(
            "Please enter a product name."
        )

        st.stop()

    # -------------------------
    # Calculate decision
    # -------------------------

    verdict, signals = calculate_purchase_signals(
        price,
        budget,
        uses_per_month,
        need_score,
        similar_product,
        impulse_score,
        cheaper_alternative
    )

    # -------------------------
    # Current Web Information
    # -------------------------

    st.divider()

    st.header("🔎 Current Web Information")

    search_results = search_product(
        product_name
    )

    if search_results:

        for result in search_results:

            st.markdown(
                f"**{result['title']}**"
            )

            if result["snippet"]:

                st.write(
                    result["snippet"]
                )

            if result["link"]:

                st.markdown(
                    f"[View source]({result['link']})"
                )

            st.write("")

    else:

        st.info(
            "No current web information was found."
        )

    # -------------------------
    # Purchase Reality Check
    # -------------------------

    st.divider()

    st.header("📊 Purchase Reality Check")

    st.write(
        f"**Product:** {product_name}"
    )

    st.write(
        f"**Price:** ₹{price:,.0f}"
    )

    st.write(
        f"**Your budget:** ₹{budget:,.0f}"
    )

    st.write(
        f"**Expected usage:** {uses_per_month} times/month"
    )

    st.write(
        f"**Need score:** {need_score}/5"
    )

    st.write(
        f"**Already own something similar:** "
        f"{similar_product}"
    )

    st.write(
        f"**Impulse score:** {impulse_score}/5"
    )

    st.write(
        f"**Cheaper alternative:** "
        f"{cheaper_alternative}"
    )

    # -------------------------
    # Verdict
    # -------------------------

    st.divider()

    if verdict == "BUY":

        st.success("🟢 BUY")

    elif verdict == "WAIT":

        st.warning("🟡 WAIT")

    else:

        st.error("🔴 BYE")

    # -------------------------
    # Gemma Prompt
    # -------------------------

    gemma_prompt = f"""
You are the explanation layer of "Buy or Bye", an AI purchase reality-check app.

The Python decision engine has already calculated the final verdict.

You MUST use this exact verdict:

VERDICT: {verdict}

PURCHASE FACTS:

Product: {product_name}
Price: ₹{price:,.0f}
User budget: ₹{budget:,.0f}
Expected uses per month: {uses_per_month}
Need score: {need_score}/5
Already owns something similar: {similar_product}
Impulse score: {impulse_score}/5
Cheaper alternative available: {cheaper_alternative}

CALCULATED SIGNALS:

{", ".join(signals)}

Your job is ONLY to explain why the predetermined verdict makes sense.

STRICT RULES:

- Do not change the verdict.
- Use only the purchase facts and calculated signals above.
- Do not use web information.
- Do not mention search results.
- Do not invent product models.
- Do not invent product features.
- Do not invent product specifications.
- Do not invent product quality.
- Do not invent prices.
- Do not infer why the user needs the product.
- Do not infer the user's income.
- Do not infer the user's savings.
- Do not infer the user's lifestyle.
- Do not infer information that the user did not provide.
- Treat every purchase fact exactly as provided.
- If price is less than or equal to budget, explicitly recognize that it is within budget.
- Mention expected monthly usage when it supports the decision.
- Mention the need score when it supports the decision.
- Mention the impulse score when it supports the decision.
- Mention whether the user already owns something similar when relevant.
- Mention the cheaper alternative only according to the provided Yes/No answer.
- Never say that a cheaper alternative exists when the answer is No.
- Never say that the user owns a similar product when the answer is No.
- If the cheaper alternative answer is Yes, you may mention that a cheaper alternative exists.
- Never calculate price multiplied by usage.
- Monthly usage means frequency of use, not monthly spending.
- Do not use vague phrases such as "worthwhile fit" without explaining the actual factors.
- Keep the explanation specific to this purchase.
- Write exactly 2 sentences.
- Start directly with "The purchase" or "This purchase".
- Do not use "REASON:" in your response.
- Do not add bullet points.
- Do not add headings.

Your explanation should clearly connect the strongest factors to the predetermined verdict.
"""

    # -------------------------
    # Gemma Explanation
    # -------------------------

    with st.spinner(
        "🤖 Gemma is analyzing your purchase..."
    ):

        gemma_reason = ask_gemma(
            gemma_prompt
        )

    st.subheader(
        "🤖 Gemma's Verdict"
    )

    st.write(
        gemma_reason
    )

    # -------------------------
    # How Buy or Bye Decided
    # -------------------------

    with st.expander(
        "💡 How Buy or Bye decided"
    ):

        st.write(
            "The final BUY / WAIT / BYE decision is "
            "calculated from your purchase inputs "
            "using a deterministic decision engine."
        )

        st.write(
            "Gemma then explains that decision using "
            "only those inputs. Current web information "
            "from SerpApi is shown separately and is "
            "not allowed to override your personal "
            "purchase facts."
        )

        st.write(
            "**Signals detected:**"
        )

        for signal in signals:

            st.write(
                f"• {signal.replace('_', ' ').title()}"
            )


# -----------------------------
# Footer
# -----------------------------

st.divider()

st.caption(
    "Buy or Bye uses Python decision logic, "
    "Gemma 3:1b via Ollama, and SerpApi "
    "for current web information."
)