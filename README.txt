# celllinedb
A cell line database visualisation tool for the CHUV.

## What does this script do?
This scripts takes as input the EXCEL database of cell lines and creates a multi-page PDF.
Each page of the PDF is a scheme of one cell line "drawer".

## How to run on a CHUV machine
You have to run this script from your "C:/TEMP" folder on your computer as the CHUV does not allow
running ".exe" files from other folders. Here is what you need to do:

 - Copy the "celllinedb.zip" file to your "C:/TEMP" directory
 - Unzip the "celllinedb.zip" file
 - Go into your "C:/TEMP/celllinedb" directory
 - Run the "celllinedb.exe" shortcut

This will launch the script, read the EXCEL database, and create a PDF with one page per "drawer".

## How to customize / change things
There is a configuration file called "config.txt".
You can open it with any text editor (Notepad, WordPad, etc.).
You can edit the following fields *safely*:
 - "db_path": specifies where your database EXCEL file is. Use full paths *without* backslashes (e.g. "C:/Users/ ...")
 - "output_pdf_file_path": specifies where your output PDF file will be generated. Again, use full paths *without* backslashes (e.g. "C:/Users/ ...")

## How to customize / change things
 - If you know what you are doing, you can edit the "celllinedb.py" script or the other fields in the "config.txt" JSON file.
 - After that, you need to regenerate the exe file by using the "pyinstaller" python module. This requires a working python installation
 - Run the following command from the command line:
	pyinstaller celllinedb.py
 - This will (re-)generate the dist folder containing the "celllinedb.exe" file.
 - This executable should however be run from the main folder, not the "dist" folder, so there is a shortcut in the main folder pointing to this executable. Use that shortcut to run the program.
 - If you run this multiple times, pyinstaller might ask you whether you want to overrwrite the content of the "dist" folder:
	WARNING: The output directory "C:\TEMP\celllinedb\dist\celllinedb" and ALL ITS CONTENTS will be REMOVED! Continue? (y/N)
 - Answer with a "y" and hit ENTER