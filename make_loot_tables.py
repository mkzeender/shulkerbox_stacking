import json
from os import listdir, path
from typing import Callable


def apply_to_jsons(src_dir: str, dest_dir: str, func: Callable[[dict], None]):
    for fp in listdir(src_dir):
        with open(path.join(src_dir, fp), "r") as f:
            table = json.load(f)

        func(table)

        with open(path.join(dest_dir, fp), "w") as f:
            json.dump(table, f, indent=2)


def make_loot(table: dict):
    funcs: list = table["pools"][0]["entries"][0]["functions"]

    funcs.append(
        {
            "function": "minecraft:set_components",
            "components": {"minecraft:max_stack_size": 64},
        }
    )


def main():
    apply_to_jsons(
        "./vanilla/new_blocks", "./data/minecraft/loot_tables/blocks", make_loot
    )


if __name__ == "__main__":
    main()
