from neo4j import GraphDatabase
import requests
from io import StringIO
import csv


class Neo4jHandler:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def load_data(self, csv_content):
        with self.driver.session() as session:
            # with open(csv_content, "r") as file:
            reader = csv.DictReader(StringIO(csv_content))
            for row in reader:
                drug_name = row["Drug"]
                chemical = row["Chemical"]
                dosage = row["Dosage"]

                session.execute_write(
                    self.create_relationships, drug_name, chemical, dosage
                )

    @staticmethod
    def create_relationships(tx, drug_name, chemical, dosage):
        # Create or get the Drug node
        tx.run(
            """
            MERGE (d:Drug {name: $drug_name})
            """,
            drug_name=drug_name,
        )

        # Create or get the Chemical node
        tx.run(
            """
            MERGE (c:Chemical {name: $chemical})
            """,
            chemical=chemical,
        )

        # Create or get the Dosage node
        tx.run(
            """
            MERGE (dos:Dosage {value: $dosage})
            """,
            dosage=dosage,
        )

        # Create relationships
        tx.run(
            """
            MATCH (d:Drug {name: $drug_name})
            MATCH (c:Chemical {name: $chemical})
            MERGE (d)-[:CONTAINS]->(c)
            """,
            drug_name=drug_name,
            chemical=chemical,
        )

        tx.run(
            """
            MATCH (d:Drug {name: $drug_name})
            MATCH (dos:Dosage {value: $dosage})
            MERGE (d)-[:HAS_DOSAGE]->(dos)
            """,
            drug_name=drug_name,
            dosage=dosage,
        )

        tx.run(
            """
            MATCH (c:Chemical {name: $chemical})
            MATCH (dos:Dosage {value: $dosage})
            MERGE (c)-[:QUANTITY]->(dos)
            """,
            dosage=dosage,
            chemical=chemical,
        )

        tx.run(
            """
            MATCH (c:Chemical {name: $chemical})
            MATCH (d:Drug {value: $drug_name})
            MERGE (c)-[:CONSTITUENT_OF]->(d)
            """,
            drug_name=drug_name,
            chemical=chemical,
        )

        tx.run(
            """
            MATCH (d:Drug {name: $drug_name})
            MATCH (dos:Dosage {value: $dosage})
            MERGE (dos)-[:OF_DRUG]->(d)
            """,
            dosage=dosage,
            drug_name=drug_name,
        )


if __name__ == "__main__":
    # uri = "neo4j+s://d3a9f16a.databases.neo4j.io"
    # uri = "bolt://localhost:7687"
    uri = "neo4j+s://f4c74ec3.databases.neo4j.io"
    user = "neo4j"
    # password = "knowledge"
    # password = "mLCCAhPSqAX6echkvVvtl5NKniDpgYxLHsHfjc7nt14"
    password = "QKs0fF2Q1ijgSew19BpHI8gH97Yli_E_L9KmPf_gCCU"
    csv_url = "https://raw.githubusercontent.com/MBUYt0n/csv-hosting/main/data.csv"
    # csv_url = "/var/lib/neo4j/import/data.csv"

    response = requests.get(csv_url)
    response.raise_for_status()  # This will raise an error if the download failed

    handler = Neo4jHandler(uri, user, password)
    handler.clear_database()
    handler.load_data(response.text)  # Pass the CSV content directly
    handler.close()
