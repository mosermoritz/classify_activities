# 🚲 classify_activities – Auto-Tagging for Strava Activities

Automatically classify your Strava activities – mark commutes, hide walks, yoga, and more from the home feed using the Strava API.

## ✨ Features

- 🔒 Hide walks, yoga and short activities from followers' feed (`hide_from_home`)
- 🚲 Automatically mark rides as **commutes** based on distance, device, and naming rules
- 📅 Classifies activities from the past day (can be scheduled via webhook or cron)
- ✅ Includes tests for all key features

## 📦 Installation

```bash
git clone https://github.com/yourusername/classify_activities.git
cd classify_activities
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
