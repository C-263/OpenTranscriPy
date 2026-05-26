import os
import shutil


import os
import shutil

from sympy import false


class TranscriptionJob:

    RESERVED_PREFIXES = [
        "whisper",
        "vosk",
        "speech_recognition"
    ]

    def __init__(
        self,
        cache_dir,
        audio_path,
        job_name="default"
    ):

        self.cache_dir = cache_dir

        self.project_name = os.path.splitext(
            os.path.basename(audio_path)
        )[0]

        self.project_dir = os.path.join(
            cache_dir,
            self.project_name
        )

        self.jobs_dir = os.path.join(
            self.project_dir,
            "jobs"
        )

        os.makedirs(self.jobs_dir, exist_ok=True)

        self.job_name = job_name

        self.job_dir = os.path.join(
            self.jobs_dir,
            self.job_name
        )

        os.makedirs(self.job_dir, exist_ok=True)

        self.final_path = os.path.join(
            self.job_dir,
            "final.txt"
        )

    def list_jobs(self):

        return [
            d for d in os.listdir(self.jobs_dir)
            if os.path.isdir(
                os.path.join(self.jobs_dir, d)
            )
        ]

    def change_job(self, job_name):

        self.job_name = job_name

        self.job_dir = os.path.join(
            self.jobs_dir,
            self.job_name
        )

        os.makedirs(self.job_dir, exist_ok=True)

        self.final_path = os.path.join(
            self.job_dir,
            "final.txt"
        )

    def select_job(self):

        jobs = self.list_jobs()

        if jobs:

            print("\n📂 Jobs encontrados:\n")

            for i, job in enumerate(jobs, start=1):
                print(f"[{i}] {job}")

            print("\n[N] Novo job")

            escolha = input("\nEscolha: ").strip()


            if escolha.lower() == "n":

                novo = input("Nome do novo job: ").strip()

                if any(
                        novo.startswith(prefix)
                        for prefix in self.RESERVED_PREFIXES
                ):
                    print("❌ prefixo reservado")

                    return False

                self.change_job(novo)

                return

            try:

                index = int(escolha) - 1

                nome = jobs[index]

                if (
                        self.is_reserved_job(nome)
                        and nome != self.job_name
                ):
                    print("❌ job pertence a outro modelo")

                    return False

                self.change_job(nome)

                print(f"\n📁 Job selecionado: {nome}")

                print("\n[1] Continuar")
                print("[2] Resetar")

                op = input("\nEscolha: ").strip()

                if op == "1":
                    return True

                if op == "2":
                    shutil.rmtree(self.job_dir)

                    os.makedirs(self.job_dir, exist_ok=True)

                    print("🗑️ Job resetado")

                    return True

                print("❌ opção inválida")

            except Exception as e:

                print(f"❌ erro: {e}")

    def block_exists(self, index):

        path = self.get_bloco_path(index)

        return os.path.exists(path)

    def get_bloco_path(self, index):

        return os.path.join(
            self.job_dir,
            f"bloco_{index}.txt"
        )

    def load_block(self, index):

        with open(
            self.get_bloco_path(index),
            "r",
            encoding="utf-8"
        ) as f:

            return f.read().strip()

    def save_block(self, index, texto):

        with open(
            self.get_bloco_path(index),
            "w",
            encoding="utf-8"
        ) as f:

            f.write(texto)

    def save_final(self, textos):

        with open(
            self.final_path,
            "w",
            encoding="utf-8"
        ) as f:

            f.write("\n".join(textos))

    def is_reserved_job(self, job_name):

        return any(
            job_name.startswith(prefix)
            for prefix in self.RESERVED_PREFIXES
        )