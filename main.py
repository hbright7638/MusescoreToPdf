# TODO (DONE): Some links have sheets that are .pngs instead of .pdfs, such as this one: https://musescore.com/classicman/scores/254071. Handle this.
# TODO: Give result .pdf the name of the piece
# TODO: Fix/handle negative dash stroke value in the .svg files
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import requests
import time
import cairosvg
from PIL import Image
from io import BytesIO
import img2pdf
from pypdf import PdfMerger

# Convert .svg files into individual .pdfs
def svg_to_pdf(svg_url, pdf_filename):
    svg_response = requests.get(svg_url).content
    cairosvg.svg2pdf(bytestring=svg_response, write_to=pdf_filename)

# Convert .png files into individual .pdfs
def png_to_pdf(png_url, pdf_filename):
    response = requests.get(png_url)
    image = Image.open(BytesIO(response.content))
    image_bytes = BytesIO()
    image.save(image_bytes, format='PNG')
    image_bytes.seek(0)
    pdf_bytes = img2pdf.convert(image_bytes)
    with open(pdf_filename, 'wb') as f:
        f.write(pdf_bytes)


options = Options()
options.page_load_strategy = 'none'
driver = webdriver.Chrome(options=options)
driver.maximize_window()
driver.get("https://musescore.com/user/13958871/scores/6027764")

# Make Selenium driver wait until the first sheet image loads before proceeding
while True:
    try:
        element = driver.find_element(By.XPATH, "//*[@id='jmuse-scroller-component']/div[1]/img")
        break
    except:
        time.sleep(1)

# link_check is the URL to the first page image
link_check = driver.find_element(By.XPATH, "//*[@id='jmuse-scroller-component']/div[1]/img").get_attribute('src')
container = driver.find_element(By.XPATH, "//*[@id='jmuse-scroller-component']")
elements = container.find_elements(By.XPATH, "//*[@id='jmuse-scroller-component']/div")
numElems = len(elements) - 3

# Get .svg URLs
list_image_urls = []
for i in range(numElems):
    scroll_element_path = "//*[@id='jmuse-scroller-component']/div[" + str(i + 1) + "]"
    scroll_element = driver.find_element(By.XPATH, scroll_element_path)
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'start', inline: 'start'});", scroll_element)
    # WebDriverWait to wait until the image loads before trying to get the svg_url from the element
    WebDriverWait(driver, 10).until(
        lambda driver: driver.find_element(By.XPATH, scroll_element_path + "/img").get_attribute('src') is not None)
    svg_url = scroll_element.find_element(By.XPATH, scroll_element_path + "/img").get_attribute('src')
    list_image_urls.append(svg_url)

driver.close()

print(list_image_urls)


# Split the first image URL at the '?' character
url_parts = link_check.split('?')

pdf_files = []
# Check whether the URL is for an .svg or .png
if url_parts[0].endswith('.svg'): # .svg case
    for i, svg_url in enumerate(list_image_urls):
        # Download .svg files from the URLs, convert to .pdfs
        pdf_filename = f"image_{i}.pdf"
        svg_to_pdf(svg_url, pdf_filename)
        pdf_files.append(pdf_filename)
else:
    for i, png_url in enumerate(list_image_urls): # .png case
        # Download .png files from the URLs, convert to .pdfs
        pdf_filename = f"image_{i}.pdf"
        png_to_pdf(png_url, pdf_filename)
        pdf_files.append(pdf_filename)

# Merge all the .pdfs into a single .pdf file
merger = PdfMerger()
for pdf in pdf_files:
    merger.append(pdf)

merger.write("result.pdf")
merger.close()