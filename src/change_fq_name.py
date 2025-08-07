import argparse
import logging
import os.path
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Dict, DefaultDict, List, OrderedDict


def read_metadata(meta: str) -> Dict[str, str]:
    assert os.path.isfile(meta), "{meta} is not found."
    # meta file looks like this
    # run_accession	sample_title
    # ERR7459269	5207STDY7327712
    # ERR7459271	5207STDY7327710
    # ERR7459280	5207STDY7327697

    res_dict: Dict = dict()
    # key: accession, val : sample name
    with open(meta) as fin:
        fin.readline()
        for line in fin:
            accession: str = line.split()[0]
            sample_name: str = line.split()[1]
            res_dict[accession] = sample_name

    return res_dict


def get_fq_path(fastq_dir: str) -> Dict[str, List[str]]:
    """
    :param fastq_dir:
    :return: result_dict: key - file_name, value - relative_file_path
    """
    result_dict: DefaultDict[str, List[str]] = defaultdict(list)

    assert os.path.isdir(fastq_dir), f"{fastq_dir} is not found!"

    for parent_dir, sub_dir, files in os.walk(fastq_dir):
        for fq in files:
            if fq.endswith("fastq.gz"):
                abs_path: str = os.path.join(parent_dir, fq)
                assert os.path.isfile(abs_path), f"{abs_path} is not valid!"

                # get the prefix of the name of fastq files
                file_name: str = re.sub("_S[\d]+_L00[1-4]_[IR][1-3]_00[1-2].fastq.gz", "", fq)

                if file_name.endswith("fastq.gz"):
                    file_name: str = re.sub("_[IR][1-3].fastq.gz", "", fq)
                    result_dict[file_name].append(abs_path)
                else:
                    result_dict[file_name].append(abs_path)

    return result_dict


def generate_rename_fq_dict(acc_id_samp_name_dict: Dict[str, str], fastq_dict: Dict[str, List[str]]) -> OrderedDict[
    str, str]:
    result_dict: OrderedDict[str, str] = OrderedDict()

    for acc_id in acc_id_samp_name_dict:
        if acc_id in fastq_dict:
            sample_name: str = acc_id_samp_name_dict.get(acc_id)

            fq_file_list: List[str] = fastq_dict.get(acc_id)
            for fq_path in fq_file_list:
                fq_dir_name: str = os.path.dirname(fq_path)
                fq_basename: str = os.path.basename(fq_path)
                new_fq_basename: str = fq_basename.replace(acc_id, sample_name)
                final_new_fq_path: str = os.path.join(fq_dir_name, new_fq_basename)

                result_dict[fq_path] = final_new_fq_path
        else:
            print(f"{acc_id} is not found in the name of the fastq files")

    return result_dict


def rename_fq(fq_path_dict: Dict):
    for ori_path in fq_path_dict:
        new_path: str = fq_path_dict.get(ori_path)
        logging.info(f"rename {ori_path} -> {new_path}")
        os.rename(ori_path, new_path)


def main():
    args = get_args()
    meta: str = args.meta
    fastq_dir: str = args.fq_path
    meta_dict: Dict = read_metadata(meta)
    fq_path_dict: Dict = get_fq_path(fastq_dir)
    rename_dict: Dict = generate_rename_fq_dict(meta_dict, fq_path_dict)
    rename_fq(rename_dict)


@dataclass
class Args:
    meta: str
    fq_path: str


def get_args() -> Args:
    parser = argparse.ArgumentParser(
        description="rename fastq files - [sample_id]_[sample_name]...fastq.gz",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument(
        "-m",
        "--meta",
        help="meta_path",
        metavar="meta",
        type=str,
        required=True,
    )

    parser.add_argument(
        "-fq",
        "--fq_path",
        help="fastq_path",
        metavar="fq_path",
        type=str,
        required=True,
    )

    args = parser.parse_args()
    return Args(args.meta, args.fq_path)


if __name__ == '__main__':
    main()
