projects = [{
    ################
    # Project Meta #
    ################
    "title" : "Variation of DNA methylation across diverse maize inbred lines",
    "creator" : "Nathan Springer",
    "investigation_type" : "Genomic", # eukariote
    "workflow": ["sequencing","alignment","analysis"],
    "description" : "Variation of DNA methylation across diverse maize inbred lines",
   #############
   # Specimens #
   #############
    "specimens" : [{
        ##############
        # Specimen 0 #
        ##############
        "taxon_name" :  "Zea Mays",
        "specimen_uuid" : "B73",
        "haploid_chromosomes_count" : "10",
        "ploid" : "diploid",
        "organ_tissue" : "leaf",
        "developmental_stage" : "14 days old seedling",
        "estimated_genome_size" : "2300 Mb",
        "propagation" : "selfing",
        "references" : [{
            "source" : "maizegdb",
            "reference_id" : "47638",
            "path" : "http://www.maizegdb.org/data_center/stock?id=47638"
        }],
        "processes" : [
            {
                ##############
                # Sequencing #
                ##############
                "process_type" : "sequencing",
                "sequencing_method" : "whole genome bisulfite sequencing",
                "sequencing_hardware" : "Illumina HiSeq 2000",
                "assembly_method" : "Bismark or BSMAP",
                "reference_sequence" : "Maize AGPv2",
                # "precursor_type" : "specimen",
                # "precursor_id" : 0,
                "specimen_uuid" : 0,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "B73_all3_R1_val_1.fq",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
                    "size" : "500000000",
                    "checksum" : "AD9C01BA48C64A80",
                },
                {
                    "file_name" : "B73_all3_R2_val_2.fq",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
                    "size" : "500000000",
                    "checksum" : "0DDCB17AC836DA93",
                },
                {
                    "file_name" : "SRR850328",
                    "file_type" : "fastq",
                    "system" : "SRA",
                    "id" : "SRR850328", # path?
                    "path" : "http://www.ncbi.nlm.nih.gov/sra/?term=SRR850328",
                    "size" : "500000000",
                    "checksum" : "AD9B01BA48C64A80",
                },],
            },
            {
                #############
                # Alignment #
                #############
                "process_type" : "alignment",
                # "precursor_type" : "sequencing",
                # "precursor_id" : 0,
                "specimen_uuid" : 0,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "B73_all3_bt202_sorted.bam",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/",
                    "size" : "500000000",
                    "checksum" : "94123C93EFFCD794",
                },],
            },
            {
                ############
                # Analysis #
                ############
                "process_type" : "analysis",
                "software" : "Bismark or BSMAP",
                "software_version" : "0.10.1",
                ## input file type                 trimmed FastQ
                ## additional analysis             100bp tile for CpG,CHG,CHH methylation
                ## additional analysis software    Python script
                # "precursor_type" : "alignment",
                # "precursor_id" : 0,
                "specimen_uuid" : 0,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "B73_all3_tile_merged_100bp.txt",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/100tile/",
                    "size" : "500000000",
                    "checksum" : "FC633EDB96754048",
                },],
            },
        ]
    },
    {
        ##############
        # Specimen 1 #
        ##############
        "taxon_name" :  "Zea Mays",
        "specimen_uuid" : "Mo17",
        "haploid_chromosomes_count" : "10",
        "ploid" : "diploid",
        "organ_tissue" : "leaf",
        "developmental_stage" : "14 days old seedling",
        "estimated_genome_size" : "2300 Mb",
        "propagation" : "selfing",
        "references" : [{
            "source" : "maizegdb",
            "reference_id" : "47846",
            "path" : "http://www.maizegdb.org/data_center/stock?id=47846"
        }],
        "processes" : [
            {
                ##############
                # Sequencing #
                ##############
                "process_type" : "sequencing",
                "sequencing_method" : "whole genome bisulfite sequencing",
                "sequencing_hardware" : "Illumina HiSeq 2000",
                "assembly_method" : "Bismark or BSMAP",
                "reference_sequence" : "Maize AGPv2",
                "specimen_uuid" : 1,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "Mo17_all3_R1_val_1.fq",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
                    "size" : "500000000",
                    "checksum" : "1743A0C6CA75F6D1",
                },
                {
                    "file_name" : "Mo17_all3_R1_val_2.fq",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
                    "size" : "500000000",
                    "checksum" : "6F985E9CD7B94519",
                },
                {
                    "file_name" : "SRR850332",
                    "file_type" : "fastq",
                    "system" : "SRA",
                    "id" : "SRR850332", # path?
                    "path" : "http://www.ncbi.nlm.nih.gov/sra/?term=SRR850332",
                    "size" : "500000000",
                    "checksum" : "1743A0C6CA75F6D1",
                },],
            },
            {
                #############
                # Alignment #
                #############
                "process_type" : "alignment",
                "specimen_uuid" : 1,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "Mo17_all3_bt202_sorted.bam",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/",
                    "size" : "500000000",
                    "checksum" : "11ABF54D5B011A2C",
                },],
            },
            {
                ############
                # Analysis #
                ############
                "process_type" : "analysis",
                "software" : "Bismark or BSMAP",
                "software_version" : "0.10.1",
                "specimen_uuid" : 1,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "100tile/Mo17_all3_tile_merged_100bp.txt",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/100tile/",
                    "size" : "500000000",
                    "checksum" : "C06DAAC217DFC2C9",
                },],
            },
        ],
    },
    {
        ##############
        # Specimen 2 #
        ##############
        "taxon_name" :  "Zea Mays",
        "specimen_uuid" : "CML322",
        "haploid_chromosomes_count" : "10",
        "ploid" : "diploid",
        "organ_tissue" : "leaf",
        "developmental_stage" : "14 days old seedling",
        "estimated_genome_size" : "2300 Mb",
        "propagation" : "selfing",
        "references" : [{
            "source" : "maizegdb",
            "reference_id" : "106308",
            "path" : "http://www.maizegdb.org/data_center/stock?id=106308"
        }],
        "processes" : [
            {
                ##############
                # Sequencing #
                ##############
                "process_type" : "sequencing",
                "sequencing_method" : "whole genome bisulfite sequencing",
                "sequencing_hardware" : "Illumina HiSeq 2000",
                "assembly_method" : "Bismark or BSMAP",
                "reference_sequence" : "Maize AGPv2",
                "specimen_uuid" : 2,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "CML322_R1.allreads_val_1.fq",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
                    "size" : "500000000",
                    "checksum" : "24A646BFBC07D6A3",
                },
                {
                    "file_name" : "CML322_R1.allreads_val_2.fq",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
                    "size" : "500000000",
                    "checksum" : "76A47D3715E3AB47",
                },
                {
                    "file_name" : "SRX731432",
                    "file_type" : "fastq",
                    "system" : "SRA",
                    "id" : "SRX731432", # path?
                    "path" : "http://www.ncbi.nlm.nih.gov/sra/?term=SRX731432",
                    "size" : "500000000",
                    "checksum" : "24A646BFBC07D6A3",
                },],
            },
            {
                #############
                # Alignment #
                #############
                "process_type" : "alignment",
                "specimen_uuid" : 2,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "CML322_all3_bt202_sorted.bam",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/",
                    "size" : "500000000",
                    "checksum" : "4C9D1495AFBB62AF",
                },],
            },
            {
                ############
                # Analysis #
                ############
                "process_type" : "analysis",
                "software" : "Bismark or BSMAP",
                "software_version" : "0.10.1",
                "specimen_uuid" : 2,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "CML322_all3_tile_merged_100bp.txt",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/100tile/",
                    "size" : "500000000",
                    "checksum" : "9B58A1852F381D33",
                },],
            },
        ],
    },
    {
        ##############
        # Specimen 3 #
        ##############
        "taxon_name" :  "Zea Mays",
        "specimen_uuid" : "Oh43",
        "haploid_chromosomes_count" : "10",
        "ploid" : "diploid",
        "organ_tissue" : "leaf",
        "developmental_stage" : "14 days old seedling",
        "estimated_genome_size" : "2300 Mb",
        "propagation" : "selfing",
        "references" : [{
            "source" : "maizegdb",
            "reference_id" : "47888",
            "path" : "http://www.maizegdb.org/data_center/stock?id=47888"
        }],
        "processes" : [
            {
                ##############
                # Sequencing #
                ##############
                "process_type" : "sequencing",
                "sequencing_method" : "whole genome bisulfite sequencing",
                "sequencing_hardware" : "Illumina HiSeq 2000",
                "assembly_method" : "Bismark or BSMAP",
                "reference_sequence" : "Maize AGPv2",
                "specimen_uuid" : 3,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "Oh43_R1.allreads_val_1.fq",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
                    "size" : "500000000",
                    "checksum" : "A97E8BDFF4897C22",
                },
                {
                    "file_name" : "Oh43_R1.allreads_val_2.fq",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
                    "size" : "500000000",
                    "checksum" : "2EECF586F48C80DE",
                },
                {
                    "file_name" : "SRX731433",
                    "file_type" : "fastq",
                    "system" : "SRA",
                    "id" : "SRX731433", # path?
                    "path" : "http://www.ncbi.nlm.nih.gov/sra/?term=SRX731433",
                    "size" : "500000000",
                    "checksum" : "A97E8BDFF4897C22",
                },],
            },
            {
                #############
                # Alignment #
                #############
                "process_type" : "alignment",
                "specimen_uuid" : 3,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "Oh43_all3_bt202_sorted.bam",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/",
                    "size" : "500000000",
                    "checksum" : "9CFDBAFC9770E434",
                },],
            },
            {
                ############
                # Analysis #
                ############
                "process_type" : "analysis",
                "software" : "Bismark or BSMAP",
                "software_version" : "0.10.1",
                "specimen_uuid" : 3,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "Oh43_all3_tile_merged_100bp.txt",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/100tile/",
                    "size" : "500000000",
                    "checksum" : "F89DB28D6E190DEB",
                },],
            },
        ]
    },
    {
        ##############
        # Specimen 4 #
        ##############
        "taxon_name" :  "Zea Mays",
        "specimen_uuid" : "Tx303",
        "haploid_chromosomes_count" : "10",
        "ploid" : "diploid",
        "organ_tissue" : "leaf",
        "developmental_stage" : "14 days old seedling",
        "estimated_genome_size" : "2300 Mb",
        "propagation" : "selfing",
        "references" : [{
            "source" : "maizegdb",
            "reference_id" : "17166",
            "path" : "http://www.maizegdb.org/data_center/stock?id=17166"
        }],
        "processes" : [
            {
                ##############
                # Sequencing #
                ##############
                "process_type" : "sequencing",
                "sequencing_method" : "whole genome bisulfite sequencing",
                "sequencing_hardware" : "Illumina HiSeq 2000",
                "assembly_method" : "Bismark or BSMAP",
                "reference_sequence" : "Maize AGPv2",
                "specimen_uuid" : 4,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "Tx303_R1.allreads_val_1.fq",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
                    "size" : "500000000",
                    "checksum" : "65FB1A2D9C546D33",
                },
                {
                    "file_name" : "Tx303_R1.allreads_val_2.fq",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
                    "size" : "500000000",
                    "checksum" : "AF441F416387D55A",
                },
                {
                    "file_name" : "SRX731434",
                    "file_type" : "fastq",
                    "system" : "SRA",
                    "id" : "SRX731434", # path?
                    "path" : "http://www.ncbi.nlm.nih.gov/sra/?term=SRX731434",
                    "size" : "500000000",
                    "checksum" : "65FB1A2D9C546D33",
                },],
            },
            {
                #############
                # Alignment #
                #############
                "process_type" : "alignment",
                "specimen_uuid" : 4,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "Tx303_all3_bt202_sorted.bam",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/",
                    "size" : "500000000",
                    "checksum" : "2E352C9C6C9F399E",
                },],
            },
            {
                ############
                # Analysis #
                ############
                "process_type" : "analysis",
                "software" : "Bismark or BSMAP",
                "software_version" : "0.10.1",
                "specimen_uuid" : 4,
                "inputs" : None,
                "outputs" : [{
                    "file_name" : "Tx303_all3_tile_merged_100bp.txt",
                    "system" : "corral",
                    "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/100tile/",
                    "size" : "500000000",
                    "checksum" : "16C286EA0B07BDFB",
                },],
            },
        ]
    },],
    #############
    # Processes #
    #############
    "processes" : [{
        ##############
        # Sequencing #
        ##############
        "process_type" : "sequencing",
        "sequencing_method" : "whole genome bisulfite sequencing",
        "sequencing_hardware" : "Illumina HiSeq 2000",
        "assembly_method" : "Bismark or BSMAP",
        "reference_sequence" : "Maize AGPv2",
        # "precursor_type" : "specimen",
        # "precursor_id" : 0,
        "specimen_uuid" : 0,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "B73_all3_R1_val_1.fq",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
            "size" : "500000000",
            "checksum" : "AD9C01BA48C64A80",
        },
        {
            "file_name" : "B73_all3_R2_val_2.fq",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
            "size" : "500000000",
            "checksum" : "0DDCB17AC836DA93",
        },
        {
            "file_name" : "SRR850328",
            "file_type" : "fastq",
            "system" : "SRA",
            "id" : "SRR850328", # path?
            "path" : "http://www.ncbi.nlm.nih.gov/sra/?term=SRR850328",
            "size" : "500000000",
            "checksum" : "AD9B01BA48C64A80",
        },],
    },
    {
        ##############
        # Sequencing #
        ##############
        "process_type" : "sequencing",
        "sequencing_method" : "whole genome bisulfite sequencing",
        "sequencing_hardware" : "Illumina HiSeq 2000",
        "assembly_method" : "Bismark or BSMAP",
        "reference_sequence" : "Maize AGPv2",
        "specimen_uuid" : 1,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "Mo17_all3_R1_val_1.fq",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
            "size" : "500000000",
            "checksum" : "1743A0C6CA75F6D1",
        },
        {
            "file_name" : "Mo17_all3_R1_val_2.fq",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
            "size" : "500000000",
            "checksum" : "6F985E9CD7B94519",
        },
        {
            "file_name" : "SRR850332",
            "file_type" : "fastq",
            "system" : "SRA",
            "id" : "SRR850332", # path?
            "path" : "http://www.ncbi.nlm.nih.gov/sra/?term=SRR850332",
            "size" : "500000000",
            "checksum" : "1743A0C6CA75F6D1",
        },],
    },
    {
        ##############
        # Sequencing #
        ##############
        "process_type" : "sequencing",
        "sequencing_method" : "whole genome bisulfite sequencing",
        "sequencing_hardware" : "Illumina HiSeq 2000",
        "assembly_method" : "Bismark or BSMAP",
        "reference_sequence" : "Maize AGPv2",
        "specimen_uuid" : 2,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "CML322_R1.allreads_val_1.fq",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
            "size" : "500000000",
            "checksum" : "24A646BFBC07D6A3",
        },
        {
            "file_name" : "CML322_R1.allreads_val_2.fq",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
            "size" : "500000000",
            "checksum" : "76A47D3715E3AB47",
        },
        {
            "file_name" : "SRX731432",
            "file_type" : "fastq",
            "system" : "SRA",
            "id" : "SRX731432", # path?
            "path" : "http://www.ncbi.nlm.nih.gov/sra/?term=SRX731432",
            "size" : "500000000",
            "checksum" : "24A646BFBC07D6A3",
        },],
    },
    {
        ##############
        # Sequencing #
        ##############
        "process_type" : "sequencing",
        "sequencing_method" : "whole genome bisulfite sequencing",
        "sequencing_hardware" : "Illumina HiSeq 2000",
        "assembly_method" : "Bismark or BSMAP",
        "reference_sequence" : "Maize AGPv2",
        "specimen_uuid" : 3,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "Oh43_R1.allreads_val_1.fq",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
            "size" : "500000000",
            "checksum" : "A97E8BDFF4897C22",
        },
        {
            "file_name" : "Oh43_R1.allreads_val_2.fq",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
            "size" : "500000000",
            "checksum" : "2EECF586F48C80DE",
        },
        {
            "file_name" : "SRX731433",
            "file_type" : "fastq",
            "system" : "SRA",
            "id" : "SRX731433", # path?
            "path" : "http://www.ncbi.nlm.nih.gov/sra/?term=SRX731433",
            "size" : "500000000",
            "checksum" : "A97E8BDFF4897C22",
        },],
    },
    {
        ##############
        # Sequencing #
        ##############
        "process_type" : "sequencing",
        "sequencing_method" : "whole genome bisulfite sequencing",
        "sequencing_hardware" : "Illumina HiSeq 2000",
        "assembly_method" : "Bismark or BSMAP",
        "reference_sequence" : "Maize AGPv2",
        "specimen_uuid" : 4,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "Tx303_R1.allreads_val_1.fq",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
            "size" : "500000000",
            "checksum" : "65FB1A2D9C546D33",
        },
        {
            "file_name" : "Tx303_R1.allreads_val_2.fq",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/5genos/",
            "size" : "500000000",
            "checksum" : "AF441F416387D55A",
        },
        {
            "file_name" : "SRX731434",
            "file_type" : "fastq",
            "system" : "SRA",
            "id" : "SRX731434", # path?
            "path" : "http://www.ncbi.nlm.nih.gov/sra/?term=SRX731434",
            "size" : "500000000",
            "checksum" : "65FB1A2D9C546D33",
        },],
    },
    {
        #############
        # Alignment #
        #############
        "process_type" : "alignment",
        # "precursor_type" : "sequencing",
        # "precursor_id" : 0,
        "specimen_uuid" : 0,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "B73_all3_bt202_sorted.bam",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/",
            "size" : "500000000",
            "checksum" : "94123C93EFFCD794",
        },],
    },
    {
        #############
        # Alignment #
        #############
        "process_type" : "alignment",
        "specimen_uuid" : 1,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "Mo17_all3_bt202_sorted.bam",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/",
            "size" : "500000000",
            "checksum" : "11ABF54D5B011A2C",
        },],
    },
    {
        #############
        # Alignment #
        #############
        "process_type" : "alignment",
        "specimen_uuid" : 2,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "CML322_all3_bt202_sorted.bam",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/",
            "size" : "500000000",
            "checksum" : "4C9D1495AFBB62AF",
        },],
    },
    {
        #############
        # Alignment #
        #############
        "process_type" : "alignment",
        "specimen_uuid" : 3,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "Oh43_all3_bt202_sorted.bam",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/",
            "size" : "500000000",
            "checksum" : "9CFDBAFC9770E434",
        },],
    },
    {
        #############
        # Alignment #
        #############
        "process_type" : "alignment",
        "specimen_uuid" : 4,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "Tx303_all3_bt202_sorted.bam",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/",
            "size" : "500000000",
            "checksum" : "2E352C9C6C9F399E",
        },],
    },
    {
        ############
        # Analysis #
        ############
        "process_type" : "analysis",
        "software" : "Bismark or BSMAP",
        "software_version" : "0.10.1",
        ## input file type                 trimmed FastQ
        ## additional analysis             100bp tile for CpG,CHG,CHH methylation
        ## additional analysis software    Python script
        # "precursor_type" : "alignment",
        # "precursor_id" : 0,
        "specimen_uuid" : 0,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "B73_all3_tile_merged_100bp.txt",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/100tile/",
            "size" : "500000000",
            "checksum" : "FC633EDB96754048",
        },],
    },
    {
        ############
        # Analysis #
        ############
        "process_type" : "analysis",
        "software" : "Bismark or BSMAP",
        "software_version" : "0.10.1",
        "specimen_uuid" : 1,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "100tile/Mo17_all3_tile_merged_100bp.txt",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/100tile/",
            "size" : "500000000",
            "checksum" : "C06DAAC217DFC2C9",
        },],
    },
    {
        ############
        # Analysis #
        ############
        "process_type" : "analysis",
        "software" : "Bismark or BSMAP",
        "software_version" : "0.10.1",
        "specimen_uuid" : 2,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "CML322_all3_tile_merged_100bp.txt",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/100tile/",
            "size" : "500000000",
            "checksum" : "9B58A1852F381D33",
        },],
    },
    {
        ############
        # Analysis #
        ############
        "process_type" : "analysis",
        "software" : "Bismark or BSMAP",
        "software_version" : "0.10.1",
        "specimen_uuid" : 3,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "Oh43_all3_tile_merged_100bp.txt",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/100tile/",
            "size" : "500000000",
            "checksum" : "F89DB28D6E190DEB",
        },],
    },
    {
        ############
        # Analysis #
        ############
        "process_type" : "analysis",
        "software" : "Bismark or BSMAP",
        "software_version" : "0.10.1",
        "specimen_uuid" : 4,
        "inputs" : None,
        "outputs" : [{
            "file_name" : "Tx303_all3_tile_merged_100bp.txt",
            "system" : "corral",
            "path" : "/corral-tacc/tacc/iplant/vaughn/springer_vaughn/eichten/jawon/10-01-13_5genos/100tile/",
            "size" : "500000000",
            "checksum" : "16C286EA0B07BDFB",
        },],
    },]
}]
