import pandas as pd
import subprocess
import sys
import argparse
from pathlib import Path
import os
import shutil

from Bio import SeqIO
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExportMain():

    def __init__(self, args):
        self.tmp_path = Path("./tmp_q2_export_idCountSeqs/")
        self.table_path = Path(args.table)
        self.rep_seq_path = Path(args.repseq)
        self.output_path = Path(args.output)
        return

    # Terminalを実行
    def exec_terminal(self, _cmd):
        logger.info(" ".join(_cmd))
        res = subprocess.run(_cmd, capture_output=True)
        if res.returncode != 0:
            # エラーが発生すれば終了する。
            logger.error("captured stderr: {}".format(res.stderr.decode()))
            sys.exit()
        else:
            logger.info(res.stdout.decode())
        return

    def save_count_tsv(self, _df: pd.DataFrame, _colname):
        _df = _df.copy()
        _df = _df[["ID", _colname, "Seq"]]
        _df = _df.rename({_colname: "count"}, axis=1)
        _df.to_csv(str(self.output_path/f"{_colname}_counts.tsv"), sep="\t", index=False, header=True)
        return


    def ready_source_file(self):

        cmd = ["qiime", "tools", "export", 
               "--input-path", str(self.rep_seq_path),
               "--output-path", str(self.tmp_path/"rep_seq")]
        self.exec_terminal(cmd)

        cmd = ["qiime", "tools", "export", 
               "--input-path", str(self.table_path),
               "--output-path", str(self.tmp_path/"table")]
        self.exec_terminal(cmd)

        cmd = ["biom", "convert", 
               "-i", str(self.tmp_path/'table'/'feature-table.biom'),
               "-o", str(self.tmp_path/'feature-table.biom.tsv'),
               "--to-tsv"]
        self.exec_terminal(cmd)
        return

    def get_source_df(self):
        biom = pd.read_csv(str(self.tmp_path/"feature-table.biom.tsv"), sep="\t", header=1)

        # DNA配列の抽出->Pandas
        dna_fasta_path = str(self.tmp_path/"rep_seq"/"dna-sequences.fasta")

        fasta_list = []

        for record in SeqIO.parse(dna_fasta_path, 'fasta'):
            desc_part = record.description
            seq = record.seq
            fasta_list.append([desc_part, str(seq)])

        seq_df = pd.DataFrame(fasta_list, columns=["ID", "Seq"])

        # 情報をマージ
        self.merged_df = biom.merge(seq_df, how="inner", left_on="#OTU ID", right_on="ID").drop("#OTU ID", axis=1)
        self.sample_names = [col for col in self.merged_df.columns if col not in ["ID", "Seq"]]
        logger.info(f"Samples: {', '.join(self.sample_names)}")
        return


    def pipeMain(self):
        if not self.tmp_path.is_dir():
            os.mkdir(self.tmp_path)

        if not self.output_path.is_dir():
            os.mkdir(self.output_path)

        self.ready_source_file()
        self.get_source_df()

        for colname in self.sample_names:
            self.save_count_tsv(self.merged_df, colname)
        logger.info(f"Saved to: {str(self.output_path)}")

        shutil.rmtree(self.tmp_path)
        return



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--table")
    parser.add_argument("-r", "--repseq")
    parser.add_argument("-o", "--output", default="./count_tsv")

    args = parser.parse_args()
    exportMain = ExportMain(args)
    exportMain.pipeMain()


