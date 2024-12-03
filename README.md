# rss-feed-generator
This script fetches product data from a MySQL database, generates an RSS feed in XML format, and uploads it to an S3 bucket.

# MySQL to S3 RSS Feed Generator

This Python script fetches data from a MySQL database, generates an RSS feed in XML format, and uploads it to an S3 bucket. The RSS feed can be used for product listings on e-commerce platforms or any other system that accepts RSS feeds.

## Requirements

Before running the script, ensure you have the following Python packages installed:

- `mysql-connector-python`: For connecting to the MySQL database.
- `sqlalchemy`: For database interaction using SQLAlchemy.
- `pandas`: For data manipulation.
- `boto3`: AWS SDK for Python, used to interact with S3.
- `lxml`: For XML parsing and generation.

You can install the required packages using `pip`:

```bash
pip install mysql-connector-python sqlalchemy pandas boto3 lxml
```
1. Connect to MySQL Database
The script uses SQLAlchemy to connect to a MySQL database and fetch data from a specified table.
```
def connect_to_database():
    try:
        engine = create_engine('mysql+mysqlconnector://username:password@host/database')
        return engine
    except Exception as err:
        print(f"Error: {err}")
        return None
```
2. Fetch Data from the Database
The script fetches data from the MySQL database using a specified SQL query and stores it in a Pandas DataFrame.
```
def fetch_data(engine):
    query = '''
    SELECT * FROM your_table;
    '''
    return pd.read_sql(query, engine)
```
3. Generate RSS XML Feed
The script generates an RSS feed in XML format, including product details such as price, availability, shipping information, and more. The generate_rss_xml function builds the XML structure using the lxml library.
```
def generate_rss_xml(items, filename):
    namespaces = {'g': "http://base.google.com/ns/1.0"}
    rss = ET.Element("rss", nsmap={'g': namespaces['g']}, version="2.0")
    channel = ET.SubElement(rss, "channel")
    
    ET.SubElement(channel, "title").text = "Your Title"
    ET.SubElement(channel, "link").text = "https://yourwebsite.com"
    ET.SubElement(channel, "description").text = "Description"
    ET.SubElement(channel, "lastBuildDate").text = pd.Timestamp.now().isoformat()
    
    for _, item in items.iterrows():
        item_element = ET.SubElement(channel, "item")
        ET.SubElement(item_element, ET.QName(namespaces['g'], "id")).text = str(item["id"])
        # Additional item details...
    
    try:
        rough_string = ET.tostring(rss, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        with open(filename, "wb") as files:
            files.write(rough_string)
        print(f"XML file '{filename}' generated successfully.")
    except Exception as e:
        print(f"Error generating XML: {e}")
```
4. Upload XML File to S3
Once the XML file is generated, the script uploads it to an S3 bucket using the boto3 library.
```
def upload_to_s3(filename):
    try:
        s3.Bucket(BUCKET).upload_file(filename, filename)
        print("Upload Successful")
    except NoCredentialsError:
        print("Credentials not available")
    except FileNotFoundError:
        print(f"File '{filename}' not found. Upload failed.")
    except Exception as e:
        print(f"Error uploading file: {e}")
```
5. Main Function
The main function ties everything together. It connects to the database, fetches the data, generates the XML file, and uploads it to S3.
```
def main():
    engine = connect_to_database()
    if engine:
        items = fetch_data(engine)
        generate_rss_xml(items, "output.xml")
        upload_to_s3("output.xml")

if __name__ == "__main__":
    main()
```
How to Use
- Update the MySQL Connection: Modify the connection string in the connect_to_database() function with your database's credentials (username, password, host, and database).
- Configure the SQL Query: Update the query in the fetch_data() function to match your table and data structure.
- Update the S3 Bucket Name: Set your S3 bucket name in the BUCKET variable.
- Run the Script: Execute the script, and it will generate an XML RSS feed and upload it to your S3 bucket.
