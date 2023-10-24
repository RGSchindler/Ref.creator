import os 
import logging
import pandas as pd 
import preprocessing
import assemble



logging.basicConfig(format="%(asctime)s | %(levelname)8s | %(message)s", level=logging.INFO)

def validate_input() -> tuple[pd.DataFrame]:
    ''' Check if the required files and folders exist. '''
    if not os.path.exists("input/IndexCombination.tsv"):
        raise FileNotFoundError("IndexCombination.tsv does not exist")
    elif not os.path.exists("input/input.fastq.gz"):
        raise FileNotFoundError("input.fastq.gz does not exist")

    logging.info("Correct files where provided.")
    idx_df = pd.read_csv("input/IndexCombination.tsv", sep="\t")
    return idx_df


def main() -> None:
    idx_df = validate_input()
    
    logging.info("Start preprocessing...")
    preprocessing.Preprocessing(idx_df)

    for sample_id in idx_df.SampleID: 
        logging.info(f"Starting the assembly of {sample_id}")
        assemble.Assemble(sample_id)

if __name__ == "__main__":
    main()