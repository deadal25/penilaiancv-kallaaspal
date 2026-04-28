from utils.scoring import interpret_score

def generate_feedback(cv_parts, best_job, score, skill, exp, edu):
    s_pct, e_pct, d_pct = skill * 100, exp * 100, edu * 100
    feedback = f"""
    CV Anda menunjukkan profil akademik sebagai lulusan {cv_parts['degree']} {cv_parts['major']}. 
    Melalui analisis mendalam menggunakan Sentence-BERT terhadap posisi <b>{best_job}</b>, 
    sistem memberikan skor kesesuaian sebesar <b>{float(score):.2f}%</b> 
    yang dikategorikan sebagai <b>{interpret_score(float(score))}</b>.
    """
    kelebihan = []
    if s_pct >= 70:
        kelebihan.append(f"penguasaan teknis (skill) yang sangat kuat di angka {float(s_pct):.2f}%")
    if e_pct >= 70:
        kelebihan.append(f"rekam jejak pengalaman yang sangat relevan ({float(e_pct):.2f}%)")
    if d_pct >= 70:
        kelebihan.append(f"latar belakang pendidikan yang sangat linier ({float(d_pct):.2f}%)")
    if kelebihan:
        feedback += f"<b>Kekuatan Utama:</b> Profil Anda memiliki keunggulan pada " + ", serta ".join(kelebihan) + ". "
        feedback += "Hal ini mengindikasikan bahwa secara fundamental, Anda memiliki aset yang kuat untuk berkontribusi pada posisi ini. "
    feedback += "<b>Analisis Pengembangan:</b> "
    if s_pct < 60:
        feedback += f"Terdapat celah kompetensi pada aspek teknis ({float(s_pct):.2f}%). "
    else:
        feedback += "Aspek kemampuan teknis Anda sudah cukup bersaing, namun tetap perlu diperbarui dengan tren industri terbaru. "
    if e_pct < 60:
        feedback += f"Bobot pengalaman kerja ({float(e_pct):.2f}%) masih belum optimal. "
    if d_pct < 60:
        feedback += f"Dari sisi edukasi ({float(d_pct):.2f}%), masih belum sepenuhnya selaras. "
    feedback += f"""
    <b>Saran Strategis:</b> Integrasikan keyword dari <i>{best_job}</i> dan tambahkan pencapaian kuantitatif.
    """
    return feedback