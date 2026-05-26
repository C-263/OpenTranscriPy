from transcriber.cli import *


def main():
    try:
        config = TranscriptionInput().collect()
    except (ValueError, FileNotFoundError) as e:
        print(e)
        return

    TranscriptionRunner(config).run()


if __name__ == "__main__":
    main()