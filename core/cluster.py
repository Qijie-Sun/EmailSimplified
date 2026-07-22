from sentence_transformers import SentenceTransformer
import numpy as np
import hdbscan
from collections import defaultdict

model = SentenceTransformer('all-MiniLM-L6-v2')

# Convert an email's subject and content to a string
def email_to_text(email):
    return f'{email.get('Subject', '')} {email.get('Content', '')}'.strip()

# Convert emails into vector embeddings
def embed_emails(emails):
    texts = [email_to_text(e) for e in emails]
    embeddings = model.encode(texts, normalize_embeddings=True)
    return np.array(embeddings)

# Cluster embeddings using HDBSCAN
def cluster_embeddings(embeddings, min_cluster_size=3):
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        metric='euclidean',
        cluster_selection_method='eom'
    )
    
    labels = clusterer.fit_predict(embeddings)
    return labels

# Generate cluster names (replace with LLM generation with Qwen3.5-2B)
def generate_cluster_names(embeddings, emails, labels):
    names = {}
    for label in set(labels):
        if label == -1:
            names[label] = 'Other'
            continue

        idxs = np.where(labels == label)[0]
        centroid = embeddings[idxs].mean(axis=0)
        closest = idxs[np.argmax(embeddings[idxs] @ centroid)]
        names[label] = emails[closest].get('Subject')
    return names

# Group emails by their clusters
def group_emails_by_cluster(embeddings, emails, labels):
    names = generate_cluster_names(embeddings, emails, labels)
    groups = defaultdict(list)

    for email, label in zip(emails, labels):
        groups[names[label]].append(email)
    return groups