# AI for Publishing

This project is a POC for the article ...tbd... , it provides a tool for creating articles starting from an existing 
knowledge base provided by the user.
The underline idea is that article generated in such a way are safe from an Intellectual Property perspective which is 
provided by the user after previously ensuring that those base article (forming the knowledge base) are safe from an IP perspective


Diagram:
...


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


