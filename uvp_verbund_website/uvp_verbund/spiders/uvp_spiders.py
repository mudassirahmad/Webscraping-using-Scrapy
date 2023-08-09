import scrapy
import os
import json
import zipfile
from io import BytesIO

class UvpSpiders(scrapy.Spider):
    name="uvp_verbound"
    start_urls=[
        "https://www.uvp-verbund.de/freitextsuche?rstart=0&currentSelectorPage=1"
    ]
    #count is for subpage counting
    #project_count is for limiting the projects to be scrapped
    count, project_count=1,0
    
    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)
            
    
    def parse(self, response):
        
        links=response.css("div.teaser-data.search a::attr(href)").getall()
        links=list(set(links))
        #navigating to the subpages from the main page
        for link in links:
            yield response.follow(link, self.page_parse)
            
        next_page= response.css('a.icon.small-button::attr(href)')[6].get()
        self.project_count+=1
        if next_page and self.project_count<3:
            yield response.follow(next_page, callback=self.parse)
        
    #scraping the data from the subpage
    def page_parse(self, response):
        
        title=response.css('h1 ::text').get(default='').strip()
        date=response.css("div.helper.text.date span ::text").get(default='').strip()
        desc=response.css("p ::text").get(default='').strip()
        
        
        meta={
            "Title":title,
            "Date:":date,
            "Project Description":desc
        }
        
        #setting directories
        page_dir=f'assignment\\Subpage{self.count}'
        self.count+=1
        
        meta_folder= os.path.join(page_dir,'Meta')
        attachments_folder=os.path.join(page_dir,'Attachments')
        
        
        os.makedirs(meta_folder, exist_ok=True)
        os.makedirs(attachments_folder, exist_ok=True)
        
        #download HTML page
        self.download_html(response,page_dir)
        
        
        # Save metadata as JSON
        meta_file_path = os.path.join(meta_folder, 'metadata.json')
        with open(meta_file_path, 'w') as meta_file:
            json.dump(meta, meta_file)

        attachments= response.css("a.link.download::attr(href)").getall()
        
        
        for link in attachments:
            yield response.follow(link, callback=self.download_attachments, meta={'attachments_folder': attachments_folder})
            
            
    def download_html(self, response,output_folder):
        
        #name=name.partition('-')[0]
        #filename= f'{name}.html'
        filename='HTML_file.html'
        html_path= os.path.join(output_folder, filename)
        
        with open(html_path, 'wb') as f:
            f.write(response.body)
            
            
    def download_attachments(self, response):
        
        filename=response.url.split('/')[-1]
        attachment_folder=response.meta['attachments_folder']
        attachments_file=os.path.join(attachment_folder,filename)
        
        #some attachments are URLs and I took the freedom to skip them by this check otherwise I can convert them into PDF save them as well.
        if '.' not in filename:
            return
        else:
            if filename.endswith('.zip'):
                self.extract_zip(response.body,  attachment_folder)
            else:
                with open(attachments_file, 'wb') as f:
                    f.write(response.body)
         
    #some attachments are in zip format this method will extract files from those folders as well.       
    def extract_zip(self, zip_data,  output_folder):
        with zipfile.ZipFile(BytesIO(zip_data), 'r') as zip_ref:
            zip_ref.extractall(output_folder)