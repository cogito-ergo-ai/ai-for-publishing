# AI for Publishing - Article Generation Tool

## Introduction
AI for Publishing is a proof of concept (POC) project aimed at automating the creation of articles. 
It's designed to work with a set of existing articles (acting as knowledge base) supplied by the user, ensuring the 
generation of content that respects Intellectual Property (IP) rights. 

This POC is part of the article series "...tbd...".

## System Architecture
[Insert a detailed diagram here to illustrate the system architecture or workflow]

## Getting Started

### Environment Setup
Setup you python environment (suggested python3.11) and install all requirements:
```bash
pip install -r requirements.txt
```

### Running the Vector Database

Use Docker to run the Qdrant database:
```bash
docker run -p 6333:6333 -ti qdrant/qdrant
```
You can also pre-load our test collection of real articles with:
```bash
curl -X POST 'http://localhost:6333/collections/knowledge_base/snapshots/upload' \
    -H 'Content-Type:multipart/form-data' \
    -F 'snapshot=@./data/vector-db-articles.snapshot'
```
*otherwise* if you want to use your own articles you can manually load them via:
```bash
python ai_publishing/ingest.py http://url/to/pdf1 /path/to/local/pdf2
```

### Starting the AI Bot
Once your articles are available, start the bot to engage in an interactive chat for article generation.
```bash
python ai_publishing/bot.py
```

## Usage Instructions / Quick showcase

...
