import subprocess
import os
import pathlib

ROOT = pathlib.Path(__file__).parent.parent.parent
EXAMPLES_HW6 = ROOT / "examples" / "hw6"


def configure_python_path():
    python_path = os.getenv("PYTHONPATH")

    if python_path is None:
        os.environ["PYTHONPATH"] = str(ROOT)
    else:
        os.environ["PYTHONPATH"] += ";" + str(ROOT)
    print("Configure python path: ", os.getenv("PYTHONPATH"))


def main():
    configure_python_path()

    sharded_test = EXAMPLES_HW6 / "hw6_sharded_table_stresstest.py"
    hash_test = EXAMPLES_HW6 / "hw6_hash_table_stresstest.py"

    subprocess.check_call(["python", str(sharded_test)])
    subprocess.check_call(["python", str(hash_test)])


if __name__ == "__main__":
    main()
