# Knowladge Planet Scraper
A tool for scraping subscribed content from Knowledge Planet (知识星球) and converting it into a PDF e-book.  
Mainly referenced from [GitHub](https://github.com/wbsabc/zsxq-spider), [Gitee](https://gitee.com/xueshanlinghu/zsxq_to_pdf)  

## Features

- Supports downloading and embedding images into PDF
- Supports displaying hyperlinks in PDF
- Supports downloading content within specific time intervals
- Optimized PDF layout for better readability and professional typography style


## How to Use

- Download this repository
- Configure Python environment
- Install required packages
  ```
    # Install required Python packages
    pip install requests
    pip install BeautifulSoup4  # Don't use PyCharm's built-in installer
    pip install pdfkit
    
    # Install wkhtmltopdf for HTML to PDF conversion
    brew install --cask wkhtmltopdf  # No environment variable configuration needed
  ```
- Login to your Knowledge Planet account with valid subscription 登录你有权限查看的星球的账号
- Open the planet page and:
  - Open Browser Developer Tools (Inspect)
  - Go to Network tab
  - Refresh the page
  - Find requests containing 'topics?...'
- Open `crawl.py` and modify the following settings
  ```
  # Required configurations
  ZSXQ_ACCESS_TOKEN = ''    # Token from Cookie after login
  USER_AGENT = ''           # User-Agent used during login
  REQUEST_URL = ''          # Knowledge Planet URL
  PDF_FILE_NAME = 'xxx.pdf'        # Output PDF filename
  ONLY_DIGESTS = False      # True for digests only | False for all content
  ONLY_OWNER = False        # True for owner only | False for all content
  ```

- Run `python crawl.py`

## Note
This tool respects the terms of service of Knowledge Planet and should be used responsibly and legally. Please ensure you have proper access rights to the content you're downloading.
## Contributing
Feel free to submit issues, fork the repository and create pull requests for any improvements.
## License
This project is licensed under the MIT License - see the LICENSE file for details.
## Disclaimer
This tool is for personal use only. The user bears all responsibility for any consequences of using this tool. Please respect copyright and terms of service of Knowledge Planet.


