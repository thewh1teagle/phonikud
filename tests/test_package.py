from pathlib import Path


def test_has_no_breakpoint():
    files = Path(__file__).parent.joinpath("../phonikud").resolve().glob("**/*.py")
    for file in files:
        print(file)

        with open(file, "r", encoding="utf-8") as f:
            content = f.readlines()
        for line_number, line in enumerate(content, 1):
            if "breakpoint()" in line:
                print(f"Error in {file}:{line_number} - 'breakpoint()' found")
                assert False, f"Error in {file}:{line_number} - 'breakpoint()' found"
