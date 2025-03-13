## DB (DuckDB) export tool 
This program loads [DuckDB](https://github.com/duckdb/duckdb "Title") databases, views their tables, and exports their structure and data to the following formats:
<table>
        <tr>
            <th></th>
           <th colspan="2">Extract</th>
        </tr>
        <tr>
            <th>[ Format ]</th>
            <th>[ Structure ]<br> <em>SQL DDL statement</em></th>
            <th> [ Data ]</th>
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
     
     

### Main window

![MainSE](https://github.com/user-attachments/assets/6e787e52-19e3-4e36-bfc1-f017564dc3da)


 1. Open DB DuckDB and load their tables.
 2. Preview the table data
 3. Select the export option
 4. Write the name of the exported file and save it
The created file is saved in the same directory that contains the open database, for quick access to the same directory, click on the open database path at the bottom of the table area.
