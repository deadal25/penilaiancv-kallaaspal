#TAMBAHAN
from utils.scoring import interpret_score

def generate_feedback(cv_parts, best_job, score, skill, exp, edu):
    s_pct, e_pct, d_pct = skill * 100, exp * 100, edu * 100
    feedback = f"""
    CV Anda menunjukkan profil akademik sebagai lulusan {cv_parts['degree']} {cv_parts['major']}. 
    Melalui analisis mendalam menggunakan Sentence-BERT terhadap posisi <b>{best_job}</b>, 
    sistem memberikan skor kesesuaian sebesar <b>{round(score, 2)}%</b> yang dikategorikan sebagai <b>{interpret_score(score)}</b>.
    """
    kelebihan = []
    if s_pct >= 70: kelebihan.append(f"penguasaan teknis (skill) yang sangat kuat di angka {round(s_pct,1)}%")
    if e_pct >= 70: kelebihan.append(f"rekam jejak pengalaman yang sangat relevan ({round(e_pct,1)}%)")
    if d_pct >= 70: kelebihan.append(f"latar belakang pendidikan yang sangat linier ({round(d_pct,1)}%)")
    if kelebihan:
        feedback += f"<b>Kekuatan Utama:</b> Profil Anda memiliki keunggulan pada " + ", serta ".join(kelebihan) + ". "
        feedback += "Hal ini mengindikasikan bahwa secara fundamental, Anda memiliki aset yang kuat untuk berkontribusi pada posisi ini"
    feedback += "<b>Analisis Pengembangan:</b> "
    if s_pct < 60:
        feedback += f"Terdapat celah kompetensi pada aspek teknis ({round(s_pct,1)}%). Kami menyarankan Anda untuk lebih eksplisit dalam mencantumkan <i>tools</i>, <i>software</i>, atau metodologi spesifik yang digunakan pada pekerjaan sebelumnya. "
    else:
        feedback += "Aspek kemampuan teknis Anda sudah cukup bersaing, namun tetap perlu diperbarui dengan tren industri terbaru. "
    if e_pct < 60:
        feedback += f"Selain itu, bobot pengalaman kerja ({round(e_pct,1)}%) menunjukkan adanya ketidaksesuaian durasi atau tanggung jawab dengan profil ideal. Fokuslah pada penulisan <i>achievement-based CV</i> daripada sekadar daftar tugas. "
    if d_pct < 60:
        feedback += f"Dari sisi edukasi ({round(d_pct,1)}%), terlihat adanya sedikit divergensi antara jurusan atau konsentrasi studi dengan kualifikasi jabatan yang spesifik. "
    feedback += f"""
    <b>Saran Strategis:</b> Untuk meningkatkan daya saing, cobalah untuk mengintegrasikan kata kunci (keywords) yang ditemukan pada deskripsi pekerjaan <i>{best_job}</i> ke dalam ringkasan profesional Anda. 
    Pastikan setiap poin pengalaman menyertakan hasil kuantitatif (misalnya: meningkatkan efisiensi sebesar 20%) untuk memberikan bukti nyata atas klaim kemampuan Anda.
    """
    return feedback
