import argparse
import sys
import os
import zipfile
import tarfile
import io
from obfuscator import Obfuscator

def obfuscate_code(code_str: str, level: str) -> str:
    obf = Obfuscator(code_str, level)
    result = obf.obfuscate()
    if level == "hardcore" and "_environment_scope" in result:
        result = "builtins = __import__('builtins')\nsetattr(builtins, '_environment_scope', None)\n" + result
    return result

def process_zip(input_path: str, output_path: str, level: str):
    with zipfile.ZipFile(input_path, 'r') as zip_in:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zip_out:
            for name in zip_in.namelist():
                content = zip_in.read(name)
                if name.endswith(".py") and not name.startswith("__MACOSX"):
                    try:
                        code = content.decode("utf-8")
                        obfuscated = obfuscate_code(code, level)
                        zip_out.writestr(name, obfuscated)
                    except Exception as e:
                        print(f"Skipping obfuscation for {name} due to: {e}", file=sys.stderr)
                        zip_out.writestr(name, content)
                else:
                    zip_out.writestr(name, content)

def process_tar(input_path: str, output_path: str, level: str):
    with tarfile.open(input_path, 'r:gz') as tar_in:
        with tarfile.open(output_path, 'w:gz') as tar_out:
            for member in tar_in.getmembers():
                f_obj = tar_in.extractfile(member)
                if f_obj and member.name.endswith(".py"):
                    try:
                        content = f_obj.read()
                        code = content.decode("utf-8")
                        obfuscated_code = obfuscate_code(code, level).encode("utf-8")
                        tarinfo = tarfile.TarInfo(name=member.name)
                        tarinfo.size = len(obfuscated_code)
                        tarinfo.mode = member.mode
                        tar_out.addfile(tarinfo, io.BytesIO(obfuscated_code))
                    except Exception:
                        tar_out.addfile(member, f_obj)
                else:
                    tar_out.addfile(member, f_obj)

def main():
    parser = argparse.ArgumentParser(description="Obfuscator sandbox runner")
    parser.add_argument("--input", required=True, help="Path to input file")
    parser.add_argument("--output", required=True, help="Path to output file")
    parser.add_argument("--level", required=True, choices=["basic", "standard", "hardcore"], help="Obfuscation level")
    
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    filename = os.path.basename(args.input)

    try:
        if filename.endswith(".py") or args.input.endswith("input_script.py"):
            with open(args.input, "r", encoding="utf-8") as f:
                code = f.read()
            obfuscated = obfuscate_code(code, args.level)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(obfuscated)
        elif filename.endswith(".zip") or ".zip" in filename:
            process_zip(args.input, args.output, args.level)
        elif filename.endswith(".tar.gz") or ".tar.gz" in filename:
            process_tar(args.input, args.output, args.level)
        else:
            print(f"Unsupported file format for {filename}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Execution error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()