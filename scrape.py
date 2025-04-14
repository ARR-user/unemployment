import asyncio
import csv
from datetime import datetime
from time import perf_counter
# import playwright
from playwright.async_api import async_playwright
import itertools



# SEARCH_TERMS = ["software engineer", "data analyst","data engineer"]
# LOCATIONS = ["sydney", "perth"]

SEARCH_TERMS = ["software engineer"]
LOCATIONS = ["brisbane"]

BASE_URL = "https://www.seek.com.au"
""" 
@dev a webscraper for getting research data from 
     Seek website
         
         
         
         """
async def scrape_seek_jobs():
    start_time = perf_counter()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)# put false for cloudflare
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)...")#anti-bot tag, still we might get flagged
        page = await context.new_page()

        all_jobs = []
      
        for term, location in itertools.product(SEARCH_TERMS,LOCATIONS):
            print(f": Scraping for: {term} in {location}")
            
     
            page_num=1
            while True:

                url = f"{BASE_URL}/{term.replace(' ', '-')}-jobs/in-all-{location}?page={page_num}" #hotfix
                await page.goto(url)

                await page.wait_for_timeout(3000)  # wait for JS to load

                job_cards = await page.query_selector_all("article[data-automation='normalJob']")
                
                if (len(job_cards)!=0):
                    print(f"  Page {page_num}: {len(job_cards)} jobs found")
                else:
                    break
                page_num +=1   

                """## FETCH ALL DETAILS CONCURRENTLY 
                """ 
                #  Concurrent description fetching using asyncio.gather
                job_tasks = []
                for card in job_cards:
                    title = await card.query_selector("h3")
                    company = await card.query_selector("span[data-automation='jobCompany']")
                    location_elem = await card.query_selector("span[data-automation='jobCardLocation']")
                    salary= await card.query_selector("span[data-automation=jobSalary]")
                    date = await card.query_selector("span[data-automation='jobListingDate']")
                    link = await card.query_selector("a")

                    job_url = BASE_URL + await link.get_attribute("href") if link else None
                    # location_text = await location_elem.inner_text() if location_elem else None

                    job_info = {
                        "search_term": term,
                        "title": await title.inner_text() if title else None,
                        "company": await company.inner_text() if company else None,
                        "location": await location_elem.inner_text() if location_elem else None,
                        "salary": await salary.inner_text()if salary else None,
                        "date_posted": await date.inner_text() if date else None,
                        "url": job_url
                    }

                    job_tasks.append((job_info, job_url))

               

                async def fetch_desc(job_url):
                    job_page = await browser.new_page()
                    desc_text = None
                    try:
                        await job_page.goto(job_url)
                        await job_page.wait_for_timeout(20000)
                        desc_elem = await job_page.query_selector("div[data-automation='jobAdDetails']")
                        desc_text = await desc_elem.inner_text() if desc_elem else "N/A"
                    except exception as e:
                        print(f"Failed to fetch description from {job_url}: {e}")
                        desc_text = "Failed to fetch"
                    await job_page.close()
                    return desc_text

              
                desc_results = await asyncio.gather(*[fetch_desc(url) for _, url in job_tasks])

       

                for (job_info, _), desc in zip(job_tasks, desc_results):
                    job_info["description"] = desc
                    all_jobs.append(job_info)

                    
                # update only the last record with the scraped date
                # if all_jobs:  
                #     all_jobs[-1]["scraped_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                 
        await browser.close()

        # Save to CSV with datestamp
        now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename= f"seek_jobs_{now}.csv"

      
        keys = all_jobs[0].keys() if all_jobs else []
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(all_jobs)

        end_time = perf_counter()
        elapsed = end_time - start_time    

        print(f"\n Saved {len(all_jobs)} jobs to seek_jobs.csv \n Total time: {elapsed:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(scrape_seek_jobs())







##++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
##+++++++++++++++++++++++++++++   CODE CEMETERY  ++++++++++++++++++++++++++++++++++++++
##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++##


# import asyncio
# import csv
# from datetime import datetime
# from time import perf_counter
# # import playwright
# from playwright.async_api import async_playwright
# import itertools



# # SEARCH_TERMS = ["software engineer", "data analyst","data engineer"]
# # LOCATIONS = ["sydney", "perth"]

# SEARCH_TERMS = ["data analyst","software engineer","developer"]
# LOCATIONS = ["brisbane","sydney","perth"]

# BASE_URL = "https://www.seek.com.au"
# """ 
# @dev a webscraper for getting research data from 
#      Seek website
         
         
         
#          """
# async def scrape_seek_jobs():
#     start_time = perf_counter()
#     async with async_playwright() as p:
#         browser = await p.chromium.launch(headless=False)# put false for cloudflare
#         context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)...")#anti-bot tag, still we might get flagged
#         page = await context.new_page()

#         all_jobs = []
#         ##Debug_Test
#         # for term in SEARCH_TERMS:
#         #     print(f"Scraping for: {term}")
#         #     for page_num in range(1, 6):  
#         #         url = f"{BASE_URL}/{term.replace(' ', '-')}-jobs?page={page_num}"




#         for term, location in itertools.product(SEARCH_TERMS,LOCATIONS):
#             print(f": Scraping for: {term} in {location}")
            
#             #Debug_sampling
#       # for _, term in enumerate((SEARCH_TERMS), start=1):    ###/// refactor 
#         #     for _,location in enumerate (LOCATIONS):
#         #         print(f" Scraping for: {term} in {location}")

#             # print(f"Index {idx}: term = {term}, location = {LOCATIONS}")
#             # for page_num in range(1, 6):
#             #      #ElementHandle to string
#             #     # term_text = await term.text_content()  # Extract the string right away
#             #     # location_text = await location.text_content()
#             page_num=1
#             while True:

#                 url = f"{BASE_URL}/{term.replace(' ', '-')}-jobs/in-all-{location}?page={page_num}" #hotfix
#                 await page.goto(url)
                
#                 # #Debug
#                 # print(await page.content())  

#                 await page.wait_for_timeout(3000)  # wait for JS to load

#                 job_cards = await page.query_selector_all("article[data-automation='normalJob']")
                
#                 if (len(job_cards)!=0):
#                     print(f"  Page {page_num}: {len(job_cards)} jobs found")
#                 else:
#                     break
#                 page_num +=1   

#                 #check seek JS before playing with html cards
#                 """ ## FETCH JUST CARD DETAILS
#                 """
#                 # for card in job_cards:
#                 #     title = await card.query_selector("h3")
#                 #     company = await card.query_selector("span[data-automation='jobCompany']")
#                 #     location = await card.query_selector("span[data-automation='jobLocation']")
#                 #     date = await card.query_selector("span[data-automation='jobListingDate']")
#                 #     link = await card.query_selector("a")

#                 #     job = {
#                 #         "search_term": term,
#                 #         "title": await title.inner_text() if title else None,
#                 #         "company": await company.inner_text() if company else None,
#                 #         "location": await location.inner_text() if location else None,
#                 #         "date_posted": await date.inner_text() if date else None,
#                 #         "url": BASE_URL + await link.get_attribute("href") if link else None
#                 #     }
#                 """ ## FETCH CARD  AND DESCRIPTION from url IN IT 
#                 """
#                 # for card in job_cards:
#                 #     # extract basic info
#                 #     title = await card.query_selector("h3")
#                 #     company = await card.query_selector("span[data-automation='jobCompany']")
#                 #     location = await card.query_selector("span[data-automation='jobLocation']")
#                 #     date = await card.query_selector("span[data-automation='jobListingDate']")
#                 #     link = await card.query_selector("a")

#                 #     url = BASE_URL + await link.get_attribute("href") if link else None

#                 #     # go to job detail page and extract description
#                 #     desc_text = None
#                 #     if url:
#                 #         job_page = await browser.new_page()
#                 #         await job_page.goto(url)
#                 #         await job_page.wait_for_timeout(2000)  # OR wait_for_selector()
#                 #         desc_elem = await job_page.query_selector("div[data-automation='jobAdDetails']")
#                 #         desc_text = await desc_elem.inner_text() if desc_elem else "N/A"
#                 #         await job_page.close()

#                 #     job = {
#                 #         "search_term": term,
#                 #         "title": await title.inner_text() if title else None,
#                 #         "company": await company.inner_text() if company else None,
#                 #         "location": await location.inner_text() if location else None,
#                 #         "date_posted": await date.inner_text() if date else None,
#                 #         "url": url,
#                 #         "description": desc_text
#                 #     }

#                     # all_jobs.append(job)
#                 """## FETCH ALL DETAILS CONCURRENTLY 
#                 """ 
#                 #  Concurrent description fetching using asyncio.gather
#                 job_tasks = []
#                 for card in job_cards:
#                     title = await card.query_selector("h3")
#                     company = await card.query_selector("span[data-automation='jobCompany']")
#                     location_elem = await card.query_selector("span[data-automation='jobLocation']")
#                     date = await card.query_selector("span[data-automation='jobListingDate']")
#                     link = await card.query_selector("a")

#                     job_url = BASE_URL + await link.get_attribute("href") if link else None
#                     location_text = await location_elem.inner_text() if location_elem else None

#                     job_info = {
#                         "search_term": term,
#                         "title": await title.inner_text() if title else None,
#                         "company": await company.inner_text() if company else None,
#                         "location": location_text,
#                         "date_posted": await date.inner_text() if date else None,
#                         "url": job_url
#                     }

#                     job_tasks.append((job_info, job_url))

               

#                 async def fetch_desc(job_url):
#                     job_page = await browser.new_page()
#                     desc_text = None
#                     try:
#                         await job_page.goto(job_url)
#                         await job_page.wait_for_timeout(20000)
#                         desc_elem = await job_page.query_selector("div[data-automation='jobAdDetails']")
#                         desc_text = await desc_elem.inner_text() if desc_elem else "N/A"
#                     except exception as e:
#                         print(f"Failed to fetch description from {job_url}: {e}")
#                         desc_text = "Failed to fetch"
#                     await job_page.close()
#                     return desc_text

              
#                 desc_results = await asyncio.gather(*[fetch_desc(url) for _, url in job_tasks])

       

#                 for (job_info, _), desc in zip(job_tasks, desc_results):
#                     job_info["description"] = desc
#                     all_jobs.append(job_info)

                    
#                 # Once the loop is finished, update only the last record with the scraped date
#                 if all_jobs:  # Check to ensure the list isn't empty
#                     all_jobs[-1]["scraped_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                
#         await browser.close()

#         # Save to CSV with datestamp
#         now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#         filename= f"seek_jobs_{now}.csv"

      
#         keys = all_jobs[0].keys() if all_jobs else []
#         with open(filename, "w", newline="", encoding="utf-8") as f:
#             writer = csv.DictWriter(f, fieldnames=keys)
#             writer.writeheader()
#             writer.writerows(all_jobs)

#         end_time = perf_counter()
#         elapsed = end_time - start_time    

#         print(f"\n Saved {len(all_jobs)} jobs to seek_jobs.csv \n Total time: {elapsed:.2f} seconds")

# if __name__ == "__main__":
#     asyncio.run(scrape_seek_jobs())




