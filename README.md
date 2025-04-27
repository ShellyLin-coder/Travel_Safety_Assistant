# Chicago Travel Safety Assistant 🛡️

A Streamlit web application that helps travelers assess safety risk based on real-time crime data around Chicago.

## Features

- 📍 Input any Chicago address to analyze nearby crimes (within 500 meters)
- 📊 Risk score calculated based on crime density, violent crime ratio, nighttime incidents, and arrest rates
- 🧠 GPT-4 generates personalized travel safety advice
- 🗺️ Interactive map showing location and danger zone
- 📥 Downloadable full safety report

## Demo

[🌐 Launch App on Streamlit Cloud](https://share.streamlit.io/your-app-link)

## How to Run Locally

1. Clone this repository:
    ```bash
    git clone https://github.com/ShellyLin-coder/Travel_Safety_Assistant.git
    cd Travel_Safety_Assistant
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the app:
    ```bash
    streamlit run streamlit_app.py
    ```

## API Keys

- Google Maps API Key (for address geocoding)
- OpenAI API Key (for GPT-4 suggestions)

You will be asked to enter these keys on the sidebar of the app.

## Project Structure

| File | Purpose |
|-----|---------|
| `streamlit_app.py` | Main Streamlit front-end |
| `utils.py` | Backend logic (data processing, risk scoring, API calling) |
| `requirements.txt` | Required Python packages |
| `README.md` | This project description |

## License

MIT License
