from dataclasses import dataclass, asdict
import json
import logging
import os
from os import path
import shutil
from typing import Iterable
from zipfile import ZipFile

ASSETS_OUT = "resources.zip"
DATA_OUT = "{datapack_name}.zip"


@dataclass
class BuildInfo:
    datapack_name: str
    description: str
    data_version: int
    resource_version: int
    world_dirs: list[str]


with open("build.json", "r") as f:
    BUILD_INFO = BuildInfo(**json.load(f))


def add_folder_to_zip(zip_file: ZipFile, folder: str):
    for file in os.listdir(folder):
        full_path = path.join(folder, file)
        if path.isfile(full_path):
            if path.splitext(full_path)[1] != "py":
                logging.info("File added: " + str(full_path))
                zip_file.write(full_path)
            else:
                logging.info(f"File skipped: {full_path}")

        elif path.isdir(full_path):
            logging.debug("Entering folder: " + str(full_path))
            add_folder_to_zip(zip_file, full_path)


def write_zip(fp: str, is_resources: bool = False):
    if is_resources:
        dir_path = "assets"
        pack_meta = {
            "pack": {
                "description": BUILD_INFO.description,
                "pack_format": BUILD_INFO.resource_version,
            }
        }
    else:
        dir_path = "data"
        pack_meta = {
            "pack": {
                "description": BUILD_INFO.description,
                "pack_format": BUILD_INFO.data_version,
            }
        }

    with ZipFile(fp, "w") as f:
        f.writestr("pack.mcmeta", json.dumps(pack_meta))

        add_folder_to_zip(f, dir_path)


def copy_file(source: str, dests: Iterable[str], *extra: str):
    for dest in dests:
        shutil.copyfile(source, path.join(dest, *extra))


def main():
    logging.basicConfig(level=logging.DEBUG)
    try:
        os.mkdir("./build")
    except FileExistsError:
        pass

    assets_fp = "./build/" + ASSETS_OUT.format(**asdict(BUILD_INFO))
    dat_name = DATA_OUT.format(**asdict(BUILD_INFO))
    data_fp = "./build/" + dat_name

    if path.exists("./assets"):
        logging.info("Creating Assets...")

        write_zip(assets_fp, True)

        logging.info(f"Copying assets to {len(BUILD_INFO.world_dirs)} world folders")
        copy_file(assets_fp, BUILD_INFO.world_dirs, "resources.zip")

    else:
        logging.info("No assets folder, skipping")

    if path.exists("./data"):
        logging.info(f"Creating datapack")
        write_zip(data_fp, False)

        logging.info(f"Copying datapack to {len(BUILD_INFO.world_dirs)} world folders")
        copy_file(data_fp, BUILD_INFO.world_dirs, "datapacks", dat_name)

    else:
        logging.info("No data folder, skipping")


if __name__ == "__main__":
    main()
