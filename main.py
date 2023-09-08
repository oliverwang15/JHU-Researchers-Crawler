
import requests
from lxml import etree
from tqdm import tqdm
import pandas as pd
import traceback

base_url = "https://www.cs.jhu.edu/faculty/"             # CS
# base_url = "https://engineering.jhu.edu/ams/faculty/"  # AMS

headers = {
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
}

response = requests.get(base_url, headers=headers)
response = etree.HTML(response.text)
entity_list = response.xpath("/html/body/div[2]/main/div/div[2]/div/div/div/ul/li")

all = pd.DataFrame()
for entity in tqdm(entity_list, desc="Scraping..."):
    try:
        # A dict to store all the details
        detail_dict = {}

        # Get the url and name from the first page
        url = entity.xpath('./div/div/div/div[1]/div/h2/a/@href')[0]
        name = entity.xpath('./div/div/div/div[1]/div/h2/a/text()')[0]
        detail_dict['name'] = name
        detail_dict['url'] = url

        # Get the details from the second page
        response = requests.get(url, headers=headers)
        response = etree.HTML(response.text)
        meta_details = response.xpath("/html/body/div[2]/main/div/div[1]/div/div/div/div/div/div")

        # Get the details
        for meta_detail in meta_details:
            meta_name = meta_detail.xpath("./div[1]/text()")[0]

            if meta_name == "Education":
                tel = meta_detail.xpath("./div[2]/a/text()")[0]
                detail_dict['tel'] = tel
                email = meta_detail.xpath("./div[3]/a/text()")[0]
                detail_dict['email'] = email

            elif meta_name == "Location":
                location = meta_detail.xpath("./div[2]/div[2]/text()")[0]
                detail_dict['location'] = location

            elif meta_name == "Research Areas":
                research_areas = meta_detail.xpath("./div")[1:]
                research_areas = [area.xpath("./text()")[0] for area in research_areas]
                research_areas = [area.strip() for area in research_areas]
                detail_dict['research_areas'] = ' | '.join(research_areas)

            elif meta_name == "Connect":
                connect_list = meta_detail.xpath("./ul/li")
                for connect in connect_list:
                    connect = connect.xpath("./a")[0]
                    url = connect.xpath("./@href")[0]
                    connect_name = connect.xpath("./span/span[1]/text()")[0]
                    detail_dict[connect_name] = url

        # Get the self introduction
        self_intro = response.xpath("/html/body/div[2]/main/div/div[2]/div/div/div//text()")
        detail_dict['self_intro'] = '\n'.join(self_intro)

        # concat the data
        tmp = pd.DataFrame(detail_dict, index=[0])
        all = pd.concat([all, tmp], ignore_index=True)
    
    except Exception as e:
        message = f"Something went wrong with {name} and the url is {url } \nError: {traceback.format_exc()}\n"
        print(message)

# Save the data
all.to_excel("cs.xlsx", index=False)
# all.to_excel("ams.xlsx", index=False)





