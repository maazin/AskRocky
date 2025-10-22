# BullBot-Dataset
The repository contains dataset of Bull Bot from 5000+ websites and links of the University of South Florida

### Checkout Bull Bot in action at **[BullBot.tech](https://www.bullbot.tech)**

## About the main files in the repository: main.ipynb and data_webScrap.ipynb
1. The program in [scrapLink.ipynb](scrapLink.ipynb) file scrapes the links from the websites stored them in the form of a pickle file [urls.pkl](urls.pkl).
2. After that, the program in [scrapData_FromLink.ipynb](scrapData_FromLink.ipynb) file scrapes the page contents from the links stored in the pickle file and stores them in the form of a json file [data.json](dataset.json).
3. The BB_filter is a class for data processing pipeline to filter out the data that relevant and remove unnecessary data.

## About the dataset
The dataset is a json file [data.json](dataset.json). In another words, it is a list of python dictionary with the following structure:
```python
[{
  "page_content": {
    "page_content of the pages.....",
    "metadata": {
      "source": "url of the page",
      "title": "title of the page"
        }
    },
  {
    "page_content": {
        "About USF. See .... "
        }
    "metadata": {
        "source": "https://www.usf.edu/about-usf/index.aspx",
        "title": "About USF | University of South Florida"
        }
    },  
  ...
}
]
```