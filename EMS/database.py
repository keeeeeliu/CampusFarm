import sqlite3

# 'sqlite3 var/ems.db'

def create_table():
    """Create the databbase table."""
    try:
        connection = sqlite3.connect('sqlite/ems.db')
        cursor = connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data(
            totalCarbonEmission VARCHAR(256) NOT NULL, 
            solarCarbonEmission VARCHAR(256) NOT NULL,
            evCarbonEmission VARCHAR(256) NOT NULL,
            emsCarbonEmission VARCHAR(256) NOT NULL,
            netInvertertoGrid VARCHAR(256) NOT NULL,
            netSolartoInverter VARCHAR(256) NOT NULL,
            netInvertertoComps VARCHAR(256) NOT NULL,
            postid INTEGER PRIMARY KEY AUTOINCREMENT,
            created DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS chart(
            baselineEmission VARCHAR(256) NOT NULL,
            noEMSEmission VARCHAR(256) NOT NULL,
            withEMSEmission VARCHAR(256) NOT NULL,
            postid INTEGER PRIMARY KEY AUTOINCREMENT,
            created DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        connection.close()
    except sqlite3.Error as error:
        print(f"Error while creating table: {error}")


def upload_data():
    """Upload generated data to database."""
    try:
        connection = sqlite3.connect('sqlite/ems.db')
        cursor = connection.cursor()

        # Update data
        cursor.execute(
            "INSERT INTO data(totalCarbonEmission, solarCarbonEmission, evCarbonEmission, emsCarbonEmission, netInvertertoGrid, netSolartoInverter, netInvertertoComps) "
            "VALUES (?,?,?,?,?,?,?) ",
            (1, 2, 3, 4, 5, 6, 7)
        )
        connection.commit()

        cursor.execute(
            "INSERT INTO chart(baselineEmission, noEMSEmission, withEMSEmission) "
            "VALUES (?,?,?) ",
            (8, 9, 10)
        )
        connection.commit()

        # close the connection
        connection.close()
    except sqlite3.Error as error:
        print(f"Error while inserting data: {error}")


if __name__ == "__main__":
    upload_data()