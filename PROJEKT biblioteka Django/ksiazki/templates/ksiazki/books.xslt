<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <html>
            <head>
                <title>Lista książek</title>
                <style>
                    table {
                    width: 100%;
                    border-collapse: collapse;
                    }
                    th, td {
                    padding: 8px;
                    border: 1px solid #ddd;
                    }
                    th {
                    background-color: #f4f4f4;
                    }
                </style>
            </head>
            <body>
                <h2>Katalog książek</h2>
                <table>
                    <tr>
                        <th>Tytuł</th>
                        <th>Autor</th>
                        <th>Rok wydania</th>
                    </tr>
                    <xsl:for-each select="ksiazki/ksiazka">
                        <tr>
                            <td><xsl:value-of select="tytul"/></td>
                            <td><xsl:value-of select="autor"/></td>
                            <td><xsl:value-of select="rok"/></td>
                        </tr>
                    </xsl:for-each>
                </table>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>