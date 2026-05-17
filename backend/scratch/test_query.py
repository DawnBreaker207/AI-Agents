import sys
import re
from ddgs import DDGS

sys.stdout.reconfigure(encoding='utf-8')

q = 'React'
sites = [
    "site:itviec.com",
    "site:topcv.vn",
    "site:vietnamworks.com",
    "site:jobsgo.vn",
    "site:careerviet.vn",
    "site:timviecnhanh.com"
]
site_filter = " OR ".join(sites)
query = f"{q} ({site_filter})"
print(f"Query: {query}")

try:
    with DDGS() as ddgs:
        results = list(ddgs.text(query, timelimit='m', max_results=65))
    
    kept = []
    excluded = []
    
    for r in results:
        url = r.get("href", "")
        title = r.get("title", "")
        
        is_job_url = False
        
        # 1. ITviec: specific job post has '/it-jobs/'
        if "itviec.com" in url and "/it-jobs/" in url:
            is_job_url = True
            
        # 2. TopCV: specific job detail has '/tuyen-dung/'
        elif "topcv.vn" in url and "/tuyen-dung/" in url:
            is_job_url = True
            
        # 3. VietnamWorks: job post has '/job/' or ends with '-jv'
        elif "vietnamworks.com" in url:
            if "/job/" in url or url.lower().endswith("-jv") or "/tuyen-dung/" in url:
                is_job_url = True
                
        # 4. JobsGo: job detail has '/viec-lam/' and ends with an ID + '.html' (e.g. -26934761240.html)
        elif "jobsgo.vn" in url:
            # Check if it has an ID pattern before .html, or has /tuyen-dung/
            if "/tuyen-dung/" in url:
                is_job_url = True
            elif "/viec-lam/" in url and url.endswith(".html"):
                # Check if it ends with digits + .html
                if re.search(r"-\d+\.html$", url):
                    is_job_url = True
                    
        # 5. CareerViet / CareerBuilder: job detail has '/vi/tim-viec-lam/' and ends in .html (not tat-ca-viec-lam or trang)
        elif "careerviet.vn" in url or "careerbuilder.vn" in url:
            if "/vi/tim-viec-lam/" in url and url.endswith(".html"):
                if not any(k in url.lower() for k in ["-trang-", "/trang-", "page", "/tat-ca-viec-lam"]):
                    is_job_url = True
                    
        # 6. TimViecNhanh: job detail has '/tuyen-dung/'
        elif "timviecnhanh.com" in url and "/tuyen-dung/" in url:
            is_job_url = True

        if is_job_url:
            kept.append((title, url))
        else:
            excluded.append((title, url))
            
    print(f"\n--- KEPT ({len(kept)} jobs) ---")
    for idx, (t, u) in enumerate(kept):
        print(f"[{idx+1}] Title: {t}\n    URL: {u}")
        
    print(f"\n--- EXCLUDED ({len(excluded)} pages) ---")
    for idx, (t, u) in enumerate(excluded[:10]):
        print(f"[{idx+1}] Title: {t}\n    URL: {u}")
        
except Exception as e:
    import traceback
    traceback.print_exc()
