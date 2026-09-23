import time
from neo4j import GraphDatabase

uri = "bolt://127.0.0.1:7687"
user = "neo4j"
pw = "Suryaraj@1234$"

print("Sleeping 6 seconds to clear rate limit...")
time.sleep(6)

print(f"Trying password {pw[0]}***...")
try:
    driver = GraphDatabase.driver(uri, auth=(user, pw))
    with driver.session(database="defendx") as session:
        result = session.run("RETURN 1 AS connected")
        record = result.single()
        if record and record["connected"] == 1:
            print(f"SUCCESS with password {pw[0]}***")
            # Fix the .env files automatically
            content_root = open('../.env').read()
            content_backend = open('.env').read()
            open('../.env', 'w').write(content_root.replace('NEO4J_PASSWORD=password', f'NEO4J_PASSWORD={pw}'))
            open('.env', 'w').write(content_backend.replace('NEO4J_PASSWORD=password', f'NEO4J_PASSWORD={pw}'))
            print("Fixed .env files!")
        else:
            print("Connected, but returned unexpected result:", record)
except Exception as e:
    print(f"FAILURE: {type(e).__name__} - {e}")
