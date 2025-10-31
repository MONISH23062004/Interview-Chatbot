# 💬 Interview Chatbot using Streamlit & OpenAI API

This project is an **AI-powered Interview Chatbot** built using **Python**, **Streamlit**, and the **OpenAI API**.  
It provides an interactive interface for users to simulate HR or technical interview scenarios, powered by GPT models.
**-----------------------------------------**
## 🚀 Features
- 🧠 Smart AI-based conversation system  
- 💻 Streamlit web interface for easy interaction  
- 🔐 Secure API key handling using `.gitignore`  
- ⚡ Fast, lightweight, and easy to deploy  
**------------------------------------**
## 🛠️ Technologies Used
- **Python**
- **Streamlit**
- **OpenAI API**
- **VS Code**
- **Git & GitHub**

**-------------------------------**

## 🔒 Security Setup

This project includes a **`.gitignore`** file to prevent sensitive files from being pushed to GitHub.  
The **OpenAI API key** is securely stored in `.streamlit/secrets.toml`, which is **ignored by Git**.

### File structure:

project-folder/
│
├── app.py
├── .gitignore
└── .streamlit/secrets.toml


### Example `.streamlit/secrets.toml`
```toml
OPENAI_API_KEY = "your-real-api-key-here"

