import os
import re

splitSymbols= r'[(\s\:]'
namespace_regex = r'namespace (.+)\n'

# numbers are not allowed in latex_commands
def replaceNumber(input_string):
    number_text_mapping = {
        '0': 'zero', '1': 'one', '2': 'two', '3': 'three', '4': 'four',
        '5': 'five', '6': 'six', '7': 'seven', '8': 'eight', '9': 'nine'
    }
    
    output_string = ''
    for char in input_string:
        if char.isdigit():
            output_string += number_text_mapping[char]
        else:
            output_string += char
    
    return output_string


# Function to perform some action on files
def process_file(root, file):
    file_path = os.path.join(root, file)
    commands = []
    with open(file_path) as f:
        namespace = ""
        lines = f.readlines()

        for i,line in enumerate(lines):
            line = line.lstrip()
            if line.startswith("namespace"):
                namespace = re.match(namespace_regex, line).group(1)
                continue
            if ''.join(line.split()) == "end" + namespace:
                namespace = ""

            if line.startswith("def") or line.startswith("lemma") or line.startswith ("theorem") or line.startswith("structure") or line.startswith("inductive") or line.startswith("abbrev") or line.startswith("class"): 
                result = re.split(splitSymbols, line)
                # allow string to be valid latex
                resultName = result[1].replace("_", "").replace(".", "").replace("'", "prime").replace("?", "")
                resultName = replaceNumber(resultName)
                textVersion =  result[1].replace("_", "\_").replace("'", "\\textsc{\char13}")
                if "'" in result[1]:
                    continue

                if resultName == "root":
                    commands.append(f"\\newcommand{{\\treeRoot}}{{\\repoLinkCode{{{file}\#L{i+1}}}{{{textVersion}}}}}")
                elif resultName == "rule":
                    commands.append(f"\\newcommand{{\\datalogrule}}{{\\repoLinkCode{{{file}\#L{i+1}}}{{{textVersion}}}}}")
                else:
                    commands.append(f"\\newcommand{{\\{namespace+resultName}}}{{\\repoLinkCode{{{file}\#L{i+1}}}{{{textVersion}}}}}")
            elif line.startswith("noncomputable") : 
                result = re.split(splitSymbols, line)
                # allow string to be valid latex
                resultName = result[2].replace("_", "").replace(".", "").replace("'", "2")
                textVersion =  result[2].replace("_", "\_").replace("'", "\\textsc{\char13}")
                if "'" in result[2]:
                    continue

                if resultName == "root":
                    commands.append(f"\\newcommand{{\\treeRoot}}{{\\repoLinkCode{{{file}\#L{i+1}}}{{{textVersion}}}}}")
                elif resultName == "rule":
                    commands.append(f"\\newcommand{{\\datalogrule}}{{\\repoLinkCode{{{file}\#L{i+1}}}{{{textVersion}}}}}")
                else:
                    commands.append(f"\\newcommand{{\\{namespace+resultName}}}{{\\repoLinkCode{{{file}\#L{i+1}}}{{{textVersion}}}}}")
    return commands

# Function to traverse directories and process files
def traverse_folders(root_folder, target_extensions, excluded_folders):
    commands = ["\\newcommand{\\repoUrl}{https://github.com/knowsys/CertifyingDatalog/blob/develop}", 
    "\\newcommand{\\repoLinkBase}[2]{\href{\\repoUrl/#1}{\\textcolor{leansymbolcolor}{\\texttt{#2}}}\\xspace}",
    "\\newcommand{\\repoLinkCode}[2]{\\repoLinkBase{CertifyingDatalog/#1}{#2}}"
    ]
    for root, dirs, files in os.walk(root_folder):
        for excluded_folder in excluded_folders:
            # if not present removing element will raise error
            if excluded_folder in dirs:
                dirs.remove(excluded_folder) 

        for file in files:
            for extension in target_extensions:
                if file.endswith(extension):
                    commands.extend(process_file(root, file))
                    break
    with open("codeCommands.tex", "w") as f:
        for cmd in commands:
            f.write(cmd + "\n")

# Example usage:
root_folder = "/home/johannes/CertifyingDatalog/CertifyingDatalog"
target_extensions = [".py", ".lean"]
excluded_folders = [".lake", "lake-packages", 'transitiveClosureBenchmarkExponentialExtension', 'transitiveClosureBenchmarkAllFacts', 'transitiveClosureBenchmarkSingleFact', 'transitiveClosureToyExample', 'elReasoning', 'OUTDATED-transitiveClosureBenchmarkExtreme']


traverse_folders(root_folder, target_extensions, excluded_folders)