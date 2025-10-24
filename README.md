# WWSI-GenAI

Course materials for GenAI course at WWSI.

## Setup

### 1. Create Conda Environment

Create a new conda environment with Python 3.11:

```bash
conda create -n wwsi-genai python=3.11 -y
```

### 2. Activate Environment

```bash
conda activate wwsi-genai
```

### 3. Install Dependencies

Install required packages from requirements.txt:

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the root directory with your API keys and configuration:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=your-openai-api-key-here

# Optional: OpenAI Organization (if applicable)
OPENAI_ORG_ID=your-org-id-here

# Optional: Model Configuration
OPENAI_MODEL=gpt-4
```

See `.env.example` for a template.

### 5. Start Jupyter

Launch Jupyter to work with the notebooks:

```bash
jupyter notebook
```

or

```bash
jupyter lab
```

## Project Structure

```
WWSI-GenAI/
├── notebooks/          # Jupyter notebooks for course materials
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (create this file)
└── README.md          # This file
```