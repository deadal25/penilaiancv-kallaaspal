import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

def compute_similarity(cv_parts, job_parts, model, df):

    results = []

    for i, job in enumerate(job_parts):

        sim_edu = cosine_similarity(
            model.encode([cv_parts['edu']]),
            model.encode([job['edu']])
        )[0][0]

        sim_exp = cosine_similarity(
            model.encode([cv_parts['exp']]),
            model.encode([job['exp']])
        )[0][0]

        sim_skill = cosine_similarity(
            model.encode([cv_parts['skill']]),
            model.encode([job['skill']])
        )[0][0]

        score = (
            sim_skill * 0.5 +
            sim_exp * 0.4 +
            sim_edu * 0.1
        )

        results.append({
            "job_title": df.iloc[i]['job_title'],
            "score": score,
            "skill": sim_skill,
            "exp": sim_exp,
            "edu": sim_edu
        })

    return pd.DataFrame(results)