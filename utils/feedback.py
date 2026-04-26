#TAMBAHAN
from utils.scoring import interpret_score


def generate_feedback(cv_parts, best_job, score, skill, exp, edu):

    feedback = f"""
CV Anda menunjukkan latar belakang pendidikan {cv_parts['degree']} dengan jurusan {cv_parts['major']}. 
Berdasarkan analisis kecocokan terhadap posisi {best_job}, diperoleh skor keseluruhan sebesar {round(score,2)}% 
yang termasuk dalam kategori {interpret_score(score)}.

Dari hasil evaluasi, aspek kemampuan (skill) memiliki skor {round(skill*100,2)}%, 
pengalaman {round(exp*100,2)}%, dan pendidikan {round(edu*100,2)}%.

Hal ini menunjukkan bahwa """

    if skill < 0.6:
        feedback += "kemampuan teknis Anda masih perlu ditingkatkan agar lebih sesuai dengan kebutuhan pekerjaan. "

    if exp < 0.6:
        feedback += "pengalaman kerja yang relevan masih kurang dan sebaiknya diperkuat dengan pengalaman praktis atau proyek nyata. "

    if edu < 0.6:
        feedback += "latar belakang pendidikan belum sepenuhnya selaras dengan posisi yang dituju. "

    feedback += """
Disarankan untuk menambahkan lebih banyak detail terkait proyek, tools yang digunakan, serta pencapaian konkret dalam CV 
agar meningkatkan nilai kesesuaian dengan posisi yang diinginkan.
"""

    return feedback
