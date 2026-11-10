import argparse
import struct
import sys
import zipfile
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_PNG_BYTES = 200_000


def png_size(data):
    if data[:8] != PNG_SIGNATURE or data[12:16] != b"IHDR":
        raise ValueError("not a PNG")
    return struct.unpack(">II", data[16:24])


def extract_skin(zip_path, destination_body_folder):
    destination = Path(destination_body_folder)
    destination.mkdir(parents=True, exist_ok=True)
    written = []
    with zipfile.ZipFile(zip_path) as archive:
        for info in archive.infolist():
            parts = info.filename.split("/")
            if info.is_dir() or ".." in parts or info.filename.startswith("/"):
                continue
            if len(parts) < 2 or parts[-2] != "Body" or not parts[-1].lower().endswith(".png"):
                print("skipped", info.filename)
                continue
            if info.file_size > MAX_PNG_BYTES:
                raise ValueError("%s is %d bytes" % (info.filename, info.file_size))
            data = archive.read(info)
            width, height = png_size(data)
            target = destination / parts[-1]
            target.write_bytes(data)
            written.append((parts[-1], width, height))
    return written


def main():
    parser = argparse.ArgumentParser(description="Extract only Body/*.png from a portal skin zip")
    parser.add_argument("zip_path")
    parser.add_argument("destination_body_folder")
    arguments = parser.parse_args()
    for name, width, height in extract_skin(arguments.zip_path, arguments.destination_body_folder):
        print("%-40s %dx%d" % (name, width, height))
    return 0


if __name__ == "__main__":
    sys.exit(main())
