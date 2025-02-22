# Configuration Documentation Generation

This script converts the `config_declaration.yml` file into structured Markdown documentation, similar to the documentation generated by `ckanext-dcat`. The generated Markdown file provides a clear and organized overview of your configuration settings.

## Prerequisites

- **Python 3.x** installed on your machine.
- **Git** (optional, for cloning the repository).

## Setup Instructions

Follow the steps below to set up a virtual environment, install the necessary dependencies, and run the script on both **Windows** and **Linux** systems.

### 1. Clone the Repository (Optional)

If you haven't already, clone your repository to your local machine:

```sh
git clone https://github.com/your-username/your-repository.git
cd your-repository
```

*Replace `https://github.com/your-username/your-repository.git` with your repository's actual URL.*

### 2. Navigate to the Script Directory

Navigate to the directory containing the 

config_declaration_to_md.py

 script:

```sh
cd ckanext/schemingdcat/docs/tools
```

### 3. Create a Virtual Environment

Creating a virtual environment ensures that your project dependencies are isolated from other projects.

#### On Linux/macOS:

```sh
python3 -m venv venv
```

#### On Windows:

```sh
python -m venv venv
```

### 4. Activate the Virtual Environment

Activate the virtual environment to start using it.

#### On Linux/macOS:

```sh
source venv/bin/activate
```

#### On Windows (Command Prompt):

```cmd
venv\Scripts\activate
```

#### On Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

*If you encounter an execution policy error on PowerShell, you can temporarily allow script execution:*

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

### 5. Install Dependencies

Install the required Python libraries using `pip`.

#### Option 1: Using requirements.txt

If a `requirements.txt` file is provided, run:

```sh
pip install -r requirements.txt
```

#### Option 2: Manual Installation

If there's no `requirements.txt`, install the necessary packages manually:

```sh
pip install pyyaml jinja2
```

### 6. Run the Script

Execute the Python script to generate the Markdown documentation.

```sh
python config_declaration_to_md.py
```

### 7. Locate the Generated Documentation

After running the script, an `output` directory will be created in the same location as the script. Inside this folder, you'll find the `configuration.md` file containing your configuration documentation.

```
ckanext/schemingdcat/docs/tools/
│
├── config_declaration_to_md.py
└── output/
    └── configuration.md
```