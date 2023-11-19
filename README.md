# About
Content Generation bot from knowledge base

# Init the env
Run the provided **init.sh** script to pull the docker image of the Vector DB (qdrant) and install the required python libraries

# Run the vector DB
```bash
docker run -p 6333:6333 -ti qdrant/qdrant
```

# Ingest Knowledge base in Qdrant
```bash
python src/ingest.py http://url/to/pdf1 http://url/to/pdf2 ... http://url/to/pdfn
```

# Start the bot
```bash
python src/bot.py
```


