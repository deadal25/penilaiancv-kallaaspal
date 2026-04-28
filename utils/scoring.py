# =========================================================
# ⚖️ WEIGHTED SCORING
# =========================================================

def compute_weighted(df_sim):

    df_sim['weighted'] = (
        df_sim['skill_sbert'] * 0.5 +
        df_sim['exp_sbert'] * 0.4 +
        df_sim['edu_sbert'] * 0.1
    )

    return df_sim


# =========================================================
# 📊 INTERPRET SCORE
# =========================================================
def interpret_score(score):
    if score >= 75:
        return "Sangat Tinggi"
    elif score >= 60:
        return "Tinggi"
    elif score >= 50:
        return "Cukup"
    else:
        return "Rendah"