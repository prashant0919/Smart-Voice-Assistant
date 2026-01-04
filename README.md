# 🎙️ Smart Voice Assistant (IoT & Generative AI)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-red)
![OpenAI](https://img.shields.io/badge/AI-OpenAI%20%2B%20Whisper-green)
![IoT](https://img.shields.io/badge/IoT-MQTT%20%26%20Blynk-orange)

## 📖 Overview

This project is a sophisticated **Smart Voice Assistant** that combines the power of Generative AI with Internet of Things (IoT) automation. Unlike standard assistants, this system uses **OpenAI Whisper** for state-of-the-art speech recognition and **OpenAI GPT models** for intelligent conversation.

The interface is built using **Streamlit**, providing a user-friendly dashboard to interact with the assistant. It is capable of controlling physical devices (lights, fans, relays) seamlessly through **MQTT** protocols and the **Blynk** platform.

## ✨ Key Features

### 🧠 AI & Voice Processing
* **High-Accuracy STT:** Uses `openai-whisper` for transcribing voice to text with high precision.
* **Intelligent Responses:** Powered by the `openai` API (GPT-3.5/GPT-4) to understand context and complex queries.
* **Voice Output:** Uses `pyttsx3` for offline text-to-speech feedback.
* **Dashboard:** A visual web interface built with `streamlit` to view logs, controls, and transcriptions.

### 🏠 IoT & Automation
* **Hybrid Control:** Devices can be controlled via voice commands or the Blynk mobile app.
* **Protocol:** Uses **MQTT** for low-latency communication between the Python backend and microcontrollers (ESP8266/ESP32).
* **Remote Access:** Control your appliances from anywhere using the Blynk cloud integration.

## 🛠️ Tech Stack

### Software (Python)
* **Interface:** `streamlit`
* **Speech Recognition:** `openai-whisper`
* **LLM/AI:** `openai`
* **Audio Processing:** `sounddevice`, `soundfile`, `scipy`
* **Text-to-Speech:** `pyttsx3`
* **Data Handling:** `pandas`

### IoT & Hardware
* **Connectivity:** MQTT Protocol (using `paho-mqtt` or compatible libraries), Blynk Cloud.
* **Hardware:** Raspberry Pi / Laptop (Server), ESP8266 / ESP32 (Client).
* **Sensors/Actuators:** Relay modules, DHT sensors.

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/your-username/Smart-Voice-Assistant.git](https://github.com/your-username/Smart-Voice-Assistant.git)
cd Smart-Voice-Assistant
