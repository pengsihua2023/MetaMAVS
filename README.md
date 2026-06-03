# MetaMAVS
MetaMAVS: A Metagenomic Multi-Agent Virus Surveillance System for Automated Viral Detection, Classification, and Epidemiological Risk Assessment
## 提示词
下面是一份可以直接复制到 **Claude Code** 里的开发提示词。它的目标是让 Claude Code 帮你从零开始设计并开发 **MetaMAVS：Metagenomic Multi-Agent Virus Surveillance System**。

---

## Claude Code 提示词

```text
You are an expert bioinformatics software architect, Python developer, and AI multi-agent system engineer.

I want to develop a research-grade software system named MetaMAVS.

Full name:
MetaMAVS: Metagenomic Multi-Agent Virus Surveillance System

Goal:
Build a multi-agent system for virus surveillance based on wastewater or environmental metagenomic sequencing data. The system should process metagenomic data, detect known and potential viral signals, classify viruses taxonomically, summarize abundance trends, and generate epidemiological warning reports.

Please help me design and implement this project step by step.

Project background:
I work on viral metagenomics, wastewater surveillance, and bioinformatics pipelines. I want MetaMAVS to combine traditional metagenomic analysis pipelines with AI multi-agent coordination. The system should eventually support virus detection, taxonomic classification, quality control, abundance analysis, trend monitoring, risk assessment, and automated report generation.

Core concept:
MetaMAVS should use multiple specialized agents. Each agent has a clear responsibility and communicates with other agents through structured messages or workflow outputs.

Please design the project architecture first, then generate code files.

Expected agents:

1. Input Manager Agent
- Accept FASTQ files, metadata files, and configuration files.
- Validate sample names, file paths, sequencing type, and metadata consistency.
- Produce a clean sample manifest.

2. Quality Control Agent
- Run or prepare commands for FastQC, fastp, MultiQC, or similar QC tools.
- Summarize read quality, adapter contamination, read length, and sequencing depth.
- Decide whether samples pass basic QC thresholds.

3. Host Removal Agent
- Remove host reads using Bowtie2, BWA, or minimap2.
- Support human, animal, or custom host reference genomes.
- Report host-read percentage and non-host read counts.

4. Viral Detection Agent
- Detect viral reads using tools such as Kraken2, KrakenUniq, Centrifuge, DIAMOND, BLAST, or RVDB-based search.
- Support both nucleotide-level and protein-level viral detection.
- Output candidate viral taxa with read counts and confidence scores.

5. Taxonomy Classification Agent
- Normalize and clean taxonomy results.
- Map detected taxa to family, genus, species, and accession information.
- Identify likely false positives, low-complexity hits, environmental phages, and potential contamination.

6. Abundance Analysis Agent
- Normalize viral abundance using reads per million, genome length correction, or PMMoV normalization if metadata are available.
- Compare abundance across samples, locations, and time points.
- Generate tables for viral trends.

7. Novel Virus / Variant Screening Agent
- Identify suspicious unclassified viral contigs or divergent viral signals.
- Support assembly-based analysis using MEGAHIT or metaSPAdes.
- Prepare commands or modules for VirSorter2, VIBRANT, geNomad, CheckV, or DeepVirFinder.
- Summarize possible novel viral candidates.

8. Epidemiological Risk Assessment Agent
- Combine abundance, temporal trend, taxonomy, host range, and known pathogen status.
- Assign simple risk levels: Low, Medium, High, or Critical.
- Explain why each virus receives its risk level.

9. Report Writer Agent
- Generate human-readable reports in Markdown and HTML.
- Include QC summary, detected viruses, abundance trends, risk assessment, and recommended follow-up actions.
- Reports should be suitable for researchers, public health analysts, and manuscript preparation.

10. Orchestrator Agent
- Coordinate all other agents.
- Decide the order of execution.
- Track task status.
- Save structured logs.
- Handle failed steps gracefully.

Technical requirements:
- Use Python as the main programming language.
- Prefer a modular architecture.
- The first version should be runnable locally without requiring cloud services.
- Use command-line interface first.
- Use YAML configuration files.
- Use pandas for table processing.
- Use pydantic for configuration and data validation.
- Use pathlib instead of hard-coded string paths.
- Use logging instead of print statements.
- Write clean, documented, maintainable code.
- Include unit tests where appropriate.
- Do not assume sudo/root privileges.
- The system should be compatible with HPC environments using SLURM.
- External bioinformatics tools may be called through subprocess, but the code should also support dry-run mode where commands are generated but not executed.

Suggested project structure:

MetaMAVS/
  README.md
  pyproject.toml
  configs/
    example_config.yaml
  data/
    example_manifest.csv
  metamavs/
    __init__.py
    cli.py
    config.py
    schemas.py
    orchestrator.py
    agents/
      __init__.py
      base_agent.py
      input_manager.py
      qc_agent.py
      host_removal_agent.py
      viral_detection_agent.py
      taxonomy_agent.py
      abundance_agent.py
      novel_virus_agent.py
      risk_assessment_agent.py
      report_writer_agent.py
    utils/
      __init__.py
      command_runner.py
      logging_utils.py
      file_utils.py
      taxonomy_utils.py
    workflows/
      __init__.py
      local_workflow.py
      slurm_workflow.py
  reports/
  tests/
    test_config.py
    test_schemas.py
    test_orchestrator.py

Implementation requirements for the first working version:
1. Create the full project skeleton.
2. Implement configuration loading from YAML.
3. Implement sample manifest validation.
4. Implement a BaseAgent class.
5. Implement all agent classes with clear run() methods.
6. For bioinformatics tools, first implement dry-run command generation instead of requiring actual tools to be installed.
7. Implement an Orchestrator that runs agents in sequence.
8. Save intermediate outputs as CSV/JSON files.
9. Generate a final Markdown report.
10. Provide a CLI command such as:

   metamavs run --config configs/example_config.yaml --dry-run

11. Provide example input files and example output report.
12. Include clear instructions in README.md.

Important design preference:
Do not create an overly complex system at first. Start with a minimal but extensible research prototype. The code should be easy to expand later to support Nextflow, Snakemake, AutoGen, LangGraph, or Claude/OpenAI API-based reasoning agents.

Please begin by:
1. Explaining the proposed software architecture.
2. Then create the files one by one.
3. Make the first version executable.
4. After generating the project, tell me how to run it.
```

---

## 更适合 Claude Code 的分阶段提示词

如果你不想一次让它生成太多代码，可以先用这个：

```text
I want to build a Python project called MetaMAVS: Metagenomic Multi-Agent Virus Surveillance System.

Please first create only the project architecture and minimal working prototype.

The prototype should include:
- pyproject.toml
- README.md
- configs/example_config.yaml
- data/example_manifest.csv
- metamavs/config.py
- metamavs/schemas.py
- metamavs/cli.py
- metamavs/orchestrator.py
- metamavs/agents/base_agent.py
- simple placeholder agents for QC, host removal, viral detection, taxonomy, abundance, risk assessment, and report writing
- dry-run mode
- final Markdown report generation

The command should be:

metamavs run --config configs/example_config.yaml --dry-run

Please generate the files and code step by step. Keep the first version simple, runnable, and easy to expand.
```

---

## 我建议你项目第一版名称写法

论文或软件说明中可以写：

**MetaMAVS: A Multi-Agent System for Virus Surveillance Based on Metagenomic Data**

或者更正式一点：

**MetaMAVS: A Metagenomic Multi-Agent Virus Surveillance System for Automated Viral Detection, Classification, and Epidemiological Risk Assessment**

第一个更简洁，适合软件名；第二个更适合论文标题或项目申请。
