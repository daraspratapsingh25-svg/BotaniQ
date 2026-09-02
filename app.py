
import json
from datetime import date, timedelta
from urllib.parse import quote
import streamlit as st
import google.generativeai as genai
from PIL import Image

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="BotaniQ",
    page_icon="🌿",
    layout="wide"
)

# ============================================================
# GEMINI CONFIGURATION
# ============================================================

MODEL_NAME = "gemini-3.6-flash"


def get_saved_api_keys():

    key_1 = ""
    key_2 = ""

    try:
        key_1 = str(st.secrets.get("api_key_1", "")).strip()
        key_2 = str(st.secrets.get("api_key_2", "")).strip()

        if "api_keys" in st.secrets:
            key_1 = str(
                st.secrets["api_keys"].get("api_key_1", key_1)
            ).strip()

            key_2 = str(
                st.secrets["api_keys"].get("api_key_2", key_2)
            ).strip()

    except Exception:
        pass

    return key_1, key_2


def get_selected_api_key(user_api_key, selected_key):
    """
    Prefer the user's own API key.

    If the user did not provide one, use the selected key from
    secrets.toml.
    """

    user_api_key = user_api_key.strip()

    if user_api_key:
        return user_api_key

    if selected_key == "API Key 1":
        return saved_key_1

    if selected_key == "API Key 2":
        return saved_key_2

    return ""

# ============================================================
# HERO HEADER
# ============================================================

st.title("🌿 BotaniQ")
st.subheader("Smart visual plant health analysis for home gardeners")

st.caption(
    "Upload a plant image and describe what you have noticed."
)

# ============================================================
# ANALYSIS UI STATE
# ============================================================

if "hide_input_preview" not in st.session_state:
    st.session_state.hide_input_preview = False


def reset_analysis_view():
    # Show the preview again whenever the user selects/changes the image.
    st.session_state.hide_input_preview = False


def start_analysis_view():
    # Runs before Streamlit reruns the script after the Analyze button click.
    # This makes the large upper preview disappear immediately.
    st.session_state.hide_input_preview = True


# ============================================================
# INPUT SECTION
# ============================================================

left_col, right_col = st.columns(
    [1.1, 0.9],
    gap="large"
)

# ============================================================
# IMAGE INPUT
# ============================================================

with left_col:
    st.subheader("📷 Upload Plant Image")

    uploaded_file = st.file_uploader(
        "Upload a clear photo of your plant",
        type=["jpg", "jpeg", "png"],
        help=(
            "For best results, include leaves, stem and soil "
            "when possible."
        ),
        key="plant_uploader",
        on_change=reset_analysis_view
    )

    image = None

    if uploaded_file is not None:
        image = Image.open(uploaded_file)

        # Show the large preview only before analysis starts.
        # Once Analyze My Plant is clicked, it stays hidden.
        if not st.session_state.hide_input_preview:
            st.image(
                image,
                caption="Uploaded Plant",
                use_container_width=True
            )

# ============================================================
# DESCRIPTION INPUT
# ============================================================

with right_col:
    st.subheader("📝 What Did You Notice?")

    symptoms = st.text_area(
        "Describe what you noticed about the plant",
        placeholder=(
            "Example:\n"
            "Leaves are turning yellow and have brown spots. "
            "Some leaves are curling and the plant looks weaker than usual."
        ),
        height=220
    )

    st.caption(
        "Mention yellowing, spots, insects, wilting, curling, "
        "slow growth, or anything unusual."
    )

# ============================================================
# API KEY SECTION
# ============================================================

st.markdown("---")

st.subheader("🔑 Gemini API Key")

st.warning(
    "⚠️ The saved API keys provided by BotaniQ may be expired, "
    "revoked, or out of quota. For the most reliable results, "
    "we recommend using your own Gemini API key."
)

saved_key_1, saved_key_2 = get_saved_api_keys()

api_input_col, api_saved_col = st.columns(
    [1.2, 0.8],
    gap="large"
)

with api_input_col:
    user_api_key = st.text_input(
        "Enter your own Gemini API key",
        type="password",
        placeholder="Paste your Gemini API key here",
        help=(
            "Your own key takes priority over the saved keys. "
            "It is used only for the current analysis session."
        )
    )

with api_saved_col:

    saved_options = []

    if saved_key_1:
        saved_options.append("API Key 1")

    if saved_key_2:
        saved_options.append("API Key 2")

    if saved_options:
        selected_saved_key = st.selectbox(
            "Or select a saved API key",
            options=["None"] + saved_options,
            help=(
                "These keys are stored in Streamlit secrets.toml "
                "and are fallback options only."
            )
        )
    else:
        selected_saved_key = "None"
        st.selectbox(
            "Or select a saved API key",
            options=["No saved keys available"],
            disabled=True
        )

st.caption(
    "If you enter your own key, BotaniQ will always use your key "
    "instead of the saved keys."
)


# ============================================================
# ANALYZE BUTTON
# ============================================================

st.markdown("---")

button_col1, button_col2, button_col3 = st.columns(
    [1, 1, 1]
)

with button_col2:
    analyze = st.button(
        "🔍 Analyze My Plant",
        use_container_width=True,
        on_click=start_analysis_view
    )

# ============================================================
# MASTER PROMPT
# ============================================================

MASTER_PROMPT = """
You are "BotaniQ", a friendly, practical, cautious, and
evidence-based AI gardening assistant for home gardeners.

The user has uploaded an image of a plant.

The gardener may also provide a written description of what they noticed.

IMPORTANT:
The gardener's description is CONTEXT, not visual evidence.
Clearly distinguish between what is visible in the image and what
the gardener reports.

Your analysis must be based primarily on observable evidence.

==================================================
CORE REASONING PRINCIPLE
==================================================

Always reason using:

1. OBSERVATION
   What can actually be seen in the image.

2. POSSIBLE EXPLANATION
   What may be causing the observed condition.

3. CONFIDENCE
   High / Medium / Low.

4. WHAT TO CHECK
   What physical or environmental evidence the gardener should verify.

5. RECOMMENDATION
   What the gardener can safely do next.

Never present a possibility as a confirmed diagnosis.

==================================================
PLANT IDENTIFICATION
==================================================

Identify the plant if reasonably possible.

Provide:

- Common name
- Scientific name
- Plant type
- Possible variety/cultivar if reasonably identifiable
- Identification confidence

Do not invent a precise species or cultivar when the image is insufficient.

==================================================
VISIBLE SYMPTOMS
==================================================

Carefully inspect the image.

Describe only visible characteristics such as:

- Leaf color
- Leaf shape
- Leaf curling
- Wilting
- Yellowing
- Brown or black spots
- Holes
- Torn leaves
- White powder
- Webbing
- Visible insects
- Stem condition
- New growth
- Flowers
- Fruits
- Soil appearance
- Pot/container appearance

==================================================
LEAF AND STEM ANALYSIS
==================================================

Analyze visible patterns.

Consider possible explanations including:

- Natural aging
- Water stress
- Overwatering
- Underwatering
- Poor drainage
- Insufficient light
- Excessive light or heat
- Nutrient-related problems
- Pest damage
- Fungal problems
- Bacterial problems
- Viral problems
- Physical damage
- Environmental stress

Explain why an explanation fits and give confidence.

Do not diagnose disease with certainty from an image alone.

==================================================
PEST CHECK
==================================================

Check for:

- Aphids
- Mealybugs
- Scale-like insects
- Caterpillars
- Mites or mite-like damage
- Thrips-like damage
- Leaf miners
- Webbing
- Chewed leaves
- Holes
- Sticky residue
- Insect clusters

If pests are not visible, say:

"No obvious pests are visible in this image."

Do not claim the plant is pest-free merely because pests cannot be seen.

==================================================
WATERING CHECK
==================================================

Look for visual signs associated with:

- Underwatering
- Overwatering
- Poor drainage
- Water stress
- Root-related stress

A photograph cannot directly measure soil moisture.

Never invent an exact soil moisture percentage.

Recommend checking:

- Moisture below the surface
- Drainage holes
- Standing water
- Recent watering history

==================================================
LIGHT CHECK
==================================================

Assess visible lighting conditions.

Consider:

- Bright direct light
- Bright indirect light
- Shade
- Deep shade
- Possible insufficient light
- Possible excessive heat/light

Do not claim an exact number of sunlight hours from a photograph.

==================================================
POT AND SOIL CHECK
==================================================

If visible, assess:

- Plant-to-pot size
- Drainage
- Pot depth
- Visible roots
- Stability
- Soil level
- Crowding

Do not claim root-bound status without evidence.

For soil only describe visible properties.

Do not claim exact:

- pH
- nutrient levels
- nitrogen
- soil composition

==================================================
PRUNING
==================================================

Identify visible growth that appears:

- Dead
- Severely damaged
- Diseased-looking
- Broken
- Excessively crowded

Do not recommend aggressive pruning from an image alone.

==================================================
GROWTH AND DEVELOPMENT
==================================================

Assess visible:

- Seedling stage
- Young plant
- Mature plant
- New leaves
- Flower buds
- Flowers
- Fruits
- Vegetative growth
- Weak or stretched growth

Do not estimate exact age without evidence.

==================================================
FLOWERING AND FRUITING
==================================================

If visible:

- Identify flowers/fruits
- Comment on development
- Comment on visible damage
- Give possible explanations cautiously

==================================================
OVERALL HEALTH
==================================================

Choose exactly one:

🟢 Healthy-looking
🟡 Needs Attention
🟠 Moderate Concern
🔴 Serious Concern
⚪ Insufficient Information

Explain why using visible evidence.

==================================================
POSSIBLE PROBLEMS
==================================================

Create a ranked list.

For each problem give:

- Possible issue
- Evidence
- Confidence

==================================================
IMMEDIATE ACTIONS
==================================================

Give practical low-risk actions.

Examples:

- Check soil moisture
- Inspect underside of leaves
- Check drainage
- Remove clearly dead material
- Observe new growth
- Inspect nearby plants
- Improve airflow
- Adjust light if appropriate

Avoid strong chemical treatments unless sufficiently justified.

==================================================
PREVENTIVE MEASURES
==================================================

Give practical preventive measures relevant to the plant condition.

==================================================
7-DAY PLAN
==================================================

Create a simple seven-day care plan.

The plan should focus on:

- Observation
- Low-risk care
- Monitoring
- Reassessment

Keep each day's action brief and specific.

==================================================
QUESTIONS
==================================================

Ask no more than five useful follow-up questions if important information
is missing.

Keep questions short and focused.

==================================================
EXPERT HELP
==================================================

Recommend expert gardening/agricultural help when:

- The plant is rapidly deteriorating
- Multiple plants are affected
- A serious disease seems possible
- The image is insufficient
- Root or soil inspection is required
- Specialized treatment may be required

==================================================
SAFETY
==================================================

1. Do not claim certainty when evidence is insufficient.
2. Do not invent species, pests, diseases, measurements or conditions.
3. Clearly separate observation from explanation.
4. Do not claim to have physically measured soil moisture, pH,
   temperature, humidity, nutrients or sunlight duration.
5. Do not provide definitive disease diagnosis from an image alone.
6. Prefer low-risk and low-cost actions.
7. State limitations when image quality is poor.
8. Rank possible problems by likelihood.
9. Use encouraging language.
10. Never make unsupported claims.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

Do not return Markdown.
Do not put the JSON inside code fences.
Do not write anything before or after the JSON.

Use exactly this structure:

{
    "plant": {
        "common_name": "",
        "scientific_name": "",
        "plant_type": "",
        "possible_variety": "",
        "confidence": ""
    },

    "visible_symptoms": [
        "",
        "",
        "",
        ""
    ],

    "severity": {
        "status": "",
        "reason": ""
    },

    "possible_causes": [
        {
            "cause": "",
            "evidence": "",
            "confidence": ""
        },
        {
            "cause": "",
            "evidence": "",
            "confidence": ""
        },
        {
            "cause": "",
            "evidence": "",
            "confidence": ""
        }
    ],

    "pest_check": {
        "visible_evidence": "",
        "observation": "",
        "possible_issue": "",
        "confidence": ""
    },

    "watering": {
        "observation": "",
        "possible_concern": "",
        "what_to_check": ""
    },

    "light": {
        "observation": "",
        "possible_concern": "",
        "recommended_action": ""
    },

    "pot_soil": {
        "pot_observation": "",
        "soil_observation": "",
        "recommended_check": ""
    },

    "growth": {
        "stage": "",
        "observation": ""
    },

    "flowering_fruiting": {
        "observation": "",
        "possible_concern": ""
    },

    "pruning": "",

    "immediate_actions": [
        "",
        "",
        "",
        "",
        ""
    ],

    "preventive_measures": [
        "",
        "",
        "",
        ""
    ],

    "seven_day_plan": [
        {
            "day": "Day 1",
            "action": ""
        },
        {
            "day": "Day 2",
            "action": ""
        },
        {
            "day": "Day 3",
            "action": ""
        },
        {
            "day": "Day 4",
            "action": ""
        },
        {
            "day": "Day 5",
            "action": ""
        },
        {
            "day": "Day 6",
            "action": ""
        },
        {
            "day": "Day 7",
            "action": ""
        }
    ],

    "questions": [
        "",
        "",
        ""
    ],

    "expert_help": "",

    "summary": {
        "main_concern": "",
        "most_useful_next_step": ""
    }
}
"""

# ============================================================
# ANALYSIS
# ============================================================

if analyze:

    if uploaded_file is None:

        st.warning(
            "🌱 Please upload a plant image first."
        )

    else:

        GOOGLE_API_KEY = get_selected_api_key(
            user_api_key,
            selected_saved_key
        )

        if not GOOGLE_API_KEY:
            st.error(
                "🔑 Please enter your own Gemini API key or select "
                "one of the available saved API keys."
            )
            st.stop()

        genai.configure(
            api_key=GOOGLE_API_KEY
        )

        # Show a large centered examination message while Gemini is working.
        loading_placeholder = st.empty()
        loading_placeholder.subheader("🌿 BotaniQ is examining your image...")

        try:

            # ----------------------------------------------------
            # IMAGE
            # ----------------------------------------------------

            image = Image.open(uploaded_file)

            # ----------------------------------------------------
            # GARDENER CONTEXT
            # ----------------------------------------------------

            user_context = f"""
Gardener's description:

{symptoms if symptoms.strip() else "The gardener did not provide a description."}

Treat this as supporting context only, not visual evidence.
Clearly distinguish what is visible in the image from what the
gardener has reported.
"""

            # ----------------------------------------------------
            # FINAL PROMPT
            # ----------------------------------------------------

            final_prompt = (
                    MASTER_PROMPT
                    + "\n\n"
                    + user_context
            )

            # ----------------------------------------------------
            # MODEL
            # ----------------------------------------------------

            model = genai.GenerativeModel(
                MODEL_NAME
            )

            # ----------------------------------------------------
            # SEND IMAGE + PROMPT
            # ----------------------------------------------------

            response = model.generate_content(
                [
                    final_prompt,
                    image
                ]
            )

            # ----------------------------------------------------
            # CLEAN RESPONSE
            # ----------------------------------------------------

            result_text = response.text.strip()

            if result_text.startswith("```json"):

                result_text = result_text[7:]

            elif result_text.startswith("```"):

                result_text = result_text[3:]

            if result_text.endswith("```"):
                result_text = result_text[:-3]

            result_text = result_text.strip()

            # ----------------------------------------------------
            # JSON
            # ----------------------------------------------------

            data = json.loads(result_text)

            # Analysis is complete, so remove the centered loading message.
            loading_placeholder.empty()

            # ====================================================
            # REPORT TITLE
            # ====================================================

            st.markdown("---")

            st.title("🌿 BotaniQ Report")

            # ====================================================
            # TOP CARDS
            # ====================================================

            col1, col2, col3 = st.columns(
                [1.05, 1.35, 0.9],
                gap="small"
            )

            # ====================================================
            # IMAGE CARD
            # ====================================================

            with col1:

                with st.container(border=True):
                    st.subheader("📷 Uploaded Plant")

                    st.image(
                        image,
                        use_container_width=True
                    )

            # ====================================================
            # PLANT CARD
            # ====================================================

            with col2:

                with st.container(border=True):
                    st.subheader("🌱 Plant / Crop")

                    plant = data["plant"]

                    st.markdown(
                        f"**Common Name:** "
                        f"{plant['common_name']}"
                    )

                    st.markdown(
                        f"**Scientific Name:** "
                        f"{plant['scientific_name']}"
                    )

                    st.markdown(
                        f"**Plant Type:** "
                        f"{plant['plant_type']}"
                    )

                    st.markdown(
                        f"**Possible Variety:** "
                        f"{plant['possible_variety']}"
                    )

                    st.markdown(
                        f"**Confidence:** "
                        f"{plant['confidence']}"
                    )

            # ====================================================
            # HEALTH CARD
            # ====================================================

            with col3:

                severity = data["severity"]

                with st.container(border=True):
                    st.subheader("🩺 Plant Health")

                    st.metric("Status", severity["status"])

                    st.write(
                        severity["reason"]
                    )

            # ====================================================
            # VISIBLE SYMPTOMS
            # ====================================================

            with st.container(border=True):

                st.subheader("👀 Visible Symptoms")

                symptom_cols = st.columns(2)

                for i, symptom in enumerate(
                        data["visible_symptoms"]
                ):

                    if symptom:
                        with symptom_cols[i % 2]:
                            st.markdown(
                                f"• {symptom}"
                            )

            # ====================================================
            # POSSIBLE CAUSES
            # ====================================================

            with st.container(border=True):

                st.subheader("🔍 Possible Causes")

                causes = data["possible_causes"]

                # Native Streamlit Markdown table.
                # No raw HTML is used here.

                table = (
                    "| Possible Cause | "
                    "Supporting Evidence | "
                    "Confidence |\n"
                )

                table += (
                    "|---|---|---|\n"
                )

                for cause in causes:
                    cause_name = str(
                        cause.get("cause", "")
                    ).replace("|", "/")

                    evidence = str(
                        cause.get("evidence", "")
                    ).replace("|", "/")

                    confidence = str(
                        cause.get("confidence", "")
                    ).replace("|", "/")

                    table += (
                        f"| {cause_name} "
                        f"| {evidence} "
                        f"| **{confidence}** |\n"
                    )

                st.markdown(table)

            # ====================================================
            # WATERING / LIGHT / SOIL
            # ====================================================

            w1, w2, w3 = st.columns(
                3,
                gap="small"
            )

            # ====================================================
            # WATERING
            # ====================================================

            with w1:

                with st.container(border=True):
                    st.subheader("💧 Watering Check")

                    watering = data["watering"]

                    st.write(
                        watering["observation"]
                    )

                    st.write(
                        watering["possible_concern"]
                    )

                    st.caption(
                        "Check: "
                        + watering["what_to_check"]
                    )

            # ====================================================
            # LIGHT
            # ====================================================

            with w2:

                with st.container(border=True):
                    st.subheader("☀️ Light Check")

                    light = data["light"]

                    st.write(
                        light["observation"]
                    )

                    st.write(
                        light["possible_concern"]
                    )

                    st.caption(
                        "Action: "
                        + light["recommended_action"]
                    )

            # ====================================================
            # POT + SOIL
            # ====================================================

            with w3:

                with st.container(border=True):
                    st.subheader("🪴 Pot & Soil")

                    pot_soil = data["pot_soil"]

                    st.write(
                        pot_soil["pot_observation"]
                    )

                    st.write(
                        pot_soil["soil_observation"]
                    )

                    st.caption(
                        "Check: "
                        + pot_soil["recommended_check"]
                    )

            # ====================================================
            # PEST / GROWTH / FLOWERING
            # ====================================================

            p1, p2, p3 = st.columns(
                3,
                gap="small"
            )

            # ====================================================
            # PEST
            # ====================================================

            with p1:

                with st.container(border=True):
                    st.subheader("🐛 Pest Check")

                    pest = data["pest_check"]

                    st.markdown(
                        f"**Visible Evidence:** "
                        f"{pest['visible_evidence']}"
                    )

                    st.write(
                        pest["observation"]
                    )

                    st.write(
                        f"**Possible Issue:** "
                        f"{pest['possible_issue']}"
                    )

                    st.write(
                        f"**Confidence:** "
                        f"{pest['confidence']}"
                    )

            # ====================================================
            # GROWTH
            # ====================================================

            with p2:

                with st.container(border=True):
                    st.subheader("🌱 Growth & Development")

                    growth = data["growth"]

                    st.markdown(
                        f"**Stage:** "
                        f"{growth['stage']}"
                    )

                    st.write(
                        growth["observation"]
                    )

            # ====================================================
            # FLOWERING / FRUITING
            # ====================================================

            with p3:

                with st.container(border=True):
                    st.subheader("🌸 Flowering & Fruiting")

                    flowering = data[
                        "flowering_fruiting"
                    ]

                    st.write(
                        flowering["observation"]
                    )

                    st.write(
                        flowering["possible_concern"]
                    )

            # ====================================================
            # ACTIONS / PREVENTION / EXPERT
            # ====================================================

            a1, a2, a3 = st.columns(
                3,
                gap="small"
            )

            # ====================================================
            # IMMEDIATE ACTIONS
            # ====================================================

            with a1:

                with st.container(border=True):

                    st.subheader("✅ Immediate Actions")

                    for i, action in enumerate(
                            data["immediate_actions"],
                            start=1
                    ):

                        if action:
                            st.markdown(
                                f"**{i}.** {action}"
                            )

            # ====================================================
            # PREVENTION
            # ====================================================

            with a2:

                with st.container(border=True):

                    st.subheader("🛡 Preventive Measures")

                    for measure in data[
                        "preventive_measures"
                    ]:

                        if measure:
                            st.markdown(
                                f"• {measure}"
                            )

            # ====================================================
            # EXPERT HELP
            # ====================================================

            with a3:

                with st.container(border=True):
                    st.subheader("👨‍🌾 Expert Help")

                    st.write(
                        data["expert_help"]
                    )

            # ====================================================
            # PRUNING
            # ====================================================

            with st.container(border=True):

                st.subheader("✂️ Pruning Advice")

                st.write(
                    data["pruning"]
                )

            # ====================================================
            # 7-DAY PLAN AND QUESTIONS SIDE BY SIDE
            # ====================================================

            plan_col, questions_col = st.columns(
                [0.7, 0.3],
                gap="medium"
            )

            # ====================================================
            # 7-DAY PLAN - COMPACT GRID (fixed HTML)
            # ====================================================

            with plan_col:

                with st.container(border=True):

                    # 7-Day Plan header
                    plan_header_col, calendar_col = st.columns(
                        [0.68, 0.32],
                        gap="small"
                    )

                    with plan_header_col:
                        st.subheader("📅 7-Day Garden Plan")

                    # Google Calendar event
                    plan_start = date.today()
                    plan_end = plan_start + timedelta(days=7)

                    calendar_description_lines = []

                    for item in data["seven_day_plan"]:

                        day_name = str(
                            item.get("day", "")
                        ).strip()

                        action = str(
                            item.get("action", "")
                        ).strip()

                        if day_name or action:
                            calendar_description_lines.append(
                                f"{day_name}: {action}"
                            )

                    calendar_description = (
                            "BotaniQ 7-Day Garden Plan\n\n"
                            + "\n".join(calendar_description_lines)
                            + "\n\n"
                              "Generated by BotaniQ. This plan provides "
                              "general visual gardening guidance."
                    )

                    calendar_url = (
                            "https://calendar.google.com/calendar/render"
                            "?action=TEMPLATE"
                            "&text="
                            + quote("BotaniQ - 7-Day Garden Plan")
                            + "&dates="
                            + plan_start.strftime("%Y%m%d")
                            + "/"
                            + plan_end.strftime("%Y%m%d")
                            + "&details="
                            + quote(calendar_description)
                    )

                    with calendar_col:

                        st.link_button(
                            "📅 Add to Google Calendar",
                            calendar_url,
                            use_container_width=True
                        )

                    # Daily plan
                    for item in data["seven_day_plan"]:
                        with st.container(border=True):
                            st.write(
                                f"**{item['day']}**"
                            )

                            st.write(
                                item["action"]
                            )

            # ====================================================
            # QUESTIONS - COMPACT SIDE PANEL (fixed markdown)
            # ====================================================

            with questions_col:

                with st.container(border=True):

                    st.subheader("❓ Questions for You")

                    valid_questions = [
                        q
                        for q in data["questions"]
                        if q
                    ]

                    if valid_questions:

                        for i, question in enumerate(
                                valid_questions,
                                start=1
                        ):
                            # Simple numbered list, no bold to avoid markdown issues
                            st.markdown(
                                f"{i}. {question}"
                            )

                    else:

                        st.write(
                            "No additional questions needed."
                        )

            # ====================================================
            # FINAL SUMMARY
            # ====================================================

            summary = data["summary"]

            st.subheader("⭐ BotaniQ Summary")

            s1, s2 = st.columns(2)

            with s1:

                st.markdown(
                    "**Main Concern**"
                )

                st.write(
                    summary["main_concern"]
                )

            with s2:

                st.markdown(
                    "**Most Useful Next Step**"
                )

                st.write(
                    summary["most_useful_next_step"]
                )


        # ========================================================
        # JSON ERROR
        # ========================================================

        except json.JSONDecodeError:

            loading_placeholder.empty()
            st.error(
                "The AI returned an unexpected response format. "
                "Please click Analyze My Plant again."
            )


        # ========================================================
        # GENERAL ERROR
        # ========================================================

        except Exception as e:

            loading_placeholder.empty()
            st.error(
                f"❌ Unable to analyze the plant: {str(e)}"
            )

# ============================================================
# FOOTER
# ============================================================

st.caption("BotaniQ provides visual guidance and does not replace professional horticultural or agricultural diagnosis.")
