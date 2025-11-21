# Elasticsearch Local Setup Guide

This guide walks you through setting up Elasticsearch locally for hybrid search experiments using Docker.

## Quick Start (No Persistence)

**⚠️ Warning:** This setup does NOT persist data. Data is lost when you remove the container.

```bash
# 1. Start Elasticsearch (no persistence)
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0

# 2. Wait ~30 seconds for startup, then verify
curl http://localhost:9200

# 3. Install Python client (match client version to server version)
pip install 'elasticsearch>=8.0.0,<9.0.0' sentence-transformers

# 4. You're ready! See examples below.
```

**Managing the container:**
```bash
# Stop (data is preserved)
docker stop elasticsearch

# Start again (data still there)
docker start elasticsearch

# Remove container (⚠️ DATA IS DELETED)
docker rm elasticsearch
```

**For persistent data, see "Data Persistence" section below.**

## Prerequisites

Make sure you have Docker installed. You can check with:
```bash
docker --version
```

If you don't have Docker, install it from [Docker Desktop](https://www.docker.com/products/docker-desktop/).

## Installation

### Option 1: Docker (Recommended)

This is the fastest and most reliable method. Start Elasticsearch with a single command:

```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```

### Option 2: Docker Compose (For Persistence)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
      - "9300:9300"
    volumes:
      - es_data:/usr/share/elasticsearch/data

volumes:
  es_data:
    driver: local
```

Then run:
```bash
docker-compose up -d
```

### Option 3: Manual Download (Not Recommended)

Only use this if you cannot use Docker:

```bash
# Download Elasticsearch
curl -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-8.11.0-darwin-x86_64.tar.gz

# Extract
tar -xzf elasticsearch-8.11.0-darwin-x86_64.tar.gz
cd elasticsearch-8.11.0

# Disable security for local development
echo "xpack.security.enabled: false" >> config/elasticsearch.yml

# Start Elasticsearch
./bin/elasticsearch
```

## Managing Elasticsearch (Docker)

### Start/Stop/Restart
```bash
# Start
docker start elasticsearch

# Stop
docker stop elasticsearch

# Restart
docker restart elasticsearch

# Check status
docker ps | grep elasticsearch

# View logs
docker logs -f elasticsearch
```

### Stop and Remove
```bash
# Stop and remove container
docker stop elasticsearch && docker rm elasticsearch

# Remove with volume (deletes all data)
docker stop elasticsearch && docker rm elasticsearch && docker volume rm elasticsearch_es_data
```

## Data Persistence

### Default Setup (No Persistence)
The basic Docker command does NOT persist data. When you remove the container, all data is lost.

### With Persistence
To keep your data between restarts, use a volume:

```bash
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms512m -Xmx512m" \
  -v es_data:/usr/share/elasticsearch/data \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```

Or use Docker Compose (see Option 2 above) which includes persistence by default.

### List volumes
```bash
docker volume ls | grep es_data
```

### Remove volume (deletes all data permanently)
```bash
docker volume rm es_data
```

## Verify Installation

```bash
# Check if Elasticsearch is running
curl http://localhost:9200

# Expected response:
# {
#   "name" : "...",
#   "cluster_name" : "elasticsearch",
#   "version" : { ... },
#   ...
# }
```

## Python Setup

Install required Python packages (match Elasticsearch client version to server version 8.x):

```bash
pip install 'elasticsearch>=8.0.0,<9.0.0' sentence-transformers
```

**Note:** The Elasticsearch Python client version should match your server version. Since we're using Elasticsearch 8.11.0, we install the 8.x client.

## Loading Data into Elasticsearch

### Example 1: Simple Document Indexing

```python
from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

# Check connection
print(es.info())

# Create an index
index_name = "documents"

# Index a document
doc = {
    "title": "Introduction to Elasticsearch",
    "content": "Elasticsearch is a distributed search and analytics engine.",
    "category": "technology"
}

es.index(index=index_name, id=1, document=doc)

# Search
response = es.search(index=index_name, query={"match": {"content": "search"}})
print(response['hits']['hits'])
```

### Example 2: Bulk Loading

```python
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

es = Elasticsearch(['http://localhost:9200'])

# Sample data
documents = [
    {
        "_index": "articles",
        "_id": 1,
        "_source": {
            "title": "Python Programming",
            "content": "Python is a versatile programming language.",
            "date": "2024-01-15"
        }
    },
    {
        "_index": "articles",
        "_id": 2,
        "_source": {
            "title": "Machine Learning Basics",
            "content": "Machine learning is a subset of artificial intelligence.",
            "date": "2024-01-16"
        }
    },
    {
        "_index": "articles",
        "_id": 3,
        "_source": {
            "title": "Vector Search",
            "content": "Vector search enables semantic similarity matching.",
            "date": "2024-01-17"
        }
    }
]

# Bulk insert
success, failed = bulk(es, documents)
print(f"Indexed {success} documents, {failed} failed")
```

### Example 3: Creating Index with Vector Mapping

For hybrid search (BM25 + vector search):

```python
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer

es = Elasticsearch(['http://localhost:9200'])

# Define index mapping with dense vector field
index_name = "hybrid_search_demo"
mapping = {
    "mappings": {
        "properties": {
            "title": {"type": "text"},
            "content": {"type": "text"},
            "embedding": {
                "type": "dense_vector",
                "dims": 384,  # dimension for all-MiniLM-L6-v2
                "index": True,
                "similarity": "cosine"
            }
        }
    }
}

# Create index
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
es.indices.create(index=index_name, body=mapping)

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Sample documents
docs = [
    {"title": "Python Tutorial", "content": "Learn Python programming from scratch"},
    {"title": "Java Guide", "content": "Complete guide to Java development"},
    {"title": "Machine Learning", "content": "Introduction to ML algorithms"}
]

# Index documents with embeddings
for i, doc in enumerate(docs):
    embedding = model.encode(doc["content"]).tolist()
    es.index(
        index=index_name,
        id=i,
        document={
            "title": doc["title"],
            "content": doc["content"],
            "embedding": embedding
        }
    )

print(f"Indexed {len(docs)} documents with embeddings")
```

### Example 4: Hybrid Search Query

```python
# Hybrid search combining BM25 (keyword) and vector similarity
query_text = "programming tutorial"
query_embedding = model.encode(query_text).tolist()

hybrid_query = {
    "query": {
        "bool": {
            "should": [
                # BM25 text search
                {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["title", "content"],
                        "boost": 0.5
                    }
                },
                # Vector similarity search
                {
                    "script_score": {
                        "query": {"match_all": {}},
                        "script": {
                            "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                            "params": {"query_vector": query_embedding}
                        },
                        "boost": 0.5
                    }
                }
            ]
        }
    }
}

results = es.search(index=index_name, body=hybrid_query)
for hit in results['hits']['hits']:
    print(f"Score: {hit['_score']}, Title: {hit['_source']['title']}")
```

## Useful Commands

### List all indices
```python
es.cat.indices(v=True)
```

### Delete an index
```python
es.indices.delete(index="index_name")
```

### Get mapping
```python
es.indices.get_mapping(index="index_name")
```

### Count documents
```python
es.count(index="index_name")
```

## Troubleshooting

### Container won't start
```bash
# Check container logs
docker logs elasticsearch

# Check if container exists
docker ps -a | grep elasticsearch

# Remove and recreate
docker stop elasticsearch && docker rm elasticsearch
# Then run the docker run command again
```

### Port already in use
```bash
# Find process using port 9200
lsof -i :9200

# If it's another Docker container
docker ps | grep 9200

# Stop the conflicting container
docker stop <container_id>
```

### Check logs
```bash
# Follow logs in real-time
docker logs -f elasticsearch

# View last 100 lines
docker logs --tail 100 elasticsearch
```

### Memory issues
The Docker command includes memory settings (`-Xms512m -Xmx512m`). If you need more memory:

```bash
# Stop current container
docker stop elasticsearch && docker rm elasticsearch

# Start with more memory
docker run -d \
  --name elasticsearch \
  -p 9200:9200 \
  -p 9300:9300 \
  -e "discovery.type=single-node" \
  -e "xpack.security.enabled=false" \
  -e "ES_JAVA_OPTS=-Xms1g -Xmx1g" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0
```

### Container keeps restarting
```bash
# Check why it's failing
docker logs elasticsearch

# Common issues:
# 1. Insufficient memory - increase ES_JAVA_OPTS
# 2. Port conflict - change port mapping: -p 9201:9200
# 3. Corrupted data - remove volume and restart
```

### Access container shell
```bash
# Enter container for debugging
docker exec -it elasticsearch bash

# Check Elasticsearch process
docker exec elasticsearch ps aux | grep elasticsearch
```

## Resources

- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [Elasticsearch Docker Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)
- [Python Elasticsearch Client](https://elasticsearch-py.readthedocs.io/)
- [Hybrid Search Tutorial](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html)
- [Docker Documentation](https://docs.docker.com/)

## Tips for Course Work

1. **Start Fresh**: If you encounter issues, it's often easiest to remove and recreate:
   ```bash
   docker stop elasticsearch && docker rm elasticsearch
   ```
   Then run the docker run command again.

2. **Check Connection Before Running Code**: Always verify Elasticsearch is responding:
   ```bash
   curl http://localhost:9200
   ```

3. **Monitor Resources**: Check Docker stats if things seem slow:
   ```bash
   docker stats elasticsearch
   ```

4. **Experiment Safely**: Since data isn't persisted by default, feel free to experiment. You can always start fresh!
