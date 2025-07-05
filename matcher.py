from sentence_transformers import SentenceTransformer, util
import numpy as np
import pandas as pd

# Load SBERT model
model = SentenceTransformer("all-MiniLM-L6-v2")

def match_resume_to_jobs(resume_text, jobs_df, top_k=5):
    # Ensure 'job_description' column exists
    if 'job_description' not in jobs_df.columns:
        raise KeyError("Missing 'job_description' column in jobs CSV.")

    job_texts = jobs_df["job_description"].astype(str).tolist()
    job_embeddings = model.encode(job_texts, convert_to_tensor=True)
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)

    # Compute cosine similarities
    scores = util.pytorch_cos_sim(resume_embedding, job_embeddings)[0].cpu().numpy()

    # Prepare result DataFrame
    top_indices = np.argsort(scores)[::-1][:top_k]
    matches = jobs_df.iloc[top_indices].copy()
    matches["score"] = scores[top_indices]
    return matches
