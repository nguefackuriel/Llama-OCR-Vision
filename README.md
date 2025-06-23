# Llama-OCR-Vision



This Python tool extracts text from scanned images using **Llama OCR (Optical Character Recognition)** with **Together AI**.


---

## 🔧 Setup Instructions


#### Libraries installation

Clone the GitHub repo using:

```bash
git clone https://github.com/nguefackuriel/Llama-OCR-Vision.git
```

Run this in Command Prompt:

```bash
cd Llama-OCR-Vision
```

Run this in Command Prompt:

```bash
pip install -r requirements.txt
```



1. Create an account on [Together AI](https://www.together.ai/), create an API key and copy it.

2. Create a folder .streamlit and inside the folder, create a file secrets.toml and paste:

TOGETHER_API_KEY ="YOUR_KEY"

Replace YOUR_KEY by your copied API key.

You can change the model used in the codes [main.py](https://github.com/nguefackuriel/Llama-OCR-Vision/main.py) and [streamlit_app.py](https://github.com/nguefackuriel/Llama-OCR-Vision/streamlit_app.py) by choosing between: **"Llama-3.2-90B-Vision"**, **"Llama-3.2-11B-Vision"**, **"free"** 



### 1. To run the script in a command line use the file main.py and the command bellow:


```bash
python main.py input_file.jpg output_file.md
```

for example:

```bash
python main.py ordo_2.jpg ordo_2_res_free.md
```

### 2. To run the script using streamlit:

```bash
streamlit run streamlit_app.py
```


