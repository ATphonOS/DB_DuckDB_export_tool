## DB (DuckDB) export tool 
This program loads [DuckDB](https://github.com/duckdb/duckdb "Title") databases, display their tables, and exports their structure and data to the following formats:
<table>
        <tr>
            <th></th>
           <th colspan="2">Extract</th>
        </tr>
        <tr>
            <th> Format </th>
            <th> Structure <br> <em>SQL DDL statement</em></th>
            <th>  Data </th>
        </tr>
        <tr>
            <td>SQL</td>
            <td align="center">Yes</td>
           <td align="center">Yes</td>
        </tr>
        <tr>
            <td>SQLite</td>
            <td align="center">Yes</td>
            <td align="center">Yes</td>
        </tr>
        <tr>
            <td>CSV</td>
            <td align="center">-</td>
            <td align="center">Yes</td>
        </tr>
        <tr>
            <td>JSON</td>
            <td align="center">-</td>
            <td align="center">Yes</td>
        </tr>
        <tr>
            <td>XML</td>
            <td align="center">-</td>
            <td align="center">Yes</td>
        </tr>
        <tr>
            <td>Parquet</td>
            <td align="center">-</td>
            <td align="center">Yes</td>
        </tr>
        <tr>
            <td>HTML</td>
            <td align="center">-</td>
            <td align="center">Yes</td>
        </tr>
     </table>

### Installation
1. **Clone or Download the Repository**:
   ```bash
   git clone https://github.com/ATphonOS/DB_DuckDB_export_tool.git
   cd ATphonOs DuckDB
   ```
2. **Execute the script directly with Python.**
   ```bash
   python main.py
   ```   
     
     
## Download compiled

[Realease on Github](https://github.com/ATphonOS/DB_DuckDB_export_tool/releases/tag/v1.0.0)

[Download](https://github.com/ATphonOS/DB_DuckDB_export_tool/releases/download/v1.0.0/ATphonOS.-.DB.DuckDB.export.tool.exe)

 ## Compile code  

To compile download the [source code](https://github.com/ATphonOS/DB_DuckDB_export_tool/archive/refs/heads/main.zip) and unzip.  

Option 1:

Install the dependencies from requeriments.txt.

```Python
pip install -r requirements.txt
```

Compile command:
```Python
pyinstaller --name "ATphonOS - DB (DuckDB) export tool" --onefile --windowed --icon="icon/logo_app.ico"
--add-data "icon/logo_app.png;icon" --add-data "icon/logo_app.ico;icon"
--hidden-import=duckdb --hidden-import=sqlite3 main.py
```

Option 2:

Compile command (create a folder with the executable and all dependencies):

```Python
pyinstaller --name "ATphonOS - DB (DuckDB) export tool" --onedir --windowed --icon="icon/logo_app.ico"
--add-data "icon/logo_app.png;icon" --add-data "icon/logo_app.ico;icon"
--hidden-import=duckdb --hidden-import=sqlite3 --collect-all duckdb --collect-all sqlite3 main.py
```

 ## Usage
 
![MainSE](https://github.com/user-attachments/assets/6e787e52-19e3-4e36-bfc1-f017564dc3da)

 1. Open the downloaded or compiled program.
 2. Open the DuckDB database (tables will load automatically).
 3. Preview the table data (optional).
 4. Select the export option.
 5. Enter the name of the exported file and save it.

The exported file will be saved in the same directory as the open database. For quick access to this directory, click the database path displayed at the bottom of the table area.

To search for tables by name, use the search field.

***Currently Windows-only***
