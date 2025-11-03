# 🧬 BioFetch

**Bioinformatics Data Downloader** - Simple CLI for downloading from 6 major biological databases.

[![PyPI version](https://badge.fury.io/py/biofetch.svg)](https://badge.fury.io/py/biofetch)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 🚀 Quick Start
```bash
# Install
pip install biofetch==1.0.2

# Download SARS-CoV-2 genome
biofetch download NC_045512 --db genbank

# Batch download
echo -e "NC_045512\nNC_000001" > accessions.txt
biofetch batch --file accessions.txt --db genbank --parallel 3
```

## 📦 Supported Databases

| Database | Description | Example |
|----------|-------------|---------|
| **SRA** | Sequence Read Archive | `SRR000001` |
| **GenBank** | Nucleotide sequences | `NC_045512` |
| **UniProt** | Protein sequences | `P04637` |
| **PDB** | Protein structures | `1A0O` |
| **ENA** | European Nucleotide Archive | `A00145` |
| **GEO** | Gene expression data | `GSE68849` |

## 💡 Why BioFetch?

- ✅ **One tool** for all databases (no more switching between APIs)
- ✅ **Simple syntax** - same command for every database
- ✅ **Parallel downloads** - speed up batch operations
- ✅ **Auto-decompress** - handles gzipped files automatically
- ✅ **Cross-platform** - works on Windows, Linux, macOS
- ✅ **Open source** - MIT licensed

## 📖 Usage

### Download Single File
```bash
# GenBank - SARS-CoV-2 genome
biofetch download NC_045512 --db genbank

# UniProt - Human p53 protein
biofetch download P04637 --db uniprot

# PDB - Protein structure
biofetch download 1A0O --db pdb
```

### Batch Download
```bash
# From command line
biofetch batch NC_045512 NC_000001 NC_012920 --db genbank --parallel 3

# From file
biofetch batch --file my_accessions.txt --db genbank --parallel 5
```

### Configuration
```bash
# Set output directory
biofetch config set output_dir ~/my_data

# View config
biofetch config show

# Reset to defaults
biofetch config reset
```

## 🎓 Use Cases

### For Students
- Download genomes for alignment practice
- Fetch protein sequences for classification projects
- Get expression data for ML experiments

### For Researchers
- Batch download RNA-Seq data for DEG analysis
- Retrieve protein structures for docking studies
- Access GEO datasets for meta-analysis

### For Educators
- Quick data access for teaching materials
- Reproducible examples for courses
- No complex setup for students

## 🛠️ Installation
```bash
# From PyPI
pip install biofetch==1.0.2

# From source
git clone https://github.com/Ananaya-J/Biofetch.git
cd biofetch
pip install -e .
```

## 📊 Examples

### RNA-Seq Analysis Pipeline
```bash
# Download reads
biofetch batch --file sra_accessions.txt --db sra --parallel 4

# Continue with your analysis...
```

### Comparative Genomics
```bash
# Download multiple genomes
biofetch batch NC_045512 NC_000001 NC_012920 --db genbank
```

### Protein Structure Analysis
```bash
# Download PDB structures
biofetch download 1A0O --db pdb
```

## 🐛 Known Limitations

- **SRA**: Large files, may require extended timeout
- **ENA**: Some older accessions may not be available
- **GEO**: Series files are large and gzip-compressed (auto-decompressed)

## 🔮 Roadmap

- [ ] Support for more databases (TCGA, RefSeq, KEGG)
- [ ] Python API for programmatic access
- [ ] Built-in quality control checks
- [ ] Format conversion utilities
- [ ] Integration with popular analysis tools

## 🤝 Contributing

Contributions welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request


## 📞 Support

- 📧 **Email**: ananayajain2024@gmail.com
- 💬 **Discussions**: [GitHub Discussions](https://github.com/Ananaya-J/Biofetch/discussions)

---

**Made with ❤️ for the bioinformatics community**

⭐ Star this repo if you find it useful!
