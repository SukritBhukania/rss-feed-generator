import mysql.connector
from sqlalchemy import create_engine
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError
from lxml import etree as ET

s3 = boto3.resource('s3')
BUCKET = "your_bucket_name"

def connect_to_database():
    try:
        engine = create_engine('mysql+mysqlconnector://username:password@host/database')
        return engine
    except Exception as err:
        print(f"Error: {err}")
        return None

def fetch_data(engine):
    query = '''
    SELECT * FROM your_table;
    '''
    return pd.read_sql(query, engine)

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
        ET.SubElement(item_element, "title").text = item["Title"]
        product_link = f"https://yourwebsite.com/products/{item['Alias']}"
        image_link = f"https://yourwebsite.com/{item['Image']}"
        ET.SubElement(item_element, "link").text = product_link
        ET.SubElement(item_element, ET.QName(namespaces['g'], "image_link")).text = image_link
        ET.SubElement(item_element, ET.QName(namespaces['g'], "condition")).text = "new"
        ET.SubElement(item_element, ET.QName(namespaces['g'], "availability")).text = "in stock" if item["Available"] == 'Yes' else "out of stock"
        ET.SubElement(item_element, ET.QName(namespaces['g'], "price")).text = f"{item['price']} INR"
        shipping = ET.SubElement(item_element, ET.QName(namespaces['g'], "shipping"))
        ET.SubElement(shipping, ET.QName(namespaces['g'], "country")).text = "IN"
        ET.SubElement(shipping, ET.QName(namespaces['g'], "service")).text = "Standard"
        ET.SubElement(shipping, ET.QName(namespaces['g'], "price")).text = "0 INR"
        ET.SubElement(item_element, ET.QName(namespaces['g'], "google_product_category")).text = "Your Category"
        ET.SubElement(item_element, ET.QName(namespaces['g'], "unit_pricing_measure")).text = item["Uom"]

    try:
        rough_string = ET.tostring(rss, pretty_print=True, xml_declaration=True, encoding='UTF-8')
        with open(filename, "wb") as files:
            files.write(rough_string)
        print(f"XML file '{filename}' generated successfully.")
    except Exception as e:
        print(f"Error generating XML: {e}")

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

def main():
    engine = connect_to_database()
    if engine:
        items = fetch_data(engine)
        generate_rss_xml(items, "output.xml")
        upload_to_s3("output.xml")

if __name__ == "__main__":
    main()