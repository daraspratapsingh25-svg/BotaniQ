# 🌿 BotaniQ

### AI-Powered Plant Health Analysis & Personalized Garden Care Assistant

BotaniQ is an AI-powered gardening assistant that analyzes plant images and provides practical, cautious, and personalized plant-care guidance.

It uses **Google Gemini multimodal AI** to examine uploaded plant images, identify visible symptoms, suggest possible causes, and generate a practical 7-day care plan.

## 🚀 Live Demo

https://botaniq.streamlit.app

## ✨ Features

- 📷 **AI Plant Image Analysis**
  - Upload a clear image of a plant for visual analysis.
  - Identify the plant when reasonably possible.

- 🩺 **Plant Health Assessment**
  - Evaluates visible symptoms and overall plant health.
  - Categorizes the condition from healthy-looking to serious concern.

- 🔍 **Possible Cause Analysis**
  - Provides ranked possible causes.
  - Separates visual evidence from possible explanations.
  - Includes confidence levels.

- 🐛 **Pest Detection**
  - Checks for visible signs of common pests and pest-related damage.

- 💧 **Watering & Light Analysis**
  - Provides visual guidance related to watering, drainage, and lighting conditions.

- 🪴 **Pot & Soil Assessment**
  - Examines visible pot and soil characteristics when available.

- ✂️ **Pruning Guidance**
  - Identifies visible damaged or dead growth and provides cautious pruning advice.

- 🌱 **Growth & Flowering Analysis**
  - Assesses visible growth stages, new growth, flowers, and fruits.

- 📋 **Immediate Actions & Prevention**
  - Provides practical low-risk actions and preventive measures.

- 📅 **7-Day Garden Plan**
  - Generates a personalized seven-day care and monitoring plan.

- 🗓️ **Google Calendar Integration**
  - Adds the generated 7-day garden plan to Google Calendar.

- 🔐 **Flexible Gemini API Key Support**
  - Supports the user's own Gemini API key.
  - Saved keys can be configured through Streamlit secrets.

## 🧠 How It Works

```text
Plant Image + User Description
            ↓
     Google Gemini AI
            ↓
   Visual Plant Analysis
            ↓
 ┌──────────────────────────┐
 │ Plant Identification     │
 │ Visible Symptoms         │
 │ Possible Causes          │
 │ Pest Check               │
 │ Watering & Light Check   │
 │ Pot & Soil Check         │
 │ Growth & Flowering       │
 └──────────────────────────┘
            ↓
 Immediate Actions
            ↓
 Preventive Measures
            ↓
    7-Day Garden Plan
            ↓
    Google Calendar

### 📚 Detailed Commands

For the complete setup and command reference, see:

[RUNNING_COMMANDS.md](RUNNING_COMMANDS.md)