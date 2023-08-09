import scrapy
import os
import json
import requests

class SthjjSpiders(scrapy.Spider):
    name="sthjj"
    start_urls=[
        "http://sthjj.pds.gov.cn/channels/11330.html"
    ]
    count, project_count=1,0
    session = requests.Session()
    inaccessible_docs=[]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse)

    
    def parse(self, response):
        links=response.css('div.xxgk td a::attr(href)').getall()
        
        #naviagte to each subpage from mainpage
        for link in links:
            yield response.follow(link, self.page_parse)
                    
        
        next_page= response.css('span.item.operation > a::attr(href)')[2].get()
        self.project_count+=1
        
        #navigate to the next main page
        if next_page and self.project_count<3:
            yield response.follow(next_page, callback=self.parse)
        

        
    def page_parse(self, response):
        title=response.css('h1 ::text').get(default='').strip()
        
        date=response.css('div.page-date ::text').get(default='').strip()
        
        #complex structure logic for description
        parent_tag = response.css('div.article')
        next_sibling_tag = parent_tag.css(':first-child')
        desc=""
        if next_sibling_tag.css('h1'):
            # The first child tag is <h1>
            data=(response.css('div.article h1 ::text').extract())
        elif next_sibling_tag.css('p'):
            data=[]
            counter=0
            flag=0
            text_query= response.css('div.article p')
            for tag in text_query:
                if counter==0:
                    counter+=1
                    flag+=1
                    continue
                
                if counter!=flag:
                    break
                
                if 'text-align:center' in tag.attrib['style']:
                    data.append("".join(tag.css('*::text').getall()))
                    counter+=1
                if 'text-align: center' in tag.attrib['style'] :
                    data.append("".join(tag.css('*::text').getall())) 
                    counter+=1
                flag+=1
            else:
                data="None"
                
        desc="".join(data)
                 
        
        meta={
            'Title:':title,
            'Date:':date,
            "Description:": desc
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
        with open(meta_file_path, 'w',encoding='utf-8') as meta_file:
            json.dump(meta, meta_file,ensure_ascii=False)

        
        attachments=response.css('a[href*=".doc"]::attr(href)').getall()
        
        #downloads the attachments in each subpage
        for link in attachments:
            #checks if the link is accessible or not.
            if not self.check_url(link):
                print("Caught error")
                continue
            yield response.follow(link, callback=self.download_attachments, meta={'attachments_folder': attachments_folder})
           
            
        
    def download_html(self, response,output_folder):
        filename='HTML_file.html'
        html_path= os.path.join(output_folder, filename)
        
        with open(html_path, 'wb') as f:
            f.write(response.body)
            
          
            
    def download_attachments(self, response):
        
        filename=response.url.split('/')[-1]
        attachment_folder=response.meta['attachments_folder']
        attachments_file=os.path.join(attachment_folder,filename)
    
        
        with open(attachments_file, 'wb') as f:
                f.write(response.body)
    
    def check_url(self,url):
        try:
            response = self.session.get(url, timeout=5)
            return True
        except requests.exceptions.RequestException as e:
            self.inaccessible_docs.append(url)
            return False
    
    def save_inaccessible_files(self):
        with open('inaccessible_links.txt', 'w') as file:
            file.write('\n'.join(self.inaccessible_docs))
    
    #automatically called after all the scrapping is done.
    def closed(self, reason):
        self.save_inaccessible_files()