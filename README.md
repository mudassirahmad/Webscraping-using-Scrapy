# Webscraping-using-Scrapy
Scraped content and downloaded attachments in custom folders from 2 different websites using Scrapy.

The basic structure is as follows:

**Navigate to Home page -> Subpage01->Fetch heading, Project description and download attachments & HTML page** to a specified path as shown below.

![scraping_format](https://github.com/mudassirahmad/Webscraping-using-Scrapy/assets/60046079/9f632a96-3d62-40a2-828c-3039d3d2e1be)

The directory structure for both the websites looks the same plus there were some .zip files on the websites which are also extracted and save in the same Attachments folder.

#### **Sthjj Website (Chinese website)**

This website has a different HTML format for each page so to identify the pattern I had to filter the required content with headings and styling of the tags.

Additionally, on this website, some of the attachments were inaccessible so to handle them I had to create an HTTP session and check if we are getting any response or not. 

If not within 5 seconds file is corrupted and append its link to a .txt file.
