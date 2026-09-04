# ARC - Translations

ARC translations is a comprehensive machine-readable translations documents in CSV format that it suyncronizes with the correspondent in the [ARC repository](https://github.com/ISARICResearch/ARC).


## Organization

The repository is organized as a set of folders. Each version of ARC recieves one folder, which then is split further into one folder per language; English being the source folder, and all other languages being translations.

Translations of ARC are generated and tested using scripts inside the folder "code".

### Root
- code/main.py calls the translations to run, with the parameter of the version to translate. It can be ran from the terminal like so:  "python code/main.py --arc-version=v1.5.0"
- code/get_version_path.py simply gets the most recent version path, to pass in as a paramter elsewhere
- code/utils.py has simple utility functions

### Translation
- code/translation/TranslationManager.py Handles setting up directories and calling translation scripts
- code/translation/ArchTranslation.py translates ARCH.csv
- code/translation/ListTranslation.py translates List CSVs
- code/translation/PaperTranslations.py translates paper like details

### Test
- code/test/conftest.py is a utility to manage tests
- code/test/test_arc_translations.py uses some tests from ARC to ensure ARCH.csv is correct
- code/test/test_lists.py uses some tests from ARC to ensure list CSVs are correct

### Old
All scripts not currently being used for translation are sorted into code/old/

## Updates
ARC-Translations is automatically updated upon an update to the ARC repository. Upon automatic translation, LINK is called and updated with this information. 

LINK then pushes information back to ARC translations, so that the number of translators stays consistent.