#!/usr/bin/python3
#
#  PROGRAM: fs_to_graph.py
#
#  PURPOSE: Walk the bulk of the Linux file system tree and create a simple CSV of parent,child,1.0 (sub-dir)
#           or source,target,0.5 (sym-link) for most of the file system tree.  Ignoring the things that caused
#           problems even when it was run as root.
#
#  DATE:    August 11, 2025
#
#  AUTHOR:  Christopher Petersen
#
from pathlib import *
from sys import exit


def descend_recursively(p_root: Path) -> None:
    l_ignore_list: list[Path] = [Path('/proc'), Path('/sys'), Path('/run'), Path('/var/run')]
    l_subdirs: list[Path] = [x for x in p_root.iterdir() if x.is_dir()]
    l_symlinks: list[Path] = [x for x in p_root.iterdir() if x.is_symlink()]

    for l_subdir in l_subdirs:
        if l_subdir not in l_symlinks:
            print(f'"{p_root}","{p_root / l_subdir}",1.0')
            if ((p_root / l_subdir) not in l_ignore_list):
                descend_recursively(p_root / l_subdir)

    for l_symlink in l_symlinks:
        l_symlink_path: Path = p_root.joinpath(l_symlink.readlink()).resolve()
        if l_symlink_path.is_dir() and (l_symlink_path not in l_ignore_list):
            print(f'"{p_root}","{p_root / l_symlink}",1.0')         #  Need this to avoid multiple zero in-coming Vertex
            print(f'"{p_root / l_symlink}","{l_symlink_path}",0.5')
            descend_recursively(l_symlink_path)

    return


def main() -> None:
    print(f'From,To,Length')
    descend_recursively(Path('/'))


if __name__ == '__main__':
    main()
    exit(0)