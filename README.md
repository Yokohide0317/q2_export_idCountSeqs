# q2_export_idCountSeqs
Qiime2の出力ファイルから、サンプルごとの代表配列情報を出力する。

## 出力例
count_tsv/<サンプル名>_counts.tsv

| ID | count | Seq |
| --- | --- | --- |
| abcdef...v0123456789 | 39 | ATGC.... |
| String | int | String |
| ... | ... | ... |

## 準備
```Bash
conda activate qiime2-yyyy.mm
conda install biopython

git clone https://github.com/Yokohide0317/q2_export_idCountSeqs.git
cd q2_export_idCountSeqs/
```

## 使い方
```Bash
# ex.
python export_count_tsv.py \
    -t test/table-dada2.qza \
    -r test/rep-seqs-dada2.qza
```

### Other usage
```bash
python export_count_tsv.py --help
usage: export_count_tsv.py [-h] [-t TABLE] [-r REPSEQ] [-o OUTPUT]

optional arguments:
  -h, --help            show this help message and exit
  -t TABLE, --table TABLE
  -r REPSEQ, --repseq REPSEQ
  -o OUTPUT, --output OUTPUT
```