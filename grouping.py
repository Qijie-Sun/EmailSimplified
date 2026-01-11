from sentence_transformers import SentenceTransformer
import numpy as np
import hdbscan
from collections import defaultdict

model = SentenceTransformer("all-MiniLM-L6-v2")

def email_to_text(email):
    return f"{email.get('Subject', '')} {email.get('Content', '')}".strip()

def embed_emails(emails):
    texts = [email_to_text(e) for e in emails]
    embeddings = model.encode(texts, normalize_embeddings=True)
    return np.array(embeddings)

def cluster_embeddings(embeddings, min_cluster_size=3, min_samples=1):
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        metric='euclidean',
        cluster_selection_method='eom'
    )
    
    labels = clusterer.fit_predict(embeddings)
    return labels

def group_emails_by_cluster(emails, labels):
    grouped = defaultdict(list)
    
    for email, label in zip(emails, labels):
        cluster_name = f"Cluster_{label}" if label != -1 else "Other"
        grouped[cluster_name].append(email)
    
    return grouped