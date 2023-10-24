import os 
import logging
from dataclasses import dataclass, field

import process


logger = logging.getLogger(__name__)

@dataclass
class Assemble:
    sample_id: str
    
    fastq_path: str = field(init=False)
    mapping_file: str = field(init=False)
    asm_raw_file: str = field(init=False)
    asm_polished: str = field(init=False)
    asm_fasta: str = field(init=False)


    def __post_init__(self) -> None:
        out_path = f"{os.getcwd()}/input/output/{self.sample_id}"

        self.fastq_path = f"{out_path}/{self.sample_id}.fastq"
        self.mapping_file = f"{out_path}/self_mapping.paf"
        self.asm_raw_file = f"{out_path}/raw_assembly.gfa"
        self.asm_polished = f"{out_path}/cleaned_assembly.gfa"
        self.asm_fasta = f"{out_path}/{self.sample_id}.fasta"

        self.self_align()
        self.assemble()
        self.polish()
        self.extract_sequence()

        logger.info(f"Finished processing {self.sample_id}")


    def self_align(self) -> None:
        '''
        Find overlaps between long reads using the ordinary minimizers for ONT 
        '''
        logger.info(f"Self aligning {self.sample_id}")
        process.run(f"/root/miniconda3/envs/minimap2/bin/minimap2 -x ava-ont {self.fastq_path} {self.fastq_path} > {self.mapping_file}", chained=False)
        logger.info(f"Finished aligning {self.sample_id}")

    
    def assemble(self) -> None:
        '''
        De-novo assembly using miniasm and the parameters:
            -m 100 - Drop mappings having less than 100 matching bases 
            -s 250 - Drop mappings shorter than 250bp 
        '''
        logger.info(f"De-novo assembly of {self.sample_id}")
        process.run(f"/root/miniconda3/envs/miniasm/bin/miniasm -f {self.fastq_path} {self.mapping_file} -m 100 -s 250 > {self.asm_raw_file}", chained=False)
        logger.info(f"Finished the assembly of {self.sample_id}")

    
    def polish(self) -> None:
        logger.info(f"Polishing {self.sample_id}")
        new_env = {
            "PATH" : "/root/miniconda3/envs/minimap2/bin:/root/miniconda3/envs/racon/bin"
        }
        process.run(f"/root/miniconda3/envs/minipolish/bin/minipolish  {self.fastq_path} {self.asm_raw_file} > {self.asm_polished}", chained=False, env=new_env)
        logger.info(f"Finished polishing {self.sample_id}")


    def extract_sequence(self) -> None:
        logger.info(f"Extracting finished {self.asm_fasta} assembly consensus")
        with open(self.asm_polished) as infile, open(self.asm_fasta, 'w') as outfile:
            for line in infile:
                if line.startswith('S'):
                    fields = line.strip().split()
                    outfile.write(">" + fields[1] + "\n" + fields[2] + "\n")
